# 2026-05-27 — churnmap TODO

<!--
Active skills (this session, 2026-05-28):
  - Loaded in session: git-commit (general practice), systematic-debugging (general practice), test-driven-development (general practice)
  - Named in prompt but NOT loaded as Claude Code skills: architecture-patterns, error-handling-patterns, devops-engineer
    → equivalent practices applied inline from general engineering principles

Skill→Phase mapping:
  Phase 1  → devops-engineer (general), git-commit
  Phase 2  → architecture-patterns (general)
  Phase 3  → architecture-patterns, error-handling-patterns (general)
  Phase 4  → architecture-patterns, error-handling-patterns (general)
  Phase 5  → architecture-patterns, systematic-debugging
  Phase 6  → architecture-patterns, systematic-debugging
  Phase 7  → architecture-patterns (general)
  Phase 8  → error-handling-patterns (general)
  Phase 9  → test-driven-development, systematic-debugging
  Phase 10 → test-driven-development, systematic-debugging
  Phase 11 → test-driven-development
  Phase 12 → git-commit
-->

---

## Phase 1: Project Setup

### 1.1 Repository Initialization
- [x] `git init churnmap` and push to `Meru143/churnmap` on GitHub
- [x] Create `README.md` with name, one-liner, install placeholder
- [x] Create `LICENSE` (MIT)
- [x] Create `.gitignore`: `__pycache__/`, `*.pyc`, `.coverage`, `dist/`, `.mypy_cache/`, `.ruff_cache/`, `*.egg-info/`, `coupling-report/`
- [x] Create `CHANGELOG.md` with `## [Unreleased]` section
- [x] Create `.churnmap.yml` with all defaults (dogfooding config for churnmap's own repo)

### 1.2 Directory Structure
- [x] Create `src/churnmap/` package directory
- [x] Create `src/churnmap/__init__.py` with `__version__ = "1.0.0"`
- [x] Create `src/churnmap/main.py` (stub)
- [x] Create `src/churnmap/config.py` (stub)
- [x] Create `src/churnmap/data_preparer.py` (stub)
- [x] Create `src/churnmap/html_renderer.py` (stub)
- [x] Create `src/churnmap/json_writer.py` (stub)
- [x] Create `src/churnmap/output_writer.py` (stub)
- [x] Create `src/churnmap/templates/` directory
- [x] Create `src/churnmap/templates/report.html.j2` (empty stub)
- [x] Create `tests/` with `__init__.py`
- [x] Create `tests/conftest.py` (stub)
- [x] Create `tests/test_config.py` (stub)
- [x] Create `tests/test_data_preparer.py` (stub)
- [x] Create `tests/test_html_renderer.py` (stub)
- [x] Create `tests/test_json_writer.py` (stub)
- [x] Create `tests/test_output_writer.py` (stub)
- [x] Create `.github/workflows/` directory

### 1.3 Package Metadata
- [x] Create `pyproject.toml` with `[project]`: `name = "churnmap"`, `version = "1.0.0"`, `requires-python = ">=3.11"`
- [x] Add `[project.dependencies]`: `coupling-core>=1.0,<2.0`, `typer>=0.26.0`, `rich>=15.0.0`, `Jinja2>=3.1.6`, `PyYAML>=6.0.2`
- [x] Add `[project.optional-dependencies]` `dev`: `pytest>=9.0.3`, `pytest-cov>=6.1.0`, `ruff>=0.11`, `mypy>=1.15`
- [x] Add `[project.scripts]`: `churnmap = "churnmap.main:app"`
- [x] Add `[tool.ruff]`: `select = ["E","F","I","UP"]`, `line-length = 100`
- [x] Add `[tool.mypy]`: `strict = true`, `python_version = "3.11"`
- [x] Add `[tool.pytest.ini_options]`: `testpaths = ["tests"]`, `addopts = "-v"`
- [x] Add `[build-system]`: `requires = ["hatchling"]`, `build-backend = "hatchling.build"`
- [x] Add `[tool.hatch.build.targets.wheel]`: `packages = ["src/churnmap"]` — ensures Jinja2 templates are included via `include = ["src/churnmap/templates/*"]`

### 1.4 Makefile
- [x] Add target `make dev`: `pip install -e ".[dev]"`
- [x] Add target `make lint`: `ruff check src/ tests/`
- [x] Add target `make type-check`: `mypy src/ --strict`
- [x] Add target `make test`: `pytest tests/ -v --cov=src/churnmap --cov-report=term-missing`
- [x] Add target `make build`: `python -m build`
- [x] Add target `make demo`: `churnmap --repo . --output-dir /tmp/churnmap-demo`

### 1.5 CI Workflow
- [x] Create `.github/workflows/ci.yml`: trigger `push` to `main`, `pull_request` to `main`
- [x] Add job `lint`: `ruff check src/ tests/`
- [x] Add job `type-check`: `mypy src/ --strict`
- [x] Add job `test`: matrix `python-version: ["3.11","3.12","3.13"]`, `os: ["ubuntu-latest","macos-latest","windows-latest"]`
- [x] Add step: `pytest tests/ -v --cov=src/churnmap --cov-report=xml`
- [x] Add step: upload coverage to Codecov via `codecov/codecov-action@v4`

### 1.6 Release Workflow
- [x] Create `.github/workflows/release.yml`: trigger `push` to `main`
- [x] Add job: `python-semantic-release publish`
- [x] Configure Trusted Publishing for PyPI in `[tool.semantic_release]` block

### 1.7 Community Files
- [x] Create `CONTRIBUTING.md`: local dev setup, `make test`, commit conventions
- [x] Create `CODE_OF_CONDUCT.md` (Contributor Covenant 2.1)
- [x] Create `SECURITY.md`
- [x] Create `.github/ISSUE_TEMPLATE/bug_report.md`
- [x] Create `.github/ISSUE_TEMPLATE/feature_request.md`
- [x] Create `.github/PULL_REQUEST_TEMPLATE.md`
- [x] Create `.editorconfig`: `indent_style=space`, `indent_size=4`, `end_of_line=lf`
- [x] Create `.github/dependabot.yml`: `package-ecosystem: pip`, `schedule: weekly`

---

## Phase 2: Data Models

### 2.1 ChurnmapConfig Dataclass (config.py)
- [x] Define `@dataclass class ChurnmapConfig` with `repo: Path = Path(".")`
- [x] Add `output_dir: Path = Path("./coupling-report")`
- [x] Add `lookback_days: int = 90`
- [x] Add `min_occurrences: int = 3`
- [x] Add `heatmap_limit: int = 50`
- [x] Add `top_files: int = 100`
- [x] Add `format: str = "both"` (literal: `"both"` | `"html"` | `"json"`)
- [x] Add `exclude: list[str] = field(default_factory=list)`
- [x] Add `low_threshold: float = 0.3`
- [x] Add `high_threshold: float = 0.7`
- [x] Add `open_browser: bool = False`

### 2.2 HeatmapData Dataclass (data_preparer.py)
- [x] Define `@dataclass class HeatmapData` with `files: list[str]`
- [x] Add `matrix: list[list[float]]`
- [x] Add `file_commit_counts: dict[str, int]`

### 2.3 ForceGraphData Dataclass (data_preparer.py)
- [x] Define `@dataclass class ForceGraphData` with `nodes: list[dict]`
- [x] Add `links: list[dict]`

### 2.4 ReportData Dataclass (data_preparer.py)
- [x] Define `@dataclass class ReportData` with `heatmap: HeatmapData`
- [x] Add `force_graph: ForceGraphData`
- [x] Add `table_pairs: list` (list of `CouplingPair` from coupling-core)
- [x] Add `repo_name: str`
- [x] Add `generated_at: str`
- [x] Add `total_commits_analyzed: int`
- [x] Add `lookback_days: int`
- [x] Add `churnmap_version: str`

### 2.5 Custom Exception (config.py)
- [x] Define `class ConfigError(Exception): pass`

---

## Phase 3: Config Loader

### 3.1 YAML Loading (config.py)
- [x] Define `def load_yaml_config(repo_path: Path) -> dict`
- [x] Check for `.churnmap.yml` at `repo_path / ".churnmap.yml"`
- [x] If exists: `yaml.safe_load(f)` — catch `yaml.YAMLError` → raise `ConfigError` with line number
- [x] If missing: return `{}`

### 3.2 Config Merge (config.py)
- [x] Define `def build_config(cli_kwargs: dict, repo_path: Path) -> ChurnmapConfig`
- [x] Load YAML: `yaml_data = load_yaml_config(repo_path)`
- [x] Merge priority: defaults → YAML → CLI kwargs (CLI wins)
- [x] Cast YAML values to correct types (YAML may parse `"90"` as string if user quotes it)
- [x] Return `ChurnmapConfig(**merged)`

---

## Phase 4: CLI Entrypoint

### 4.1 Typer App (main.py)
- [x] Import `typer`, `rich`, `pathlib.Path`, `typing.Optional`, `typing.Annotated`
- [x] Create `app = typer.Typer(name="churnmap", help="Coupling heatmap generator for git repos.")`
- [x] Define `@app.command() def main(...)` with all flags as typed parameters with `typer.Option(...)`:
  - [x] `repo: Annotated[Path, typer.Option("--repo", help="Path to git repository root.")] = Path(".")`
  - [x] `output_dir: Annotated[Path, typer.Option("--output-dir", help="Output directory for report files.")] = Path("./coupling-report")`
  - [x] `lookback_days: Annotated[int, typer.Option("--lookback-days")] = 90`
  - [x] `min_occurrences: Annotated[int, typer.Option("--min-occurrences")] = 3`
  - [x] `heatmap_limit: Annotated[int, typer.Option("--heatmap-limit")] = 50`
  - [x] `top_files: Annotated[int, typer.Option("--top-files")] = 100`
  - [x] `format: Annotated[str, typer.Option("--format")] = "both"`
  - [x] `exclude: Annotated[Optional[list[str]], typer.Option("--exclude")] = None`
  - [x] `low_threshold: Annotated[float, typer.Option("--low-threshold")] = 0.3`
  - [x] `high_threshold: Annotated[float, typer.Option("--high-threshold")] = 0.7`
  - [x] `open_browser: Annotated[bool, typer.Option("--open/--no-open")] = False`
  - [x] `version: Annotated[bool, typer.Option("--version", is_eager=True)] = False`

### 4.2 Version Flag (main.py)
- [x] In `main()`: if `version` is True: `typer.echo(f"churnmap {__version__}")` and `raise typer.Exit()`

### 4.3 Config Build in main() (main.py)
- [x] Build `cli_kwargs` dict from all flag values
- [x] Call `build_config(cli_kwargs, repo)` → `config` — catch `ConfigError` → `typer.echo(f"Error in .churnmap.yml: {e}", err=True)` and `raise typer.Exit(1)`

### 4.4 Progress Bar Setup (main.py)
- [x] Import `from rich.progress import Progress, SpinnerColumn, TextColumn`
- [x] Wrap `coupling_core.analyze_repo` call in `with Progress(SpinnerColumn(), TextColumn("{task.description}")) as progress:`
- [x] Add task: `task = progress.add_task("[cyan]Analyzing git history...", total=None)`
- [x] After call: `progress.update(task, completed=True)`
- [x] rich `Progress` auto-suppresses in non-TTY (CI/pipe) environments — no extra handling needed

### 4.5 Analysis Call (main.py)
- [x] Import `coupling_core` and `coupling_core.models.ShallowCloneError`, `coupling_core.models.CouplingCoreError`
- [x] Call `coupling_core.analyze_repo(config.repo, coupling_core_config)` — build `coupling_core.Config` from `ChurnmapConfig` fields
- [x] Catch `ShallowCloneError` → print E002 message, `raise typer.Exit(1)`
- [x] Catch `CouplingCoreError` → print `Error: {e}`, `raise typer.Exit(1)`
- [x] If `analysis.pairs` is empty → print E008 message, `raise typer.Exit(0)`

### 4.6 Report Generation (main.py)
- [x] Call `DataPreparer(config).prepare(analysis)` → `ReportData`
- [x] If `config.format in ("html", "both")`: call `HtmlRenderer().render(report_data)` → `html_str`
- [x] If `config.format in ("json", "both")`: call `JsonWriter().write(report_data)` → `json_str`
- [x] Call `OutputWriter(config).write(html_str if html else None, json_str if json else None)`

### 4.7 Entrypoint (main.py)
- [x] Add at module bottom: `if __name__ == "__main__": app()`
- [x] Add in `pyproject.toml` `[project.scripts]`: `churnmap = "churnmap.main:app"` — already done in Phase 1.3 but verify here

---

## Phase 5: Data Preparer

### 5.1 Top Files for Heatmap (data_preparer.py)
- [x] Define `def top_files_for_heatmap(pairs: list, heatmap_limit: int) -> list[str]`
- [x] Build `max_score_per_file: dict[str, float]` — for each pair, update both `file_a` and `file_b` entries with `max(current, score)`
- [x] Sort files by `max_score_per_file[f]` descending
- [x] Return top `min(heatmap_limit, len(files))` file paths

### 5.2 Heatmap Matrix Construction (data_preparer.py)
- [x] Define `def build_heatmap_matrix(files: list[str], pairs: list) -> list[list[float]]`
- [x] Build `pair_lookup: dict[tuple[str,str], float]` from all pairs: `{(a,b): score, (b,a): score}`
- [x] Initialize `matrix = [[0.0] * N for _ in range(N)]` where `N = len(files)`
- [x] For each `(i, j)`: `matrix[i][j] = pair_lookup.get((files[i], files[j]), 0.0)`
- [x] Return `matrix`

### 5.3 Force Graph Data (data_preparer.py)
- [x] Define `def build_force_graph_data(pairs: list, file_commit_counts: dict, config: ChurnmapConfig) -> ForceGraphData`
- [x] Collect all unique files from pairs
- [x] For each file: compute `max_score = max(p.score for p in pairs if p.file_a==file or p.file_b==file)`
- [x] Build node list: `{"id": file.replace("\\", "/"), "churn": file_commit_counts.get(file, 1), "max_score": max_score, "risk": classify_risk(max_score, config)}`
- [x] Build link list: `{"source": pair.file_a.replace("\\", "/"), "target": pair.file_b.replace("\\", "/"), "score": pair.score, "risk": pair.risk}`
- [x] Return `ForceGraphData(nodes=nodes, links=links)`

### 5.4 Risk Classification for Preparer (data_preparer.py)
- [x] Define `def classify_risk(score: float, config: ChurnmapConfig) -> str`
- [x] Return `"low"` if `score < config.low_threshold`, `"medium"` if `score < config.high_threshold`, else `"high"`

### 5.5 Full Prepare Method (data_preparer.py)
- [x] Define `class DataPreparer` with `__init__(self, config: ChurnmapConfig)`
- [x] Define `def prepare(self, analysis: RepoAnalysis) -> ReportData`
- [x] Get `file_commit_counts` from `coupling_core.get_file_commit_counts(analysis.commits)` — NOTE: need to expose commits from RepoAnalysis or call `get_file_commit_counts` separately; verify coupling-core API surface supports this
- [x] Call `top_files_for_heatmap(analysis.pairs, config.heatmap_limit)` → `top_files`
- [x] Call `build_heatmap_matrix(top_files, analysis.pairs)` → `matrix`
- [x] Build `HeatmapData(files=top_files, matrix=matrix, file_commit_counts=...)`
- [x] Call `build_force_graph_data(analysis.pairs, file_commit_counts, config)` → `ForceGraphData`
- [x] Table pairs: `analysis.pairs[:config.top_files]`
- [x] Return `ReportData(heatmap=..., force_graph=..., table_pairs=..., repo_name=analysis.repo_name, generated_at=date.today().isoformat(), total_commits_analyzed=analysis.total_commits_analyzed, lookback_days=analysis.lookback_days, churnmap_version=__version__)`

---

## Phase 6: HTML Renderer

### 6.1 Jinja2 Environment (html_renderer.py)
- [x] Import `jinja2`, `importlib.resources`
- [x] Define `def get_jinja_env() -> jinja2.Environment`
- [x] Use `jinja2.PackageLoader("churnmap", "templates")` to load templates from the package
- [x] Set `autoescape=False` (HTML template, data already sanitized)
- [x] Catch `jinja2.TemplateNotFound` → raise `RuntimeError("Internal error: report template not found — please reinstall churnmap")`

### 6.2 Template Render (html_renderer.py)
- [x] Define `class HtmlRenderer`
- [x] Define `def render(self, report_data: ReportData) -> str`
- [x] Call `env.get_template("report.html.j2")` → `template`
- [x] Build template context dict from `ReportData` fields
- [x] Serialize `HeatmapData.files`, `HeatmapData.matrix`, `ForceGraphData.nodes`, `ForceGraphData.links` to JSON strings via `json.dumps` (for embedding in `<script>` tag)
- [x] Call `template.render(context)` → `html_str`
- [x] Return `html_str`

### 6.3 Jinja2 Report Template (templates/report.html.j2)
- [x] Write `<!DOCTYPE html>` + `<html lang="en">` structure
- [x] Add `<title>ChurnMap — {{ repo_name }}</title>` in `<head>`
- [x] Add inline CSS for: tab switcher, table, heatmap cell colors, force graph container
- [x] Add D3.js CDN script: `<script src="https://cdn.jsdelivr.net/npm/d3@7/dist/d3.min.js"></script>`
- [x] Add HTML comment: `<!-- D3.js loaded from CDN. Report requires internet to render visualizations. -->`
- [x] Add three tab buttons: "Heatmap", "Force Graph", "Table"
- [x] Add div `id="tab-heatmap"` (default visible): contains SVG for D3 heatmap
- [x] Add div `id="tab-force"` (default hidden): contains SVG for D3 force graph
- [x] Add div `id="tab-table"` (default hidden): contains HTML table of top pairs
- [x] Add summary stats bar: total pairs, max score, total commits analyzed, lookback days
- [x] Add tab switching JavaScript (pure JS, no framework): `function showTab(name) { ... }`

### 6.4 D3 Heatmap JavaScript (inside report.html.j2)
- [x] Embed heatmap data as JavaScript: `const heatmapFiles = {{ heatmap_files_json }};` and `const heatmapMatrix = {{ heatmap_matrix_json }};`
- [x] D3 `scaleBand` for X and Y axes using `heatmapFiles`
- [x] D3 `scaleSequential(d3.interpolateRdYlGn).domain([1, 0])` for cell color (high score = red)
- [x] Draw cells via `svg.selectAll("rect").data(flatCells).join("rect")`
- [x] Add X-axis labels rotated 45 degrees (truncated to 20 chars with `...`)
- [x] Add Y-axis labels (truncated to 20 chars with `...`)
- [x] Add hover tooltip showing `file_a ↔ file_b: score (co_changes co-changes)` via D3 `title` or `mouseover` event

### 6.5 D3 Force Graph JavaScript (inside report.html.j2)
- [x] Embed force graph data: `const nodes = {{ force_nodes_json }};` and `const links = {{ force_links_json }};`
- [x] Create SVG with width 100%, height 600px
- [x] D3 `forceSimulation(nodes)` with `.force("link", d3.forceLink(links).id(d => d.id))`, `.force("charge", d3.forceManyBody().strength(-200))`, `.force("center", d3.forceCenter(width/2, height/2))`
- [x] Node radius: `const rScale = d3.scaleLinear().domain([minChurn, maxChurn]).range([5, 25]); r = rScale(d.churn)`
- [x] Node fill color: `d.risk === "high" ? "#ef4444" : d.risk === "medium" ? "#f59e0b" : "#22c55e"`
- [x] Link stroke width: `d.score * 8` (clamped min 0.5, max 8)
- [x] Link stroke color: `d.score > 0.7 ? "#ef4444" : "#94a3b8"`
- [x] Add drag behavior via `d3.drag()` on each node
- [x] Add hover tooltip on nodes: `"${d.id} — churn: ${d.churn}, max coupling: ${d.max_score.toFixed(2)}"`
- [x] Add hover tooltip on links: `"${d.source.id} ↔ ${d.target.id}: ${d.score.toFixed(2)}"`
- [x] Simulation `tick` handler updates node `cx`/`cy` and link `x1`/`y1`/`x2`/`y2`

### 6.6 Table in Template (report.html.j2)
- [x] Embed table data: `const tablePairs = {{ table_pairs_json }};`
- [x] Render static HTML table via Jinja2 `{% for pair in table_pairs %}` loop (not JavaScript)
- [x] Table columns: `File A`, `File B`, `Score`, `Risk`, `Co-changes`
- [x] Row `Risk` cell: `🟢 Low` / `🟡 Medium` / `🔴 High` based on `pair.risk`
- [x] Add `class="risk-high"` to rows where `pair.risk == "high"` for CSS highlighting

### 6.7 Footer (report.html.j2)
- [x] Add `<footer>Generated by churnmap v{{ churnmap_version }} on {{ generated_at }}</footer>`

---

## Phase 7: JSON Writer

### 7.1 JSON Schema Builder (json_writer.py)
- [x] Define `class JsonWriter`
- [x] Define `def build_json_dict(self, report_data: ReportData) -> dict`
- [x] Build `meta` dict: `{"repo": report_data.repo_name, "generated_at": report_data.generated_at, "lookback_days": report_data.lookback_days, "total_commits_analyzed": report_data.total_commits_analyzed, "churnmap_version": report_data.churnmap_version}`
- [x] Build `pairs` list: for each `CouplingPair` in `report_data.table_pairs` (CORRECTION: use ALL pairs from RepoAnalysis for JSON, not truncated table_pairs — verify against PRD Section 6.7)
- [x] Each pair dict: `{"file_a": pair.file_a, "file_b": pair.file_b, "score": pair.score, "co_changes": pair.co_changes, "total_commits": pair.total_commits, "risk": pair.risk}`
- [x] Return `{"meta": meta, "pairs": pairs}`

### 7.2 JSON Serialization (json_writer.py)
- [x] Define `def write(self, report_data: ReportData) -> str`
- [x] Call `build_json_dict(report_data)` → `data`
- [x] Return `json.dumps(data, indent=2)`

---

## Phase 8: Output Writer

### 8.1 Directory Creation (output_writer.py)
- [x] Define `class OutputWriter` with `__init__(self, config: ChurnmapConfig)`
- [x] Define `def ensure_output_dir(self) -> None`
- [x] Call `config.output_dir.mkdir(parents=True, exist_ok=True)` — catch `PermissionError` → `typer.echo(f"Cannot create output directory: {config.output_dir}: {e}", err=True)` and re-raise

### 8.2 File Writing (output_writer.py)
- [x] Define `def write_html(self, html_str: str) -> None`
- [x] Write to `config.output_dir / "index.html"` — catch `PermissionError` → E006 message
- [x] Define `def write_json(self, json_str: str) -> None`
- [x] Write to `config.output_dir / "report.json"` — catch `PermissionError` → E006 message

### 8.3 Path Output (output_writer.py)
- [x] Define `def print_paths(self, wrote_html: bool, wrote_json: bool) -> None`
- [x] If `wrote_html`: `typer.echo(f"Report generated: {config.output_dir}/index.html")`
- [x] If `wrote_json`: `typer.echo(f"Report generated: {config.output_dir}/report.json")`

### 8.4 Browser Open (output_writer.py)
- [x] Define `def open_browser(self) -> None`
- [x] Import `webbrowser`
- [x] Call `result = webbrowser.open(str(config.output_dir / "index.html"))`
- [x] If `result is False`: `typer.echo(f"Note: Could not open browser automatically. Open manually: {config.output_dir}/index.html")`

### 8.5 Full Write Flow (output_writer.py)
- [x] Define `def write(self, html_str: Optional[str], json_str: Optional[str]) -> None`
- [x] Call `ensure_output_dir()`
- [x] If `html_str is not None`: call `write_html(html_str)` → set `wrote_html = True`
- [x] If `json_str is not None`: call `write_json(json_str)` → set `wrote_json = True`
- [x] Call `print_paths(wrote_html, wrote_json)`
- [x] If `config.open_browser and wrote_html`: call `open_browser()`

---

## Phase 9: Unit Tests

### 9.1 Test Fixtures (conftest.py)
- [x] Define `@pytest.fixture fake_repo(tmp_path)`: `git.Repo.init(tmp_path)`, configure user
- [x] Add `commit(files)` helper to `fake_repo`
- [x] Define `@pytest.fixture sample_pairs()`: return list of 5 known `CouplingPair` objects
- [x] Define `@pytest.fixture sample_config()`: return `ChurnmapConfig()` with defaults
- [x] Define `@pytest.fixture sample_analysis(sample_pairs)`: return `RepoAnalysis` with `sample_pairs`, `total_commits_analyzed=50`, `repo_name="Meru143/churnmap"`, `lookback_days=90`

### 9.2 Config Tests (test_config.py)
- [x] Test: valid YAML loaded, `lookback_days` set correctly
- [x] Test: CLI flag override wins over YAML value
- [x] Test: missing YAML file → all defaults, no error
- [x] Test: invalid YAML → `ConfigError` raised with message containing line number
- [x] Test: multiple `--exclude` values merged into list correctly
- [x] Test: `format="both"` accepted; `format="invalid"` raises `ConfigError`

### 9.3 Data Preparer Tests (test_data_preparer.py)
- [x] Test: `top_files_for_heatmap` returns top N files sorted by max score desc
- [x] Test: `top_files_for_heatmap` clamps when fewer unique files than heatmap_limit
- [x] Test: `build_heatmap_matrix` cell `(i,j)` equals score for `(files[i], files[j])` pair
- [x] Test: `build_heatmap_matrix` cell `(i,j)` = 0.0 when no pair exists
- [x] Test: `build_force_graph_data` node has correct `churn`, `max_score`, `risk` fields
- [x] Test: `build_force_graph_data` link has correct `source`, `target`, `score`, `risk` fields
- [x] Test: Windows backslash paths in node IDs converted to forward slashes
- [x] Test: table_pairs truncated to `top_files` count

### 9.4 HTML Renderer Tests (test_html_renderer.py)
- [x] Test: rendered HTML contains `<script src="https://cdn.jsdelivr.net/npm/d3@7/dist/d3.min.js">`
- [x] Test: rendered HTML `<title>` contains `ChurnMap — Meru143/churnmap`
- [x] Test: rendered HTML contains tab buttons "Heatmap", "Force Graph", "Table"
- [x] Test: rendered HTML contains `<!-- D3.js loaded from CDN` comment
- [x] Test: rendered HTML is non-empty string and begins with `<!DOCTYPE html>`
- [x] Test: footer contains `churnmap_version` string
- [x] Test: rendered HTML contains embedded JSON for heatmap files (verify `heatmapFiles` variable)

### 9.5 JSON Writer Tests (test_json_writer.py)
- [x] Test: `meta.repo` equals `ReportData.repo_name`
- [x] Test: `meta.generated_at` is today's ISO date string
- [x] Test: `meta.churnmap_version` equals `__version__`
- [x] Test: `pairs` sorted by `score` descending
- [x] Test: each pair has keys `file_a`, `file_b`, `score`, `co_changes`, `total_commits`, `risk`
- [x] Test: `json.loads(output)` succeeds without exception
- [x] Test: `pairs` count equals all pairs in RepoAnalysis (not truncated)

### 9.6 Output Writer Tests (test_output_writer.py)
- [x] Test: output dir created when it does not exist (`tmp_path / "new-dir"`)
- [x] Test: no error when output dir already exists
- [x] Test: `index.html` written to output dir when `html_str` provided
- [x] Test: `report.json` written to output dir when `json_str` provided
- [x] Test: neither file written when both are `None`
- [x] Test: `webbrowser.open` called with path to `index.html` when `open_browser=True`
- [x] Test: `webbrowser.open` NOT called when `open_browser=False`
- [x] Test: path printed to stdout after successful HTML write
- [x] Test: path printed to stdout after successful JSON write

---

## Phase 10: Integration Tests

### 10.1 CLI Runner Tests
- [x] Import `typer.testing.CliRunner` and `from churnmap.main import app`
- [x] Define `runner = CliRunner()`
- [x] Test: `runner.invoke(app, ["--repo", str(fake_repo_path)])` → exit code 0, `index.html` + `report.json` exist in `./coupling-report/`
- [x] Test: `--format html` → `index.html` exists, `report.json` does NOT exist
- [x] Test: `--format json` → `report.json` exists, `index.html` does NOT exist
- [x] Test: `--min-occurrences 999` → exit code 0, E008 message in output
- [x] Test: `--repo /nonexistent` → exit code 1, E001 message in stderr
- [x] Test: `--output-dir {tmp_path}/custom-dir` → both files written to custom dir
- [x] Test: `--lookback-days 1` on a repo with 0 recent commits → E003 message, exit 0

### 10.2 JSON Output Validation
- [x] After CLI integration run: `json.loads(Path(output_dir / "report.json").read_text())` succeeds
- [x] Verify `meta.repo` matches the fake repo name
- [x] Verify `pairs` list is non-empty and each pair has correct schema keys

---

## Phase 11: E2E Tests

### 11.1 Full Coupling Detection E2E
- [x] Init `fake_repo` with 10 commits: files `src/payment.py` and `src/billing.py` co-change 8 times, `src/payment.py` changes alone 2 times
- [x] Run `churnmap --repo {fake_repo_path} --output-dir {tmp_path}/report --min-occurrences 3`
- [x] Verify `index.html` and `report.json` both exist
- [x] Parse `report.json` → verify pair `(src/payment.py, src/billing.py)` has `score >= 0.7`

### 11.2 No Pairs E2E
- [x] Init `fake_repo` with 2 commits, each touching a single file (no co-changes)
- [x] Run `churnmap --repo {fake_repo_path} --min-occurrences 3`
- [x] Verify E008 message in output, exit code 0, no output files written

---

## Phase 12: Documentation

### 12.1 README
- [x] Add install badge: `![PyPI](https://img.shields.io/pypi/v/churnmap)` at top
- [x] Add CI badge for main branch
- [x] Add "Install" section: `pip install churnmap` and `uv tool install churnmap`
- [x] Add "Usage" section: minimal one-liner and full options example
- [x] Add "Flags" table (all 12 flags with type, default, description)
- [x] Add "Output" section: explain `index.html` (two-tab) and `report.json` (envelope schema)
- [x] Add "Config file" section with `.churnmap.yml` example
- [x] Add "How it works" section: coupling-core → normalize → render
- [x] Add "Report screenshot" placeholder (or ASCII art of the two-tab report)
- [x] Add "Used alongside" section: link to couplingguard

### 12.2 Marketplace / PyPI
- [x] Write PyPI `description` (< 100 chars): "Coupling heatmap generator — visualize co-change risk in any git repo"
- [x] Add classifiers: `"Topic :: Software Development :: Version Control :: Git"`, `"Topic :: Software Development :: Quality Assurance"`
- [x] Add keywords: `coupling`, `git`, `code-quality`, `heatmap`, `visualization`, `d3`
