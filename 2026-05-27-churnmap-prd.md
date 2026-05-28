# 2026-05-27 — churnmap PRD

## Section 1 — Project Overview

**Name:** churnmap  
**Type:** CLI Tool + PyPI package  
**Language:** Python 3.11+  
**License:** MIT  
**Repository:** `Meru143/churnmap`  
**PyPI package name:** `churnmap`  
**CLI entrypoint:** `churnmap`  
**Description:** churnmap is a dead-simple CLI that analyzes any git repository's co-change history and generates a two-tab interactive HTML report — a coupling heatmap and a D3 force graph — plus a machine-readable JSON file. It is the open-source CodeScene replacement for local, ad-hoc coupling audits. No signup, no external service, no Kubernetes. One command, two files.

---

## Section 2 — Problem Statement

- **CodeScene costs $1k+/month.** Free alternatives are a dead Java CLI from 2016 with no visualization, no normalization, and no maintenance.
- **Repo coupling audits are done manually.** Engineers review large PRs without knowing which files historically break together. ChurnMap makes this visible.
- **The heatmap doesn't scale.** Existing tools that show coupling show a full matrix — unreadable on monorepos with 200+ files. ChurnMap limits to top-N by coupling score.
- **Force graphs are unreadable without metric encoding.** Raw force graphs show all edges at the same weight. ChurnMap encodes churn into node size and coupling into edge thickness + color.
- **JSON output doesn't exist.** No existing free tool exports coupling data as a structured JSON envelope suitable for CI scripts or further analysis.
- **Local analysis requires Kubernetes or a hosted service.** ChurnMap runs on the local machine against any git repo in seconds.

---

## Section 3 — Solution

1. **One command audit:** `churnmap --repo .` → generates `./coupling-report/index.html` and `./coupling-report/report.json`.
2. **Normalized co-change scoring** via `coupling-core` — same algorithm as couplingguard, 0–1 ratio, comparable across repos.
3. **Two-tab HTML report** — heatmap (default tab) + D3 force graph (second tab), self-contained single HTML file with embedded D3.js from CDN.
4. **Heatmap** — top-N files by max coupling score (default 50), color-coded cells by risk, hover tooltip with co-change count.
5. **Force graph** — node size = churn (total commits), node color = max coupling score risk (🟢/🟡/🔴), edge thickness proportional to coupling score, edges >0.7 colored red.
6. **Machine-readable JSON** — flat `pairs` list wrapped in `meta` envelope with repo name, date, lookback days, total commits analyzed.
7. **`rich` progress bar** — real-time feedback during git history parsing, auto-suppressed in non-TTY environments.
8. **Format flag** — `--format html`, `--format json`, or `--format both` (default).

---

## Section 4 — Target Users

| User | Workflow improved |
|------|------------------|
| Platform engineers auditing a monorepo | Run churnmap on the monorepo, share the HTML report with team leads to prioritize decoupling work |
| Senior engineers doing architecture reviews | Generate coupling heatmap of a codebase before or after a major refactor |
| Tech leads onboarding to a new codebase | Instantly see which files are most tightly coupled to understand the hidden dependency structure |
| DevOps/DevSecOps | Pipe `report.json` into custom scripts to gate CI on coupling thresholds |

---

## Section 5 — Tech Stack Table

| Component | Library | Version | Purpose |
|-----------|---------|---------|---------|
| Core algorithm | `coupling-core` | `>=1.0,<2.0` | Git parsing, co-change matrix, normalization, analysis |
| CLI framework | `typer` | `0.26.0` | Type-hint-driven CLI with auto-completion and `--help` |
| Terminal UI | `rich` | `15.0.0` | Progress bar, colored output, non-TTY suppression |
| HTML templating | `Jinja2` | `3.1.6` | HTML report generation from templates |
| Config file | `PyYAML` | `6.0.2` | Parse `.churnmap.yml` |
| Testing | `pytest` | `9.0.3` | Unit and integration tests |
| Coverage | `pytest-cov` | `6.1.0` | Coverage reporting |
| Linting | `ruff` | `0.11.x` | Fast Python linter |
| Type checking | `mypy` | `1.15.x` | Static typing (`--strict`) |
| Release | `python-semantic-release` | `9.x` | Automated versioning from Conventional Commits |

**Visualization (client-side, via CDN):**
| Library | Version | CDN URL |
|---------|---------|---------|
| D3.js | `7.9.0` | `https://cdn.jsdelivr.net/npm/d3@7/dist/d3.min.js` |

**Why Typer over Click?**
Typer 0.26.0 vendors Click internally — one fewer transitive dependency to track. Type-hint-driven API means flags are self-documenting and mypy-checkable. Auto-generates shell completions for bash, zsh, fish, and PowerShell. `typer.run()` for simple single-command CLIs eliminates boilerplate.

**Why Jinja2 for HTML?**
The HTML report has conditional logic (show heatmap tab if heatmap data exists, format risk emoji per cell) that would be unmaintainable in an f-string. Jinja2 templates are version-controlled, testable independently of Python logic, and support template inheritance for future report types.

**Why D3.js via CDN (not bundled)?**
Bundling D3 into the HTML file would add ~550KB to every report. CDN loads once and is cached. Reports are generated locally and viewed in a browser — CDN access is safe to assume. Offline mode is v2 scope.

---

## Section 6 — Core Features (v1)

### 1. CLI Entrypoint
- Single command: `churnmap [OPTIONS]`
- `--repo PATH` (default: `.`) — path to git repository root
- `--output-dir PATH` (default: `./coupling-report`) — where to write output files
- `--lookback-days INTEGER` (default: `90`) — days of git history to analyze
- `--min-occurrences INTEGER` (default: `3`) — minimum co-change count to include a pair
- `--heatmap-limit INTEGER` (default: `50`) — max files shown in heatmap (top by max coupling score)
- `--top-files INTEGER` (default: `100`) — max pairs shown in HTML table
- `--format [both|html|json]` (default: `both`) — output format(s)
- `--exclude TEXT` (multiple, e.g. `--exclude "docs/**" --exclude "*.md"`) — glob patterns to exclude
- `--low-threshold FLOAT` (default: `0.3`) — score below this is 🟢 Low
- `--high-threshold FLOAT` (default: `0.7`) — score above this is 🔴 High
- `--open` (flag, default: off) — open HTML report in browser after generation
- `--version` — print churnmap version and exit
- `--help` — auto-generated by Typer

### 2. Config File
- `.churnmap.yml` in repo root (optional) — same fields as CLI flags, lower priority
- CLI flags override config file values
- Missing config file: silently use defaults (no error)
- Invalid YAML: print error with line number, exit 1

### 3. Git Analysis (via coupling-core)
- Call `coupling_core.analyze_repo(repo_path, config)` → `RepoAnalysis`
- `RepoAnalysis.pairs` is sorted by score desc — all pairs, no truncation at this layer
- rich progress bar wraps the `analyze_repo` call: `[cyan]Analyzing git history... [/cyan]`
- Non-TTY (CI/pipe): progress bar suppressed automatically by rich

### 4. Heatmap Generation
- Take top `heatmap_limit` unique files by their maximum coupling score across all pairs
- Build NxN matrix of these files (N ≤ heatmap_limit)
- Cell `(i, j)` = coupling score between file i and file j; `0.0` if no pair exists
- Color scale: 0.0 = white, 0–0.3 = light green, 0.3–0.7 = yellow, 0.7–1.0 = red
- Hover tooltip: `"{file_a} ↔ {file_b}: score={score:.2f} ({co_changes} co-changes)"`
- Rendered via D3.js `scaleBand` + `scaleSequential` in the HTML template

### 5. Force Graph Generation
- Nodes: all files appearing in any pair in `RepoAnalysis.pairs` (not limited to top-N)
- Node size: proportional to file's total commit count (`file_commit_count[file]`) — min 5px radius, max 25px radius, scaled linearly
- Node color: file's maximum coupling score across all pairs → same risk color scale (🟢/🟡/🔴)
- Edges: one edge per `CouplingPair`
- Edge thickness: `score * 8` pixels (min 0.5px, max 8px)
- Edge color: score > 0.7 → `#ef4444` (red); else → `#94a3b8` (slate)
- D3 force simulation: `d3.forceSimulation()` with `d3.forceManyBody()`, `d3.forceLink()`, `d3.forceCenter()`
- Drag to reposition nodes; hover tooltip shows pair score and co-change count
- Rendered via D3.js in SVG within the HTML template

### 6. Two-Tab HTML Report
- Single self-contained `index.html` file
- Tab 1 "Heatmap" (default active): D3 coupling heatmap + summary stats (total pairs, max score, total files analyzed)
- Tab 2 "Force Graph": D3 force graph
- Tab 3 "Table": sortable HTML table of top `--top-files` pairs (columns: File A, File B, Score, Risk, Co-changes)
- Report title: derived from `RepoAnalysis.repo_name` → `"ChurnMap — {repo_name}"`
- Footer: `Generated by churnmap v{version} on {date}`
- D3.js loaded from CDN: `https://cdn.jsdelivr.net/npm/d3@7/dist/d3.min.js`
- No external CSS framework — inline styles only, keeping the report self-contained
- Tab switching via pure JavaScript (no framework)
- Table sorted by score descending (static, no interactive sort in v1)

### 7. JSON Report
- Written to `{output_dir}/report.json`
- Format:
```json
{
  "meta": {
    "repo": "Meru143/couplingguard",
    "generated_at": "2026-05-27",
    "lookback_days": 90,
    "total_commits_analyzed": 342,
    "churnmap_version": "1.0.0"
  },
  "pairs": [
    {
      "file_a": "src/payment.py",
      "file_b": "src/billing.py",
      "score": 0.82,
      "co_changes": 41,
      "total_commits": 50,
      "risk": "high"
    }
  ]
}
```
- `pairs` list is sorted by score descending, not truncated (all pairs above `min_occurrences`)
- Written with `json.dumps(data, indent=2)`

### 8. Output and Path Handling
- Create `{output_dir}/` if it does not exist (no error if it already exists)
- Print on success: `Report generated: {output_dir}/index.html` (HTML) and/or `Report generated: {output_dir}/report.json` (JSON)
- If `--open`: call `webbrowser.open(str(output_dir / "index.html"))` after writing
- All print output via `rich.print` or `typer.echo` — never raw `print()`

### 9. Safety Features
- Shallow clone detection: `coupling-core` raises `ShallowCloneError` → print error message with fix instructions, exit 1
- No git history in lookback window: print informational message "No commits found in the last N days. Try increasing --lookback-days.", exit 0 (not an error)
- Invalid repo path: print "Not a git repository: {path}", exit 1
- Invalid YAML config: print "Error in .churnmap.yml: {yaml_error}", exit 1
- Output dir creation failure (permissions): print "Cannot create output directory: {path}: {error}", exit 1
- `--heatmap-limit` > total unique files: silently clamp to total unique files, no warning

### 10. Shell Completions
- `typer` auto-generates completions for bash, zsh, fish, PowerShell via `--install-completion` and `--show-completion` flags
- No additional implementation required — Typer handles this

---

## Section 7 — Interface Spec

### CLI Command

```bash
# Minimal (analyze current directory)
churnmap

# Full options
churnmap \
  --repo /path/to/repo \
  --output-dir ./my-report \
  --lookback-days 180 \
  --min-occurrences 5 \
  --heatmap-limit 30 \
  --top-files 50 \
  --format html \
  --exclude "docs/**" \
  --exclude "*.md" \
  --exclude "migrations/**" \
  --low-threshold 0.25 \
  --high-threshold 0.65 \
  --open

# Version
churnmap --version

# Help (auto-generated by Typer)
churnmap --help
```

### CLI Flags Table

| Flag | Type | Default | Description |
|------|------|---------|-------------|
| `--repo` | `Path` | `.` | Path to git repository root |
| `--output-dir` | `Path` | `./coupling-report` | Output directory for report files |
| `--lookback-days` | `int` | `90` | Days of git history to analyze |
| `--min-occurrences` | `int` | `3` | Minimum co-change count to include a pair |
| `--heatmap-limit` | `int` | `50` | Max files in heatmap (top by max coupling score) |
| `--top-files` | `int` | `100` | Max pairs in HTML table |
| `--format` | `str` | `both` | Output format: `both`, `html`, `json` |
| `--exclude` | `list[str]` | `[]` | Glob patterns to exclude (repeatable) |
| `--low-threshold` | `float` | `0.3` | Score below this is Low |
| `--high-threshold` | `float` | `0.7` | Score above this is High |
| `--open` | `bool` | `False` | Open HTML report in browser after generation |
| `--version` | flag | — | Print version and exit |

### Config File (`.churnmap.yml`)

```yaml
lookback_days: 90
min_occurrences: 3
heatmap_limit: 50
top_files: 100
format: both
low_threshold: 0.3
high_threshold: 0.7
open: false
exclude:
  - "docs/**"
  - "*.md"
  - "migrations/**"
```

### Output Files

```
coupling-report/
├── index.html    # Self-contained two-tab HTML report (D3 heatmap + force graph + table)
└── report.json   # Machine-readable JSON with meta + pairs envelope
```

---

## Section 8 — Data Flow Diagram

```
┌──────────────────────────────────────────────────────────────────────┐
│                        churnmap CLI                                   │
│                                                                       │
│  ┌──────────────────────┐   ┌───────────────────────────────────┐    │
│  │  ConfigLoader         │   │  .churnmap.yml (optional)         │    │
│  │  merge(               │◀──│  repo root                        │    │
│  │    cli_flags,         │   └───────────────────────────────────┘    │
│  │    yaml_file,         │                                            │
│  │    defaults           │                                            │
│  │  )                    │                                            │
│  └──────────┬────────────┘                                            │
│             │ Config                                                  │
│             ▼                                                         │
│  ┌──────────────────────────────────────────────────────────────┐    │
│  │  coupling_core.analyze_repo(repo_path, config)                │    │
│  │                                                               │    │
│  │  ├─ open_repo() → shallow clone check                         │    │
│  │  ├─ get_commits() → exclude, binary filter, rename            │    │
│  │  ├─ build_normalized_matrix() → co-change + normalize         │    │
│  │  └─ returns RepoAnalysis(pairs, total_commits, repo_name)     │    │
│  └──────────┬─────────────────────────────────────────────────┬─┘    │
│             │ RepoAnalysis                  rich Progress Bar  │      │
│             ▼                                                  │      │
│  ┌──────────────────────────────────────────┐                  │      │
│  │  DataPreparer                             │                  │      │
│  │  ├─ top_files_for_heatmap(pairs,          │                  │      │
│  │  │    heatmap_limit)                      │                  │      │
│  │  ├─ build_heatmap_matrix(files, pairs)    │                  │      │
│  │  ├─ pairs[:top_files] for table           │                  │      │
│  │  └─ all pairs for JSON                    │                  │      │
│  └──────────┬─────────────────────────────┬─┘                  │      │
│             │ heatmap_data                │ pairs_data          │      │
│             ▼                             ▼                     │      │
│  ┌─────────────────────┐   ┌─────────────────────────────┐     │      │
│  │  HtmlRenderer        │   │  JsonWriter                  │     │      │
│  │                      │   │                              │     │      │
│  │  Jinja2.render(      │   │  json.dumps({                │     │      │
│  │    template,         │   │    "meta": {...},            │     │      │
│  │    heatmap_data,     │   │    "pairs": [...]            │     │      │
│  │    force_data,       │   │  })                          │     │      │
│  │    table_data,       │   │                              │     │      │
│  │    meta              │   │  → report.json               │     │      │
│  │  )                   │   └─────────────────────────────┘     │      │
│  │  → index.html        │                                        │      │
│  └─────────────────────┘                                        │      │
│             │                                                    │      │
│             ▼                                                    │      │
│  ┌──────────────────────────────────────────┐                   │      │
│  │  OutputWriter                             │                   │      │
│  │  ├─ mkdir(output_dir, exist_ok=True)      │                   │      │
│  │  ├─ write index.html                      │                   │      │
│  │  ├─ write report.json                     │                   │      │
│  │  ├─ print paths to stdout                 │                   │      │
│  │  └─ webbrowser.open() if --open           │                   │      │
│  └──────────────────────────────────────────┘                   │      │
└─────────────────────────────────────────────────────────────────┘      │
                                                                  ───────┘
```

---

## Section 9 — Architecture / Package Structure

```
churnmap/
├── action.yml                    # NOT present — churnmap is a CLI, not a GitHub Action
├── pyproject.toml                # Package metadata, deps, ruff/mypy/typer config
├── README.md
├── CHANGELOG.md
├── LICENSE
├── .churnmap.yml                 # Example config for churnmap's own repo (dogfooding)
├── .github/
│   └── workflows/
│       ├── ci.yml
│       └── release.yml
├── src/
│   └── churnmap/
│       ├── __init__.py           # __version__ = "1.0.0"
│       ├── main.py               # typer app, CLI entrypoint — `def app()`
│       ├── config.py             # ConfigLoader: merge CLI flags + YAML + defaults
│       ├── data_preparer.py      # DataPreparer: heatmap matrix, force graph data, table data
│       ├── html_renderer.py      # HtmlRenderer: Jinja2 template rendering
│       ├── json_writer.py        # JsonWriter: build and write report.json
│       ├── output_writer.py      # OutputWriter: mkdir, write files, open browser
│       └── templates/
│           └── report.html.j2    # Jinja2 HTML template with embedded D3.js
└── tests/
    ├── conftest.py               # Fixtures: fake_repo, sample_pairs, sample_config
    ├── test_config.py
    ├── test_data_preparer.py
    ├── test_html_renderer.py
    ├── test_json_writer.py
    └── test_output_writer.py
```

### Key Types

```python
# config.py
@dataclass
class ChurnmapConfig:
    repo: Path = Path(".")
    output_dir: Path = Path("./coupling-report")
    lookback_days: int = 90
    min_occurrences: int = 3
    heatmap_limit: int = 50
    top_files: int = 100
    format: str = "both"          # "both" | "html" | "json"
    exclude: list[str] = field(default_factory=list)
    low_threshold: float = 0.3
    high_threshold: float = 0.7
    open_browser: bool = False

# data_preparer.py
@dataclass
class HeatmapData:
    files: list[str]              # ordered list of top-N files
    matrix: list[list[float]]     # NxN score matrix, 0.0 if no pair
    file_commit_counts: dict[str, int]

@dataclass
class ForceGraphData:
    nodes: list[dict]             # [{"id": "src/payment.py", "churn": 50, "max_score": 0.82, "risk": "high"}]
    links: list[dict]             # [{"source": "src/payment.py", "target": "src/billing.py", "score": 0.82}]

@dataclass
class ReportData:
    heatmap: HeatmapData
    force_graph: ForceGraphData
    table_pairs: list[CouplingPair]  # top top_files pairs
    repo_name: str
    generated_at: str
    total_commits_analyzed: int
    lookback_days: int
    churnmap_version: str
```

---

## Section 10 — Error Handling

| Code | Scenario | User-facing message | Action |
|------|----------|--------------------|-|
| `E001` | Path is not a git repo | `Error: Not a git repository: {path}` | Exit 1 |
| `E002` | Shallow clone | `Error: Repository is a shallow clone. Add 'fetch-depth: 0' to your checkout step, or run: git fetch --unshallow` | Exit 1 |
| `E003` | No commits in lookback window | `No commits found in the last {N} days. Try increasing --lookback-days.` | Exit 0 |
| `E004` | Invalid `.churnmap.yml` | `Error in .churnmap.yml: {yaml_error}` | Exit 1 |
| `E005` | Cannot create output dir | `Cannot create output directory: {path}: {os_error}` | Exit 1 |
| `E006` | Write permission denied on output file | `Cannot write {filename}: permission denied` | Exit 1 |
| `E007` | `--heatmap-limit` > unique files (silent) | (none — silently clamp) | Continue |
| `E008` | No pairs found after filtering | `No coupling pairs found. Try decreasing --min-occurrences or increasing --lookback-days.` | Exit 0 |

---

## Section 11 — Edge Cases

1. **Empty repo** — zero commits: `analyze_repo` returns `RepoAnalysis(pairs=[], total_commits_analyzed=0, ...)`. churnmap prints E003 and exits 0.
2. **All pairs filtered by `min_occurrences`** — matrix is non-empty but no pairs survive the filter: E008.
3. **Repo with only binary files** — all files filtered by coupling-core: E008.
4. **`--heatmap-limit` larger than unique files** — clamp to actual unique file count. HTML renders an NxN where N < heatmap_limit.
5. **`--top-files` larger than pair count** — table shows all pairs. No truncation message.
6. **Jinja2 template missing from package** — `PackageLoader` raises `TemplateNotFound`. Catch it, print "Internal error: report template not found — please reinstall churnmap", exit 1.
7. **D3.js CDN unavailable** — report renders with broken visualizations. Informational comment in HTML: `<!-- D3.js loaded from CDN. Report requires internet to render visualizations. -->`. No offline fallback in v1.
8. **`--open` on headless server** — `webbrowser.open()` silently fails (returns False). Print "Note: Could not open browser automatically. Open manually: {path}" and continue.
9. **Repo with 100k+ commits and 90-day lookback** — coupling-core handles this via `since=` filter in GitPython. The 90-day window is the ceiling; performance is bounded by commits in that window, not total history.
10. **Windows path separators** — `Path.as_posix()` must be used when passing file paths to Jinja2 template as JavaScript string literals (D3 node IDs cannot contain backslashes).
11. **Files with spaces in path** — D3 uses string IDs; spaces in node IDs are valid JSON strings. No special handling needed beyond correct JSON serialization.
12. **Circular coupling** — file A and file B always change together AND both change with file C. Force graph handles this naturally. Heatmap shows all three cells. No special handling needed.

---

## Section 12 — Testing Strategy

### Unit Tests
- **config.py** — YAML loading, CLI override precedence, defaults, invalid YAML
- **data_preparer.py** — heatmap matrix construction (correct scores at correct indices), top-N file selection, force graph node/link generation, table truncation
- **html_renderer.py** — Jinja2 renders without error for known input; output contains D3 CDN script tag; output contains tab switcher; title contains repo name
- **json_writer.py** — output matches expected schema; `meta.repo` correct; `pairs` sorted by score desc; `json.dumps` produces valid JSON

### Mocking Approach
- Mock `coupling_core.analyze_repo` with a fixed `RepoAnalysis` fixture — no real git repo needed for unit tests of churnmap itself
- Use `tmp_path` pytest fixture for output directory tests
- Mock `webbrowser.open` to verify it's called with the correct path when `--open` is set

---

## Section 13 — Distribution

```bash
# Build
python -m build

# Install (end users)
pip install churnmap

# Install with uv (recommended)
uv tool install churnmap

# Source install
git clone https://github.com/Meru143/churnmap
cd churnmap
pip install -e ".[dev]"
```

### Release Pipeline
- `python-semantic-release` reads Conventional Commits, bumps version in `pyproject.toml`
- GitHub Actions release workflow: push to main → semantic-release → PyPI via Trusted Publishing

---

## Section 14 — Differentiators

1. **vs CodeScene** — Free, OSS, local, no external service. CodeScene: $1k+/month, proprietary, cloud-required.
2. **vs code-maat** — code-maat: Java CLI, 2016, unmaintained, no visualization, no normalization. churnmap: Python 3.11, maintained, two-tab D3 report, normalized scoring.
3. **vs couplingguard** — couplingguard: PR-time warning as a GitHub Action. churnmap: full-repo audit as a local CLI. Complementary tools sharing coupling-core.
4. **vs GitClear / CodeClimate** — Paid hosted services. churnmap: local, free, no signup.

---

## Section 15 — Future Scope (v2+)

- [ ] `--offline` flag: bundle D3.js into the HTML output (no CDN dependency)
- [ ] Interactive table sort in HTML (click column headers)
- [ ] `--since` / `--until` date range flags (in addition to `--lookback-days`)
- [ ] Directory-level aggregation: collapse file pairs into module/package pairs
- [ ] Trend mode: compare coupling between two date ranges
- [ ] Hosted churnmap.io: upload JSON report, share report URL
- [ ] VS Code extension: run churnmap on current workspace and show inline coupling annotations
- [ ] `--watch` flag: re-run analysis on new commits

---

## Section 16 — Success Metrics

- [ ] `churnmap` command completes in < 15s for a repo with 90 days of history and < 10k commits
- [ ] HTML report renders without errors in Chrome, Firefox, Safari (latest)
- [ ] JSON output validates against the documented schema
- [ ] Unit test coverage ≥ 85%
- [ ] `mypy src/ --strict` passes with zero errors
- [ ] `ruff check src/` passes with zero errors
- [ ] Runs on Python 3.11, 3.12, 3.13
- [ ] Runs on ubuntu-latest, macos-latest, windows-latest

---

## Section 17 — Additional Deliverables

### Documentation Files
- [ ] `README.md` — install snippet, usage examples, screenshot of HTML report, flags table
- [ ] `CONTRIBUTING.md` — local dev setup, test commands, commit convention
- [ ] `CODE_OF_CONDUCT.md` — Contributor Covenant 2.1
- [ ] `SECURITY.md` — vulnerability disclosure email
- [ ] `.github/ISSUE_TEMPLATE/bug_report.md`
- [ ] `.github/ISSUE_TEMPLATE/feature_request.md`
- [ ] `.github/PULL_REQUEST_TEMPLATE.md`

### Development Environment
- [ ] `.env.example` — `COUPLINGGUARD_DEBUG=0` (no secrets needed for churnmap)
- [ ] `devcontainer/devcontainer.json` — Python 3.11, ruff, mypy, pytest
- [ ] `.editorconfig` — indent 4 spaces, LF line endings
- [ ] `Makefile` targets: `lint`, `type-check`, `test`, `build`, `dev`, `demo`

### `make demo` Target
- [ ] `make demo` runs `churnmap --repo . --output-dir /tmp/churnmap-demo --open`
- [ ] Dogfoods churnmap against its own repo — the demo screenshot in the README is generated this way

### Logging & Observability
- [ ] All print/echo output via `rich.print` or `typer.echo`
- [ ] `CHURNMAP_DEBUG=1` env var: enable verbose logging of config, pair count, matrix size
- [ ] Log levels: DEBUG (matrix stats), INFO (progress, output paths), ERROR (fatal)

### Environment Variables
| Variable | Purpose | Default |
|----------|---------|---------|
| `CHURNMAP_DEBUG` | Enable debug logging | `0` |

---

## Section 18 — Expanded Testing Strategy

### Unit Tests (target: 85% coverage)

#### test_config.py
- [ ] Valid YAML loaded, `lookback_days` set correctly
- [ ] CLI flag `--lookback-days 180` overrides YAML `lookback_days: 90`
- [ ] Missing YAML file → all defaults applied, no error
- [ ] Invalid YAML → `ConfigError` raised with line number
- [ ] Multiple `--exclude` flags merged into list
- [ ] `format` value `"both"` accepted; `"html"`, `"json"` accepted; invalid value → Typer error

#### test_data_preparer.py
- [ ] `top_files_for_heatmap`: returns top N files sorted by max coupling score desc
- [ ] `top_files_for_heatmap`: when fewer unique files than heatmap_limit, returns all
- [ ] `build_heatmap_matrix`: cell `(i,j)` equals score for pair `(files[i], files[j])`
- [ ] `build_heatmap_matrix`: cell `(i,j)` = 0.0 when no pair exists for that file combo
- [ ] `build_force_graph_data`: node `{"id": "src/payment.py", "churn": 50, "max_score": 0.82, "risk": "high"}` correct
- [ ] `build_force_graph_data`: link `{"source": "src/payment.py", "target": "src/billing.py", "score": 0.82}` correct
- [ ] Table pairs: truncated to `top_files` count
- [ ] Windows path separators converted to forward slashes in node IDs

#### test_html_renderer.py
- [ ] Rendered HTML contains `<script src="https://cdn.jsdelivr.net/npm/d3@7/dist/d3.min.js">` tag
- [ ] Rendered HTML contains `ChurnMap — {repo_name}` in `<title>`
- [ ] Rendered HTML contains tab switcher element with "Heatmap", "Force Graph", "Table" tabs
- [ ] Rendered HTML contains `<!-- D3.js loaded from CDN` comment
- [ ] Rendered HTML is valid enough to pass basic `<html>` open/close check
- [ ] Footer contains churnmap version string

#### test_json_writer.py
- [ ] JSON output contains `meta.repo` matching `RepoAnalysis.repo_name`
- [ ] JSON output contains `meta.generated_at` (today's date, ISO format)
- [ ] JSON output `pairs` sorted by `score` descending
- [ ] JSON output `pairs[0]` has keys: `file_a`, `file_b`, `score`, `co_changes`, `total_commits`, `risk`
- [ ] `json.loads(output)` succeeds without exception

#### test_output_writer.py
- [ ] Output dir created when it does not exist
- [ ] Output dir creation with `exist_ok=True` — no error if already exists
- [ ] `index.html` written to output dir when `format="html"` or `format="both"`
- [ ] `report.json` written to output dir when `format="json"` or `format="both"`
- [ ] Neither file written when output dir creation fails (permissions)
- [ ] `webbrowser.open()` called with correct path when `open_browser=True`
- [ ] `webbrowser.open()` NOT called when `open_browser=False`

### Integration Tests

- [ ] `churnmap` CLI invoked via `typer.testing.CliRunner` against a real fake_repo fixture with scripted commits → output dir contains `index.html` and `report.json`
- [ ] `report.json` from CLI run parses correctly and contains expected pairs
- [ ] CLI with `--format html` only → `index.html` exists, `report.json` does NOT exist
- [ ] CLI with `--format json` only → `report.json` exists, `index.html` does NOT exist
- [ ] CLI with `--min-occurrences 99` → no pairs (E008), exit code 0
- [ ] CLI with `--repo /nonexistent` → E001 error message, exit code 1
- [ ] CLI with invalid `.churnmap.yml` → E004 error message, exit code 1

### E2E Tests

- [ ] Full workflow: init fake repo with 10 scripted commits (files A, B co-change 8 times) → run `churnmap` → open `index.html` → parse embedded JSON data → verify pair score matches expected
- [ ] Full workflow: repo with 2 commits, `min_occurrences=3` → E008, exit 0, no output files written

### Test Infrastructure
- [ ] `fake_repo` fixture creates a real git repo via `git.Repo.init(tmp_path)` with configured user
- [ ] `fake_repo` has `commit(files: list[str])` helper
- [ ] `sample_analysis` fixture returns a `RepoAnalysis` with 5 known pairs for unit testing churnmap components
- [ ] All tests use `typer.testing.CliRunner` for CLI invocation (not subprocess)

---

## Section 19 — CI/CD Pipeline

### GitHub Actions — CI

- [ ] Create `.github/workflows/ci.yml`
- [ ] Trigger: `push` to `main`, `pull_request` to `main`
- [ ] Job `lint`: `ruff check src/ tests/`
- [ ] Job `type-check`: `mypy src/ --strict`
- [ ] Job `test`: matrix `python-version: ["3.11","3.12","3.13"]`, `os: ["ubuntu-latest","macos-latest","windows-latest"]`
- [ ] Step in `test`: `pytest tests/ -v --cov=src/churnmap --cov-report=xml`
- [ ] Step: upload coverage to Codecov

### GitHub Actions — Release

- [ ] Create `.github/workflows/release.yml`
- [ ] Trigger: push to `main`
- [ ] Job: `python-semantic-release publish`
- [ ] PyPI Trusted Publishing configured in `[tool.semantic_release]`

### Makefile Targets

- [ ] `make dev`: `pip install -e ".[dev]"`
- [ ] `make lint`: `ruff check src/ tests/`
- [ ] `make type-check`: `mypy src/ --strict`
- [ ] `make test`: `pytest tests/ -v --cov=src/churnmap --cov-report=term-missing`
- [ ] `make build`: `python -m build`
- [ ] `make demo`: `churnmap --repo . --output-dir /tmp/churnmap-demo && open /tmp/churnmap-demo/index.html`

### Security Scanning

- [ ] Add `pip-audit` to CI: `pip-audit --require-hashes -r requirements.txt`
- [ ] Add `dependabot.yml`: `package-ecosystem: pip`, `schedule: weekly`
