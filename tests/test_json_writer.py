"""JsonWriter tests."""

from __future__ import annotations

import json
from datetime import date
from typing import Any

from coupling_core import RepoAnalysis

from churnmap import __version__
from churnmap.config import ChurnmapConfig
from churnmap.data_preparer import DataPreparer
from churnmap.json_writer import JsonWriter


def test_json_output_contains_meta_repo(sample_analysis: RepoAnalysis) -> None:
    data = _json_dict(sample_analysis)

    assert data["meta"]["repo"] == "Meru143/churnmap"


def test_json_output_contains_today_generated_at(sample_analysis: RepoAnalysis) -> None:
    data = _json_dict(sample_analysis)

    assert data["meta"]["generated_at"] == date.today().isoformat()


def test_json_output_contains_churnmap_version(sample_analysis: RepoAnalysis) -> None:
    data = _json_dict(sample_analysis)

    assert data["meta"]["churnmap_version"] == __version__


def test_json_pairs_sorted_by_score_desc(sample_analysis: RepoAnalysis) -> None:
    data = _json_dict(sample_analysis)
    scores = [pair["score"] for pair in data["pairs"]]

    assert scores == sorted(scores, reverse=True)


def test_json_pair_has_required_keys(sample_analysis: RepoAnalysis) -> None:
    data = _json_dict(sample_analysis)

    assert set(data["pairs"][0]) == {
        "file_a",
        "file_b",
        "score",
        "co_changes",
        "total_commits",
        "risk",
    }


def test_json_write_returns_valid_json(sample_analysis: RepoAnalysis) -> None:
    report = DataPreparer(ChurnmapConfig()).prepare(sample_analysis)

    parsed = json.loads(JsonWriter().write(report))

    assert parsed["meta"]["repo"] == "Meru143/churnmap"


def test_json_pairs_count_uses_all_pairs_not_truncated(sample_analysis: RepoAnalysis) -> None:
    report = DataPreparer(ChurnmapConfig(top_files=1)).prepare(sample_analysis)

    data = JsonWriter().build_json_dict(report)

    assert len(data["pairs"]) == len(sample_analysis.pairs)


def _json_dict(analysis: RepoAnalysis) -> dict[str, Any]:
    report = DataPreparer(ChurnmapConfig()).prepare(analysis)
    return JsonWriter().build_json_dict(report)
