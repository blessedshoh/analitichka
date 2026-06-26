# NBU Market Review — Newsletter Generator

Automates the recurring two-page treasury markets PDF newsletter (today
assembled by hand in Canva). **Type the news, click one button, get an
identical PDF with all data and charts populated automatically.**

- **Backend:** Python + FastAPI (all logic). Modular: `fetchers/`,
  `rendering/`, `models/`, `api/`, `assets/`, `config/`.
- **Frontend:** Next.js (React) — a thin form + editable data grids + live PDF
  preview + a Generate button, usable by non-technical staff.
- **Render:** Jinja2 HTML/CSS template → Playwright (headless Chromium)
  `page.pdf()`, A4 landscape, two pages.

---

## Quick start

```bash
cp .env.example .env        # fill in secrets later; works without them
make install                # backend venv + deps + Playwright chromium + npm
make dev                    # backend :8000  +  frontend :3000
```

Open **http://localhost:3000**. The form opens pre-filled with the reference
issue; edit anything, then click **Сгенерировать PDF**.

Docker alternative:

```bash
docker compose up --build   # same two services
```

API docs (FastAPI): http://localhost:8000/docs

---

## How it works

The frontend assembles one reviewed `Newsletter` payload and POSTs it to
`/api/generate`. Nothing is fetched at render time — every value is a **draft
that a human reviews/edits in the UI first**. Each fetcher degrades gracefully
(returns last-known/empty + a flagged warning, never crashes generation).

| Source | Module | Notes |
|---|---|---|
| CBU currency rates | `fetchers/cbu_currency.py` | `cbu.uz` public JSON feed → local FX table (USDUZS…GBPUZS). 1m/6m/12m via historical queries. |
| CBU money market | `fetchers/cbu_money_market.py` | UZONIA / REPO / interbank. No stable feed → **always a manual-confirm grid** (scrape hook left in place). |
| Bloomberg `.xlsx` | `fetchers/bloomberg_excel.py` | Drag-and-drop export. Parsed via `config/bloomberg_map.yaml` (anchor + column offsets — **no hardcoded cells**). |
| Telegram stock photo | `fetchers/telegram_stocks.py` | Telethon (MTProto) downloads the latest image → Claude (`claude-sonnet-4-6`) extracts strict JSON → `change_pct` **recomputed server-side**; mismatched rows **flagged & highlighted**. |
| Telegram news | `fetchers/telegram_news.py` | Extension hook (stub) to pre-fill news drafts. |

Charts (`rendering/charts.py`, matplotlib) are re-plotted each issue from the
same series the tables use: system-liquidity (red line), CB liquidity
operations (green area), VIX, EMBI — embedded as data-URIs.

---

## Pixel-match & fonts

The template targets the Canva reference exactly: **A3 landscape (420×297mm)**,
two pages, with the reference's own typefaces embedded as `@font-face`
data-URIs (so output is identical on any machine, no system fonts needed):

| Element | Font | Source |
|---|---|---|
| ОБЗОР РЫНКА title, section headers | **Bebas Neue** | exact glyphs extracted from the reference PDF (`assets/fonts/bebas-ref.woff2`) |
| Table data | **Times New Roman** → **Tinos** (metric-compatible) | bundled |
| Captions / news headlines | **Lora** | bundled |
| Labels, column heads, body | **Noto Sans** | bundled |
| `*TSMI` footnote | **Open Sans Italic** | bundled |

Point sizes and the gold date colour (`#c0955d`) were measured from the
reference. The bundled fonts live in `backend/assets/fonts/` (committed);
`app/rendering/fonts.py` inlines them. To refresh/extend them, install the
`@fontsource/*` npm packages and copy the `cyrillic`/`latin` woff2 subsets.

## Brand / design tokens

- **Gold accent** lives in exactly one place: `ACCENT_GOLD` (default
  `#f4e7d4`). The backend exposes it at `/api/config`; the template injects it
  as the single CSS variable `--accent-gold`; the frontend mirrors it. Change
  it once.
- **Background asset** (`assets/background.png`) is referenced by **path** so
  you can swap in the transparent PNG without code changes. Placement is one
  switch: `BACKGROUND_PLACEMENT = watermark | cover | header | none`.
  > The extracted placeholder is opaque; drop your transparent PNG at the same
  > path (or point `BACKGROUND_ASSET` elsewhere) and it's used as-is.
- `assets/nbu_logo.png` — the NBU masthead logo.

---

## Configuration & secrets

All in env vars / config files, never hardcoded — see **`.env.example`**.
Telegram `api_id`/`api_hash`, the Anthropic key, the Bloomberg column map and
the background-asset path are all configurable. The app runs without any
secrets (live fetchers simply fall back to manual entry).

The Bloomberg layout is data, not code: edit `config/bloomberg_map.yaml` when
the export changes.

---

## Project layout

```
backend/
  app/
    models/        pydantic schemas (one per source + the Newsletter)
    fetchers/      one independent module per data source
    rendering/     charts.py, pdf.py, templates/newsletter.html.j2
    api/           FastAPI routes
    core/          config (settings), cache (last-known-good)
    sample_data.py reference-issue payload (pre-fills the form)
  assets/          background.png, nbu_logo.png
  config/          bloomberg_map.yaml
  tests/
frontend/
  app/             Next.js App Router page + layout
  components/       EditableGrid, FileDrop, MetaBadge
  lib/api.ts       typed backend client
```

---

## Tests

```bash
make test          # backend unit tests (parsing, validation, render)
```

## Notes & constraints

- Multilingual content (RU / UZ Latin & Cyrillic / EN) — the template font
  stack and all parsing handle Cyrillic.
- Treat every extracted/fetched value as a draft requiring human review,
  especially the published financial tables.
- `make install` runs `playwright install chromium`. On hosts that ship a
  pre-installed Chromium, set `PLAYWRIGHT_EXECUTABLE_PATH` to its binary.

## Build status

Steps 1–7 of the planned build order are implemented (scaffold + template,
CBU JSON fetcher, Bloomberg parser, charts, PDF render endpoint, money-market
manual fallback, Telegram + Claude extraction, and the Next.js UI). Step 8
(morning auto-refresh scheduler) is intentionally left as the optional last
step.
