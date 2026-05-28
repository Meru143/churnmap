# Contributing to churnmap

Thanks for considering a contribution. This project is intentionally small — a focused CLI on top of `coupling-core` — so most contributions are tightly scoped.

## Local setup

```bash
git clone https://github.com/Meru143/churnmap
cd churnmap
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
make dev                    # pip install -e ".[dev]"
```

## Run the test suite

```bash
make test          # pytest with coverage
make lint          # ruff check
make type-check    # mypy --strict
```

Equivalent direct commands (for systems without `make`):

```bash
pytest tests/ -v --cov=src/churnmap --cov-report=term-missing
ruff check src/ tests/
mypy src/ --strict
```

All three must pass before a PR is merged.

## Commit style

Commits follow [Conventional Commits](https://www.conventionalcommits.org/):

```
feat:     new feature or behavior
fix:      bug fix
test:     test additions or changes
docs:     documentation only
refactor: restructuring without behavior change
chore:    tooling, config, dependencies
```

Use the imperative mood (`feat: add --watch flag`, not `feat: added --watch flag`).

## What we accept

- Bug fixes with a regression test.
- Documentation improvements.
- New features that fit the v1 scope outlined in the README. For larger ideas (offline D3, hosted report sharing, interactive table sort), open an issue first.

## What we don't accept

- Changes that depend on a paid service.
- Bundling third-party JS into the HTML output beyond D3.js.
- Anything that breaks the no-network-required local CLI guarantee.
