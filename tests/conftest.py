"""Shared pytest fixtures for churnmap tests."""

from __future__ import annotations

import os
import subprocess
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest
from coupling_core import CouplingPair, RepoAnalysis

from churnmap.config import ChurnmapConfig


@dataclass(frozen=True)
class FakeRepo:
    path: Path

    def commit(self, files: list[str], message: str | None = None, days_ago: int = 0) -> None:
        timestamp = datetime.now(UTC) - timedelta(days=days_ago)
        env = os.environ | {
            "GIT_AUTHOR_DATE": timestamp.strftime("%Y-%m-%dT%H:%M:%S%z"),
            "GIT_COMMITTER_DATE": timestamp.strftime("%Y-%m-%dT%H:%M:%S%z"),
        }
        for file_name in files:
            path = self.path / file_name
            path.parent.mkdir(parents=True, exist_ok=True)
            current = path.read_text(encoding="utf-8") if path.exists() else ""
            path.write_text(
                f"{current}change {datetime.now(UTC).isoformat()}\n",
                encoding="utf-8",
            )

        _git(self.path, "add", *files)
        _git(
            self.path,
            "commit",
            "-m",
            message or f"test commit {datetime.now(UTC).isoformat()}",
            env=env,
        )


@pytest.fixture
def fake_repo(tmp_path: Path) -> FakeRepo:
    _git(tmp_path, "init")
    _git(tmp_path, "config", "user.email", "test@example.com")
    _git(tmp_path, "config", "user.name", "Test User")
    return FakeRepo(tmp_path)


@pytest.fixture
def sample_pairs() -> list[CouplingPair]:
    return [
        CouplingPair("src/payment.py", "src/billing.py", 0.82, 41, 50, "high"),
        CouplingPair("src/payment.py", "src/cart.py", 0.64, 16, 25, "medium"),
        CouplingPair("src/billing.py", "src/tax.py", 0.58, 12, 22, "medium"),
        CouplingPair("src/reporting.py", "src/export.py", 0.31, 7, 18, "medium"),
        CouplingPair("src/low.py", "src/helpers.py", 0.12, 4, 12, "low"),
    ]


@pytest.fixture
def sample_config(tmp_path: Path) -> ChurnmapConfig:
    return ChurnmapConfig(output_dir=tmp_path / "report")


@pytest.fixture
def sample_analysis(sample_pairs: list[CouplingPair]) -> RepoAnalysis:
    return RepoAnalysis(
        pairs=sample_pairs,
        total_commits_analyzed=50,
        lookback_days=90,
        repo_name="Meru143/churnmap",
    )


def _git(cwd: Path, *args: str, env: dict[str, str] | None = None) -> None:
    result = subprocess.run(
        ["git", *args],
        cwd=cwd,
        capture_output=True,
        text=True,
        check=False,
        env=env,
    )
    if result.returncode != 0:
        raise AssertionError(
            f"git {' '.join(args)} failed\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"
        )
