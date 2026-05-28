.PHONY: dev lint type-check test build demo demo-assets clean

dev:
	pip install -e ".[dev]"

lint:
	ruff check src/ tests/

type-check:
	mypy src/ --strict

test:
	pytest tests/ -v --cov=src/churnmap --cov-report=term-missing

build:
	python -m build

demo:
	churnmap --repo . --output-dir /tmp/churnmap-demo --min-occurrences 1 --open

demo-assets:
	PYTHONPATH=src python docs/demo/generate_sample_report.py
	node docs/demo/capture_report_assets.mjs
	cd docs/frames/churnmap-demo && npm run check
	cd docs/frames/churnmap-demo && npx --yes hyperframes@0.6.52 render --quality standard --output ../../assets/churnmap-demo.mp4
	ffmpeg -y -i docs/assets/churnmap-demo.mp4 -vf "fps=12,scale=960:-1:flags=lanczos,split[s0][s1];[s0]palettegen=max_colors=128[p];[s1][p]paletteuse=dither=bayer:bayer_scale=3" docs/assets/churnmap-demo.gif
	ffmpeg -y -ss 4.8 -i docs/assets/churnmap-demo.mp4 -frames:v 1 -vf "scale=1280:-1:flags=lanczos" docs/assets/churnmap-demo-poster.png

clean:
	rm -rf dist/ build/ *.egg-info/ src/*.egg-info/ .pytest_cache/ .mypy_cache/ .ruff_cache/ .coverage coverage.xml htmlcov/
