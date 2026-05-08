# Verse presentation

Custom minimal slide deck for the Master's AI program talk — "Building AI-Driven Applications".

Single-file, vanilla-JS framework. No reveal.js.

## Run

Open directly (file:// works):

```bash
open presentation/index.html
```

Or serve locally (recommended for ES module imports):

```bash
cd presentation && python3 -m http.server 8080
# → http://localhost:8080
```

## Keyboard

- `→` / `Space` / `PageDown` — next
- `←` / `PageUp` — previous
- `Home` / `End` — first / last
- `F` — toggle fullscreen

Also: click right/left half of the screen, or swipe on touch devices.

## Files

- `index.html` — slide content + navigation script
- `theme.css` — visual theme, mirrors `apps/frontend/src/common/styles/variables.scss`
- `embeddings.png` — generated RAG visualization
