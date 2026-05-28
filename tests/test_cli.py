"""CLI integration tests."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from typer.testing import CliRunner

from churnmap.main import app
from tests.conftest import FakeRepo

runner = CliRunner()


def test_cli_writes_html_and_json_to_default_output_dir(
    fake_repo: FakeRepo,
    tmp_path: Path,
    monkeypatch: Any,
) -> None:
    _make_coupled_history(fake_repo, 4)
    monkeypatch.chdir(tmp_path)

    result = runner.invoke(app, ["--repo", str(fake_repo.path)])
    output_dir = tmp_path / "coupling-report"

    assert result.exit_code == 0, result.output
    assert (output_dir / "index.html").exists()
    assert (output_dir / "report.json").exists()


def test_cli_format_html_writes_only_html(fake_repo: FakeRepo, tmp_path: Path) -> None:
    _make_coupled_history(fake_repo, 4)
    output_dir = tmp_path / "html-report"

    result = runner.invoke(
        app,
        ["--repo", str(fake_repo.path), "--output-dir", str(output_dir), "--format", "html"],
    )

    assert result.exit_code == 0, result.output
    assert (output_dir / "index.html").exists()
    assert not (output_dir / "report.json").exists()


def test_cli_format_json_writes_only_json(fake_repo: FakeRepo, tmp_path: Path) -> None:
    _make_coupled_history(fake_repo, 4)
    output_dir = tmp_path / "json-report"

    result = runner.invoke(
        app,
        ["--repo", str(fake_repo.path), "--output-dir", str(output_dir), "--format", "json"],
    )

    assert result.exit_code == 0, result.output
    assert (output_dir / "report.json").exists()
    assert not (output_dir / "index.html").exists()


def test_cli_no_pairs_prints_e008_and_exits_zero(fake_repo: FakeRepo, tmp_path: Path) -> None:
    _make_coupled_history(fake_repo, 2)

    result = runner.invoke(
        app,
        [
            "--repo",
            str(fake_repo.path),
            "--output-dir",
            str(tmp_path / "report"),
            "--min-occurrences",
            "999",
        ],
    )

    assert result.exit_code == 0, result.output
    assert "No coupling pairs found. Try decreasing --min-occurrences" in result.output
    assert not (tmp_path / "report").exists()


def test_cli_invalid_repo_prints_e001(tmp_path: Path) -> None:
    missing = tmp_path / "missing"

    result = runner.invoke(app, ["--repo", str(missing)])

    assert result.exit_code == 1
    assert f"Error: Not a git repository: {missing}" in result.output


def test_cli_custom_output_dir_writes_both_files(fake_repo: FakeRepo, tmp_path: Path) -> None:
    _make_coupled_history(fake_repo, 4)
    output_dir = tmp_path / "custom-dir"

    result = runner.invoke(app, ["--repo", str(fake_repo.path), "--output-dir", str(output_dir)])

    assert result.exit_code == 0, result.output
    assert (output_dir / "index.html").exists()
    assert (output_dir / "report.json").exists()


def test_cli_old_history_prints_e003(fake_repo: FakeRepo, tmp_path: Path) -> None:
    fake_repo.commit(["src/old.py", "src/ancient.py"], days_ago=10)

    result = runner.invoke(
        app,
        [
            "--repo",
            str(fake_repo.path),
            "--output-dir",
            str(tmp_path / "report"),
            "--lookback-days",
            "1",
        ],
    )

    assert result.exit_code == 0, result.output
    assert "No commits found in the last 1 days. Try increasing --lookback-days." in result.output


def test_cli_invalid_yaml_prints_e004(fake_repo: FakeRepo) -> None:
    (fake_repo.path / ".churnmap.yml").write_text("lookback_days: [90\n", encoding="utf-8")

    result = runner.invoke(app, ["--repo", str(fake_repo.path)])

    assert result.exit_code == 1
    assert "Error in .churnmap.yml:" in result.output


def test_cli_json_output_parses_and_has_schema(fake_repo: FakeRepo, tmp_path: Path) -> None:
    _make_coupled_history(fake_repo, 4)
    output_dir = tmp_path / "report"

    result = runner.invoke(app, ["--repo", str(fake_repo.path), "--output-dir", str(output_dir)])

    assert result.exit_code == 0, result.output
    data = json.loads((output_dir / "report.json").read_text(encoding="utf-8"))
    assert data["meta"]["repo"]
    assert data["pairs"]
    assert set(data["pairs"][0]) == {
        "file_a",
        "file_b",
        "score",
        "co_changes",
        "total_commits",
        "risk",
    }


def test_version_flag_prints_version() -> None:
    result = runner.invoke(app, ["--version"])

    assert result.exit_code == 0
    assert "churnmap 1.0.0" in result.output


def _make_coupled_history(fake_repo: FakeRepo, commits: int) -> None:
    for index in range(commits):
        fake_repo.commit(
            ["src/payment.py", "src/billing.py"],
            message=f"coupled change {index}",
        )
