"""Pure transformations from coupling-core analysis into report data."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import TYPE_CHECKING

from churnmap import __version__
from churnmap.config import ChurnmapConfig

if TYPE_CHECKING:
    from coupling_core import CouplingPair, RepoAnalysis


@dataclass(frozen=True)
class HeatmapData:
    files: list[str]
    matrix: list[list[float]]
    file_commit_counts: dict[str, int]


@dataclass(frozen=True)
class ForceGraphData:
    nodes: list[dict[str, object]]
    links: list[dict[str, object]]


@dataclass(frozen=True)
class ReportData:
    heatmap: HeatmapData
    force_graph: ForceGraphData
    table_pairs: list[CouplingPair]
    all_pairs: list[CouplingPair]
    repo_name: str
    generated_at: str
    total_commits_analyzed: int
    lookback_days: int
    churnmap_version: str


def top_files_for_heatmap(pairs: list[CouplingPair], heatmap_limit: int) -> list[str]:
    """Return top files ordered by their maximum coupling score."""

    max_score_per_file: dict[str, float] = {}
    for pair in pairs:
        file_a = _normalize_path(pair.file_a)
        file_b = _normalize_path(pair.file_b)
        max_score_per_file[file_a] = max(max_score_per_file.get(file_a, 0.0), pair.score)
        max_score_per_file[file_b] = max(max_score_per_file.get(file_b, 0.0), pair.score)

    sorted_files = sorted(
        max_score_per_file,
        key=lambda file_path: (-max_score_per_file[file_path], file_path),
    )
    return sorted_files[: min(heatmap_limit, len(sorted_files))]


def build_heatmap_matrix(files: list[str], pairs: list[CouplingPair]) -> list[list[float]]:
    """Build a symmetric NxN coupling score matrix for selected files."""

    pair_lookup: dict[tuple[str, str], float] = {}
    for pair in pairs:
        file_a = _normalize_path(pair.file_a)
        file_b = _normalize_path(pair.file_b)
        pair_lookup[(file_a, file_b)] = pair.score
        pair_lookup[(file_b, file_a)] = pair.score

    return [
        [pair_lookup.get((file_a, file_b), 0.0) for file_b in files]
        for file_a in files
    ]


def build_force_graph_data(
    pairs: list[CouplingPair],
    file_commit_counts: dict[str, int],
    config: ChurnmapConfig,
) -> ForceGraphData:
    """Build D3-ready nodes and links for the force graph."""

    max_score_per_file: dict[str, float] = {}
    for pair in pairs:
        file_a = _normalize_path(pair.file_a)
        file_b = _normalize_path(pair.file_b)
        max_score_per_file[file_a] = max(max_score_per_file.get(file_a, 0.0), pair.score)
        max_score_per_file[file_b] = max(max_score_per_file.get(file_b, 0.0), pair.score)

    nodes = [
        {
            "id": file_path,
            "churn": file_commit_counts.get(file_path, 1),
            "max_score": max_score,
            "risk": classify_risk(max_score, config),
        }
        for file_path, max_score in sorted(max_score_per_file.items())
    ]
    links = [
        {
            "source": _normalize_path(pair.file_a),
            "target": _normalize_path(pair.file_b),
            "score": pair.score,
            "co_changes": pair.co_changes,
            "risk": pair.risk,
        }
        for pair in pairs
    ]
    return ForceGraphData(nodes=nodes, links=links)


def classify_risk(score: float, config: ChurnmapConfig) -> str:
    if score < config.low_threshold:
        return "low"
    if score < config.high_threshold:
        return "medium"
    return "high"


class DataPreparer:
    """Prepare report data from a coupling-core ``RepoAnalysis``."""

    def __init__(self, config: ChurnmapConfig) -> None:
        self.config = config

    def prepare(self, analysis: RepoAnalysis) -> ReportData:
        file_commit_counts = _derive_file_commit_counts(analysis.pairs)
        top_files = top_files_for_heatmap(analysis.pairs, self.config.heatmap_limit)
        matrix = build_heatmap_matrix(top_files, analysis.pairs)
        heatmap = HeatmapData(
            files=top_files,
            matrix=matrix,
            file_commit_counts=file_commit_counts,
        )
        force_graph = build_force_graph_data(analysis.pairs, file_commit_counts, self.config)
        return ReportData(
            heatmap=heatmap,
            force_graph=force_graph,
            table_pairs=analysis.pairs[: self.config.top_files],
            all_pairs=list(analysis.pairs),
            repo_name=analysis.repo_name,
            generated_at=date.today().isoformat(),
            total_commits_analyzed=analysis.total_commits_analyzed,
            lookback_days=analysis.lookback_days,
            churnmap_version=__version__,
        )


def _derive_file_commit_counts(pairs: list[CouplingPair]) -> dict[str, int]:
    """Best-effort churn counts from public RepoAnalysis pair data."""

    counts: dict[str, int] = {}
    for pair in pairs:
        file_a = _normalize_path(pair.file_a)
        file_b = _normalize_path(pair.file_b)
        counts[file_a] = max(counts.get(file_a, 0), pair.total_commits)
        counts[file_b] = max(counts.get(file_b, 0), pair.total_commits)
    return counts


def _normalize_path(path: str) -> str:
    return path.replace("\\", "/")
