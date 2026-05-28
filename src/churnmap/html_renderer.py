"""Jinja2-based HTML report rendering."""

from __future__ import annotations

import json
from typing import Any

import jinja2

from churnmap.data_preparer import ReportData


def get_jinja_env() -> jinja2.Environment:
    """Create a package-backed Jinja2 environment."""

    return jinja2.Environment(
        loader=jinja2.PackageLoader("churnmap", "templates"),
        autoescape=False,
    )


class HtmlRenderer:
    """Render the interactive static HTML report."""

    def __init__(self) -> None:
        self.env = get_jinja_env()

    def render(self, report_data: ReportData) -> str:
        try:
            template = self.env.get_template("report.html.j2")
        except jinja2.TemplateNotFound as exc:
            raise RuntimeError(
                "Internal error: report template not found - please reinstall churnmap"
            ) from exc

        context = self._build_context(report_data)
        return str(template.render(**context))

    def _build_context(self, report_data: ReportData) -> dict[str, Any]:
        table_pairs = [
            {
                "file_a": pair.file_a.replace("\\", "/"),
                "file_b": pair.file_b.replace("\\", "/"),
                "score": pair.score,
                "co_changes": pair.co_changes,
                "total_commits": pair.total_commits,
                "risk": pair.risk,
            }
            for pair in report_data.table_pairs
        ]
        max_score = max((pair.score for pair in report_data.all_pairs), default=0.0)
        return {
            "repo_name": report_data.repo_name,
            "generated_at": report_data.generated_at,
            "total_commits_analyzed": report_data.total_commits_analyzed,
            "lookback_days": report_data.lookback_days,
            "churnmap_version": report_data.churnmap_version,
            "total_pairs": len(report_data.all_pairs),
            "max_score": max_score,
            "total_files": len(report_data.force_graph.nodes),
            "heatmap_files_json": json.dumps(report_data.heatmap.files),
            "heatmap_matrix_json": json.dumps(report_data.heatmap.matrix),
            "force_nodes_json": json.dumps(report_data.force_graph.nodes),
            "force_links_json": json.dumps(report_data.force_graph.links),
            "table_pairs_json": json.dumps(table_pairs),
            "table_pairs": table_pairs,
        }
