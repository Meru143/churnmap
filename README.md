![PyPI](https://img.shields.io/pypi/v/churnmap)
![CI](https://github.com/Meru143/churnmap/actions/workflows/ci.yml/badge.svg?branch=main)
![License](https://img.shields.io/badge/license-MIT-blue.svg)

# churnmap

> Coupling heatmap generator — visualize co-change risk in any git repo.

churnmap is a dead-simple CLI that analyzes any git repository's co-change history and generates a two-tab interactive HTML report — a coupling heatmap and a D3 force graph — plus a machine-readable JSON file. It is the open-source CodeScene replacement for local, ad-hoc coupling audits.

One command, two files. No signup, no external service, no Kubernetes.

## Install

```bash
pip install churnmap
```

Or with [uv](https://github.com/astral-sh/uv):

```bash
uv tool install churnmap
```

## Usage

```bash
# Analyze the current directory
churnmap

# Analyze a specific repo with custom settings
churnmap \
  --repo /path/to/repo \
  --output-dir ./my-report \
  --lookback-days 180 \
  --min-occurrences 5 \
  --heatmap-limit 30 \
  --format both \
  --open
```

Output is written to `./coupling-report/`:

```
coupling-report/
├── index.html    # Two-tab interactive report (Heatmap + Force Graph + Table)
└── report.json   # Machine-readable JSON with meta + pairs envelope
```

## Flags

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
| `--low-threshold` | `float` | `0.3` | Score below this is 🟢 Low |
| `--high-threshold` | `float` | `0.7` | Score above this is 🔴 High |
| `--open` | `bool` | `False` | Open HTML report in browser after generation |
| `--version` | flag | — | Print version and exit |

## Output

- **`index.html`** — self-contained, three-tab D3-powered report. Heatmap tab shows top-N files by max coupling score with color-coded cells. Force Graph tab shows file relationships with node size = churn and edge thickness = coupling score. Table tab lists top pairs.
- **`report.json`** — envelope with `meta` (repo name, generation date, lookback days, total commits analyzed, churnmap version) and `pairs` (all coupling pairs above `min_occurrences`, sorted by score descending).

## Config file

Drop a `.churnmap.yml` in your repo root to set defaults:

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

CLI flags override config file values.

## How it works

1. **`coupling-core`** parses the git history, builds a co-change matrix, normalizes scores into the 0–1 range, and returns a `RepoAnalysis`.
2. **`DataPreparer`** turns the analysis into a heatmap matrix, force-graph nodes/links, and a table-pairs list.
3. **`HtmlRenderer`** renders a Jinja2 template containing embedded JSON data and D3.js (loaded from CDN).
4. **`JsonWriter`** emits the machine-readable envelope.
5. **`OutputWriter`** creates the output directory and writes both files.

## Report screenshot

```
┌──────────────────────────────────────────────────────────────┐
│  ChurnMap — Meru143/churnmap                                  │
│  Total pairs: 42  •  Max score: 0.91  •  Commits: 342         │
│                                                                │
│  [ Heatmap ]  [ Force Graph ]  [ Table ]                       │
│  ─────────                                                     │
│                                                                │
│       src/  src/  src/  ...                                    │
│       a.py  b.py  c.py                                         │
│  a.py  ▓▓   ░░    ▒▒                                           │
│  b.py  ░░   ▓▓    ▓▓                                           │
│  c.py  ▒▒   ▓▓    ▓▓                                           │
│                                                                │
└──────────────────────────────────────────────────────────────┘
```

## Used alongside

- [couplingguard](https://github.com/Meru143/couplingguard) — PR-time coupling warning as a GitHub Action. Same `coupling-core` engine, complementary surface.

## License

[MIT](LICENSE)
