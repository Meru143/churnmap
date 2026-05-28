"""OutputWriter tests."""

from __future__ import annotations

from pathlib import Path
from typing import Any
from unittest.mock import Mock

from churnmap.config import ChurnmapConfig
from churnmap.output_writer import OutputWriter


def test_output_dir_created_when_missing(tmp_path: Path) -> None:
    output_dir = tmp_path / "new-dir"

    OutputWriter(ChurnmapConfig(output_dir=output_dir)).ensure_output_dir()

    assert output_dir.is_dir()


def test_existing_output_dir_does_not_error(tmp_path: Path) -> None:
    tmp_path.mkdir(exist_ok=True)

    OutputWriter(ChurnmapConfig(output_dir=tmp_path)).ensure_output_dir()

    assert tmp_path.is_dir()


def test_index_html_written_when_html_str_provided(tmp_path: Path) -> None:
    OutputWriter(ChurnmapConfig(output_dir=tmp_path)).write("<html></html>", None)

    assert (tmp_path / "index.html").read_text(encoding="utf-8") == "<html></html>"


def test_report_json_written_when_json_str_provided(tmp_path: Path) -> None:
    OutputWriter(ChurnmapConfig(output_dir=tmp_path)).write(None, "{}")

    assert (tmp_path / "report.json").read_text(encoding="utf-8") == "{}"


def test_neither_file_written_when_both_outputs_are_none(tmp_path: Path) -> None:
    OutputWriter(ChurnmapConfig(output_dir=tmp_path)).write(None, None)

    assert not (tmp_path / "index.html").exists()
    assert not (tmp_path / "report.json").exists()


def test_webbrowser_open_called_when_open_browser_true(
    tmp_path: Path,
    monkeypatch: Any,
) -> None:
    opener = Mock(return_value=True)
    monkeypatch.setattr("churnmap.output_writer.webbrowser.open", opener)

    OutputWriter(ChurnmapConfig(output_dir=tmp_path, open_browser=True)).write(
        "<html></html>",
        None,
    )

    opener.assert_called_once_with(str(tmp_path / "index.html"))


def test_webbrowser_open_not_called_when_open_browser_false(
    tmp_path: Path,
    monkeypatch: Any,
) -> None:
    opener = Mock(return_value=True)
    monkeypatch.setattr("churnmap.output_writer.webbrowser.open", opener)

    OutputWriter(ChurnmapConfig(output_dir=tmp_path, open_browser=False)).write(
        "<html></html>",
        None,
    )

    opener.assert_not_called()


def test_html_path_printed_after_successful_write(tmp_path: Path, capsys: Any) -> None:
    OutputWriter(ChurnmapConfig(output_dir=tmp_path)).write("<html></html>", None)

    captured = capsys.readouterr()

    assert f"Report generated: {tmp_path / 'index.html'}" in captured.out


def test_json_path_printed_after_successful_write(tmp_path: Path, capsys: Any) -> None:
    OutputWriter(ChurnmapConfig(output_dir=tmp_path)).write(None, "{}")

    captured = capsys.readouterr()

    assert f"Report generated: {tmp_path / 'report.json'}" in captured.out
