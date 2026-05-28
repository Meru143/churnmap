# churnmap demo kit

This directory holds reproducible public demo material for churnmap.

- `generate_sample_report.py` builds a curated sample report with realistic coupling hotspots.
- `sample-report.html` is the interactive D3 report used for screenshots.
- `sample-report.json` is the matching machine-readable output.
- `../assets/` contains rendered assets used by the README.

Regenerate the sample report:

```bash
PYTHONPATH=src python docs/demo/generate_sample_report.py
```

Create the README GIF from the MP4:

```bash
ffmpeg -y -i docs/assets/churnmap-demo.mp4 -vf "fps=12,scale=960:-1:flags=lanczos" docs/assets/churnmap-demo.gif
```

Refresh report screenshots:

```bash
node docs/demo/capture_report_assets.mjs
```
