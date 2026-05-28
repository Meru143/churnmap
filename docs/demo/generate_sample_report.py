"""Generate the curated churnmap sample report used by README assets."""

from __future__ import annotations

from pathlib import Path

from coupling_core import CouplingPair, RepoAnalysis

from churnmap.config import ChurnmapConfig
from churnmap.data_preparer import DataPreparer
from churnmap.html_renderer import HtmlRenderer
from churnmap.json_writer import JsonWriter


def main() -> None:
    output_dir = Path(__file__).parent
    pairs = [
        CouplingPair("src/checkout.py", "src/invoice.py", 0.91, 38, 42, "high"),
        CouplingPair("src/payment.py", "src/refunds.py", 0.84, 29, 35, "high"),
        CouplingPair("src/checkout.py", "src/cart.py", 0.76, 25, 33, "high"),
        CouplingPair("src/invoice.py", "src/tax.py", 0.68, 19, 28, "medium"),
        CouplingPair("src/cart.py", "src/promotions.py", 0.63, 17, 27, "medium"),
        CouplingPair("src/payment.py", "src/gateway.py", 0.57, 14, 25, "medium"),
        CouplingPair("src/reporting.py", "src/export.py", 0.46, 10, 22, "medium"),
        CouplingPair("src/auth.py", "src/session.py", 0.41, 9, 22, "medium"),
        CouplingPair("src/notifications.py", "src/templates.py", 0.33, 7, 21, "medium"),
        CouplingPair("src/search.py", "src/indexer.py", 0.29, 6, 21, "low"),
        CouplingPair("src/api.py", "src/openapi.py", 0.24, 5, 21, "low"),
        CouplingPair("src/admin.py", "src/audit.py", 0.18, 4, 22, "low"),
    ]
    analysis = RepoAnalysis(
        pairs=pairs,
        total_commits_analyzed=168,
        lookback_days=90,
        repo_name="example/payments-service",
    )
    config = ChurnmapConfig(
        output_dir=output_dir,
        min_occurrences=3,
        heatmap_limit=12,
        top_files=12,
        low_threshold=0.3,
        high_threshold=0.7,
    )
    report = DataPreparer(config).prepare(analysis)
    (output_dir / "sample-report.html").write_text(HtmlRenderer().render(report), encoding="utf-8")
    (output_dir / "sample-report.json").write_text(JsonWriter().write(report), encoding="utf-8")


if __name__ == "__main__":
    main()
