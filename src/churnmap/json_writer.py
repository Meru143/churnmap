"""Machine-readable report JSON serialization."""

from __future__ import annotations

import json
from typing import Any

from churnmap.data_preparer import ReportData


class JsonWriter:
    """Serialize ``ReportData`` to the PRD JSON envelope."""

    def build_json_dict(self, report_data: ReportData) -> dict[str, Any]:
        meta = {
            "repo": report_data.repo_name,
            "generated_at": report_data.generated_at,
            "lookback_days": report_data.lookback_days,
            "total_commits_analyzed": report_data.total_commits_analyzed,
            "churnmap_version": report_data.churnmap_version,
        }
        pairs = [
            {
                "file_a": pair.file_a.replace("\\", "/"),
                "file_b": pair.file_b.replace("\\", "/"),
                "score": pair.score,
                "co_changes": pair.co_changes,
                "total_commits": pair.total_commits,
                "risk": pair.risk,
            }
            for pair in sorted(report_data.all_pairs, key=lambda item: item.score, reverse=True)
        ]
        return {"meta": meta, "pairs": pairs}

    def write(self, report_data: ReportData) -> str:
        return json.dumps(self.build_json_dict(report_data), indent=2)
