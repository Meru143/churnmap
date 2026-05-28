"""CLI entrypoint for churnmap."""

from __future__ import annotations

import os
import subprocess
from pathlib import Path
from typing import Annotated

import coupling_core
import typer
from coupling_core import Config as CouplingCoreConfig
from coupling_core import CouplingCoreError, ShallowCloneError
from rich.progress import Progress, SpinnerColumn, TextColumn

from churnmap import __version__
from churnmap.config import ConfigError, build_config
from churnmap.data_preparer import DataPreparer
from churnmap.html_renderer import HtmlRenderer
from churnmap.json_writer import JsonWriter
from churnmap.output_writer import OutputWriter

app = typer.Typer(name="churnmap", help="Coupling heatmap generator for git repos.")


@app.command()
def main(
    ctx: typer.Context,
    repo: Annotated[Path, typer.Option("--repo", help="Path to git repository root.")] = Path("."),
    output_dir: Annotated[
        Path,
        typer.Option("--output-dir", help="Output directory for report files."),
    ] = Path("./coupling-report"),
    lookback_days: Annotated[
        int,
        typer.Option("--lookback-days", help="Days of git history to analyze."),
    ] = 90,
    min_occurrences: Annotated[
        int,
        typer.Option("--min-occurrences", help="Minimum co-change count to include a pair."),
    ] = 3,
    heatmap_limit: Annotated[
        int,
        typer.Option("--heatmap-limit", help="Max files in heatmap."),
    ] = 50,
    top_files: Annotated[
        int,
        typer.Option("--top-files", help="Max pairs in the HTML table."),
    ] = 100,
    format: Annotated[
        str,
        typer.Option("--format", help="Output format: both, html, or json."),
    ] = "both",
    exclude: Annotated[
        list[str] | None,
        typer.Option("--exclude", help="Glob pattern to exclude. Repeat for multiple patterns."),
    ] = None,
    low_threshold: Annotated[
        float,
        typer.Option("--low-threshold", help="Score below this is Low risk."),
    ] = 0.3,
    high_threshold: Annotated[
        float,
        typer.Option("--high-threshold", help="Score at or above this is High risk."),
    ] = 0.7,
    open_browser: Annotated[
        bool,
        typer.Option("--open/--no-open", help="Open HTML report in browser after generation."),
    ] = False,
    version: Annotated[
        bool,
        typer.Option("--version", is_eager=True, help="Print churnmap version and exit."),
    ] = False,
) -> None:
    """Analyze a git repository and generate coupling reports."""

    if version:
        typer.echo(f"churnmap {__version__}")
        raise typer.Exit()

    if not _is_git_repo(repo):
        typer.echo(f"Error: Not a git repository: {repo}", err=True)
        raise typer.Exit(1)

    cli_kwargs = _build_cli_kwargs(
        ctx=ctx,
        repo=repo,
        output_dir=output_dir,
        lookback_days=lookback_days,
        min_occurrences=min_occurrences,
        heatmap_limit=heatmap_limit,
        top_files=top_files,
        format=format,
        exclude=exclude,
        low_threshold=low_threshold,
        high_threshold=high_threshold,
        open_browser=open_browser,
    )

    try:
        config = build_config(cli_kwargs, repo)
    except ConfigError as exc:
        typer.echo(f"Error in .churnmap.yml: {exc}", err=True)
        raise typer.Exit(1) from exc

    _debug(
        "config: "
        f"repo={config.repo}, output_dir={config.output_dir}, "
        f"lookback_days={config.lookback_days}, "
        f"min_occurrences={config.min_occurrences}, format={config.format}"
    )

    coupling_core_config = CouplingCoreConfig(
        lookback_days=config.lookback_days,
        min_occurrences=config.min_occurrences,
        low_threshold=config.low_threshold,
        high_threshold=config.high_threshold,
        exclude=config.exclude,
    )

    try:
        with Progress(SpinnerColumn("line"), TextColumn("{task.description}")) as progress:
            task = progress.add_task("[cyan]Analyzing git history...", total=None)
            analysis = coupling_core.analyze_repo(config.repo, coupling_core_config)
            progress.update(task, completed=True)
    except ShallowCloneError as exc:
        typer.echo(
            "Error: Repository is a shallow clone. Add 'fetch-depth: 0' to your checkout step, "
            "or run: git fetch --unshallow",
            err=True,
        )
        raise typer.Exit(1) from exc
    except CouplingCoreError as exc:
        message = str(exc)
        if "not a git repository" in message.lower() or "path does not exist" in message.lower():
            typer.echo(f"Error: Not a git repository: {config.repo}", err=True)
        else:
            typer.echo(f"Error: {exc}", err=True)
        raise typer.Exit(1) from exc

    if analysis.total_commits_analyzed == 0:
        typer.echo(
            f"No commits found in the last {config.lookback_days} days. "
            "Try increasing --lookback-days."
        )
        raise typer.Exit()

    if not analysis.pairs:
        typer.echo(
            "No coupling pairs found. Try decreasing --min-occurrences "
            "or increasing --lookback-days."
        )
        raise typer.Exit()

    report_data = DataPreparer(config).prepare(analysis)
    _debug(
        f"pairs={len(report_data.all_pairs)}, heatmap_files={len(report_data.heatmap.files)}, "
        f"nodes={len(report_data.force_graph.nodes)}"
    )

    html_str = HtmlRenderer().render(report_data) if config.format in {"html", "both"} else None
    json_str = JsonWriter().write(report_data) if config.format in {"json", "both"} else None

    try:
        OutputWriter(config).write(html_str, json_str)
    except PermissionError as exc:
        raise typer.Exit(1) from exc


def _build_cli_kwargs(ctx: typer.Context, **values: object) -> dict[str, object]:
    """Return only values explicitly provided on the command line."""

    explicit: dict[str, object] = {}
    for key, value in values.items():
        click_key = "format" if key == "format" else key
        if _is_command_line_value(ctx, click_key):
            explicit[key] = [] if key == "exclude" and value is None else value
    return explicit


def _is_command_line_value(ctx: typer.Context, name: str) -> bool:
    source = ctx.get_parameter_source(name)
    return getattr(source, "name", "") == "COMMANDLINE"


def _is_git_repo(repo: Path) -> bool:
    if not repo.exists():
        return False
    result = subprocess.run(
        ["git", "-C", str(repo), "rev-parse", "--is-inside-work-tree"],
        capture_output=True,
        text=True,
        check=False,
    )
    return result.returncode == 0 and result.stdout.strip() == "true"


def _debug(message: str) -> None:
    if os.environ.get("CHURNMAP_DEBUG") == "1":
        typer.echo(f"DEBUG: {message}", err=True)


if __name__ == "__main__":
    app()
