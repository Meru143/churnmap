"""DataPreparer tests."""

from __future__ import annotations

from coupling_core import CouplingPair, RepoAnalysis

from churnmap.config import ChurnmapConfig
from churnmap.data_preparer import (
    DataPreparer,
    build_force_graph_data,
    build_heatmap_matrix,
    classify_risk,
    top_files_for_heatmap,
)


def test_top_files_for_heatmap_returns_top_n_sorted_by_max_score(
    sample_pairs: list[CouplingPair],
) -> None:
    assert top_files_for_heatmap(sample_pairs, 3) == [
        "src/billing.py",
        "src/payment.py",
        "src/cart.py",
    ]


def test_top_files_for_heatmap_clamps_to_unique_file_count(
    sample_pairs: list[CouplingPair],
) -> None:
    files = top_files_for_heatmap(sample_pairs[:1], 50)

    assert files == ["src/billing.py", "src/payment.py"]


def test_build_heatmap_matrix_sets_pair_score(sample_pairs: list[CouplingPair]) -> None:
    files = ["src/payment.py", "src/billing.py", "src/cart.py"]

    matrix = build_heatmap_matrix(files, sample_pairs)

    assert matrix[0][1] == 0.82
    assert matrix[1][0] == 0.82
    assert matrix[0][2] == 0.64


def test_build_heatmap_matrix_uses_zero_when_pair_missing(
    sample_pairs: list[CouplingPair],
) -> None:
    files = ["src/cart.py", "src/tax.py"]

    matrix = build_heatmap_matrix(files, sample_pairs)

    assert matrix[0][1] == 0.0


def test_build_force_graph_data_node_has_churn_max_score_and_risk(
    sample_pairs: list[CouplingPair],
    sample_config: ChurnmapConfig,
) -> None:
    data = build_force_graph_data(sample_pairs, {"src/payment.py": 50}, sample_config)

    payment = next(node for node in data.nodes if node["id"] == "src/payment.py")

    assert payment == {
        "id": "src/payment.py",
        "churn": 50,
        "max_score": 0.82,
        "risk": "high",
    }


def test_build_force_graph_data_link_has_source_target_score_and_risk(
    sample_pairs: list[CouplingPair],
    sample_config: ChurnmapConfig,
) -> None:
    data = build_force_graph_data(sample_pairs[:1], {}, sample_config)

    assert data.links[0] == {
        "source": "src/payment.py",
        "target": "src/billing.py",
        "score": 0.82,
        "co_changes": 41,
        "risk": "high",
    }


def test_windows_backslashes_are_converted_in_force_graph_node_ids() -> None:
    pairs = [CouplingPair("src\\payment.py", "src\\billing.py", 0.82, 4, 5, "high")]

    data = build_force_graph_data(pairs, {"src/payment.py": 5}, ChurnmapConfig())

    assert {node["id"] for node in data.nodes} == {"src/payment.py", "src/billing.py"}
    assert data.links[0]["source"] == "src/payment.py"


def test_prepare_truncates_table_pairs_to_top_files_count(
    sample_pairs: list[CouplingPair],
) -> None:
    analysis = RepoAnalysis(sample_pairs, 50, 90, "repo")

    report = DataPreparer(ChurnmapConfig(top_files=2)).prepare(analysis)

    assert report.table_pairs == sample_pairs[:2]
    assert report.all_pairs == sample_pairs


def test_classify_risk_respects_config_thresholds() -> None:
    config = ChurnmapConfig(low_threshold=0.25, high_threshold=0.65)

    assert classify_risk(0.24, config) == "low"
    assert classify_risk(0.25, config) == "medium"
    assert classify_risk(0.65, config) == "high"
