"""Output directory, file writing, and browser launch helpers."""

from __future__ import annotations

import webbrowser

import typer

from churnmap.config import ChurnmapConfig


class OutputWriter:
    """Write generated report artifacts to disk."""

    def __init__(self, config: ChurnmapConfig) -> None:
        self.config = config

    def ensure_output_dir(self) -> None:
        try:
            self.config.output_dir.mkdir(parents=True, exist_ok=True)
        except PermissionError as exc:
            typer.echo(f"Cannot create output directory: {self.config.output_dir}: {exc}", err=True)
            raise

    def write_html(self, html_str: str) -> None:
        path = self.config.output_dir / "index.html"
        try:
            path.write_text(html_str, encoding="utf-8")
        except PermissionError:
            typer.echo(f"Cannot write {path.name}: permission denied", err=True)
            raise

    def write_json(self, json_str: str) -> None:
        path = self.config.output_dir / "report.json"
        try:
            path.write_text(json_str, encoding="utf-8")
        except PermissionError:
            typer.echo(f"Cannot write {path.name}: permission denied", err=True)
            raise

    def print_paths(self, wrote_html: bool, wrote_json: bool) -> None:
        if wrote_html:
            typer.echo(f"Report generated: {self.config.output_dir / 'index.html'}")
        if wrote_json:
            typer.echo(f"Report generated: {self.config.output_dir / 'report.json'}")

    def open_browser(self) -> None:
        path = self.config.output_dir / "index.html"
        result = webbrowser.open(str(path))
        if result is False:
            typer.echo(f"Note: Could not open browser automatically. Open manually: {path}")

    def write(self, html_str: str | None, json_str: str | None) -> None:
        self.ensure_output_dir()
        wrote_html = False
        wrote_json = False
        if html_str is not None:
            self.write_html(html_str)
            wrote_html = True
        if json_str is not None:
            self.write_json(json_str)
            wrote_json = True
        self.print_paths(wrote_html, wrote_json)
        if self.config.open_browser and wrote_html:
            self.open_browser()
