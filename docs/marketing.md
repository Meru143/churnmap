# churnmap positioning kit

## One-liner

churnmap is a local CLI that turns git co-change history into an interactive coupling heatmap, force graph, and JSON report.

## Primary audience

- Tech leads preparing refactors.
- Platform engineers auditing risky ownership boundaries.
- Staff engineers explaining why two files should move or split together.
- Maintainers who want CodeScene-style coupling signal without a hosted service.

## Core message

Before you rewrite, split, or migrate a system, find the files that already behave as one unit. churnmap makes that coupling visible from git history, then leaves behind static artifacts the team can inspect, share, and automate against.

## Proof points

- One command creates `index.html` and `report.json`.
- The HTML report has Heatmap, Force Graph, and Table views.
- No token, signup, SaaS dashboard, or repository upload.
- JSON output is sorted by coupling score and ready for scripts.
- The package is on PyPI as `churnmap`.

## Copy blocks

### Homepage hero

**Headline:** Run the coupling map before the rewrite.

**Subheadline:** churnmap analyzes git co-change history and generates an interactive D3 heatmap, force graph, and JSON report from any local repository.

**CTA:** Install churnmap

### Short launch post

Refactors usually start with opinions about where the risky boundaries are. churnmap gives you evidence first.

Run `churnmap` in a git repo and it writes a static interactive report plus JSON output showing which files repeatedly change together. It is local, open source, and built for quick architecture audits before a migration or cleanup.

### Maintainer pitch

If two files keep changing in the same commits, they are probably coupled in practice, whether the architecture diagram admits it or not. churnmap turns that signal into a report you can open, share, and automate against.

## Demo narrative

1. Start with the pain: teams plan refactors from memory and code search.
2. Show the command: `churnmap --repo . --open`.
3. Reveal the heatmap: red blocks expose repeated co-change hotspots.
4. Move to the pair list: the highest-risk file pairs become review targets.
5. Close with the artifact: HTML for humans, JSON for automation.

## Suggested channels

- GitHub README and release assets.
- PyPI project description.
- Product Hunt or Hacker News launch post.
- Engineering blog post: "Use git history to scope your next refactor."
- Short MP4/GIF on LinkedIn, X, and README hero.
