"""End-to-end tests against a real git repository."""

from __future__ import annotations

import json
from pathlib import Path

from typer.testing import CliRunner

from churnmap.main import app
from tests.conftest import FakeRepo

runner = CliRunner()


def test_full_workflow_detects_high_payment_billing_coupling(
    fake_repo: FakeRepo,
    tmp_path: Path,
) -> None:
    for index in range(8):
        fake_repo.commit(["src/payment.py", "src/billing.py"], message=f"payment billing {index}")
    for index in range(2):
        fake_repo.commit(["src/payment.py"], message=f"payment only {index}")
    output_dir = tmp_path / "report"

    result = runner.invoke(
        app,
        [
            "--repo",
            str(fake_repo.path),
            "--output-dir",
            str(output_dir),
            "--min-occurrences",
            "3",
        ],
    )

    assert result.exit_code == 0, result.output
    assert (output_dir / "index.html").exists()
    assert (output_dir / "report.json").exists()
    data = json.loads((output_dir / "report.json").read_text(encoding="utf-8"))
    pair = next(
        item
        for item in data["pairs"]
        if {item["file_a"], item["file_b"]} == {"src/payment.py", "src/billing.py"}
    )
    assert pair["score"] >= 0.7


def test_full_workflow_with_no_co_changes_exits_zero_without_outputs(
    fake_repo: FakeRepo,
    tmp_path: Path,
) -> None:
    fake_repo.commit(["src/payment.py"], message="payment only")
    fake_repo.commit(["src/billing.py"], message="billing only")
    output_dir = tmp_path / "report"

    result = runner.invoke(
        app,
        [
            "--repo",
            str(fake_repo.path),
            "--output-dir",
            str(output_dir),
            "--min-occurrences",
            "3",
        ],
    )

    assert result.exit_code == 0, result.output
    assert "No coupling pairs found." in result.output
    assert not output_dir.exists()
