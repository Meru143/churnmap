# churnmap demo kit

This directory holds reproducible marketing and documentation demo material for churnmap.

- `generate_sample_report.py` builds a curated sample report with realistic coupling hotspots.
- `sample-report.html` is the interactive D3 report used for screenshots.
- `sample-report.json` is the matching machine-readable output.
- `../frames/churnmap-demo/` is the HyperFrames source for the product video.
- `../assets/` contains rendered assets used by the README.

Regenerate the sample report:

```bash
PYTHONPATH=src python docs/demo/generate_sample_report.py
```

Render the HyperFrames product video:

```bash
cd docs/frames/churnmap-demo
npm run check
npx --yes hyperframes@0.6.52 render --quality standard --output ../../assets/churnmap-demo.mp4
```

Create the README GIF from the MP4:

```bash
ffmpeg -y -i docs/assets/churnmap-demo.mp4 -vf "fps=12,scale=960:-1:flags=lanczos" docs/assets/churnmap-demo.gif
```

Refresh report screenshots:

```bash
node docs/demo/capture_report_assets.mjs
```
