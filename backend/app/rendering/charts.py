"""Server-side chart rendering (matplotlib, headless 'Agg').

Re-plotted each issue from the same time-series the tables use, styled to
the newsletter palette. Matches the reference PDF:

  * system-liquidity     -> red line
  * CB liquidity ops      -> green filled area
  * VIX                   -> volatility line
  * EMBI                  -> emerging-market spread line

Each function returns a `data:image/png;base64,...` URI so charts embed
directly into the HTML template with no temp files.
"""

from __future__ import annotations

import base64
import io
from typing import Optional

import matplotlib

matplotlib.use("Agg")  # headless: no display needed
import matplotlib.dates as mdates  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.ticker import FuncFormatter  # noqa: E402

from app.core.config import get_settings
from app.models.timeseries import ChartSet, TimeSeries

# Palette
_RED = "#c0392b"
_GREEN = "#27ae60"
_GRID = "#d8cfbe"
_TEXT = "#5b5345"


def _parse_dates(series: TimeSeries):
    """Return matplotlib-friendly x. Falls back to index if dates unparsable."""
    import datetime as _dt

    parsed = []
    ok = True
    for d in series.dates:
        val = None
        for fmt in ("%d.%m.%Y", "%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y"):
            try:
                val = _dt.datetime.strptime(str(d), fmt)
                break
            except (ValueError, TypeError):
                continue
        if val is None:
            ok = False
            break
        parsed.append(val)
    if ok and parsed:
        return parsed, True
    return list(range(len(series.values))), False


def _clean(series: TimeSeries):
    xs, is_dates = _parse_dates(series)
    ys = [v for v in series.values]
    # Drop trailing None alignment issues by zipping to the shorter length.
    n = min(len(xs), len(ys))
    return xs[:n], ys[:n], is_dates


def _style_axes(ax, is_dates: bool):
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    for s in ("left", "bottom"):
        ax.spines[s].set_color(_GRID)
    ax.tick_params(colors=_TEXT, labelsize=7)
    ax.grid(True, color=_GRID, linewidth=0.5, alpha=0.7)
    ax.set_facecolor("none")
    if is_dates:
        ax.xaxis.set_major_locator(mdates.AutoDateLocator())
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %y"))


def _fig_to_uri(fig) -> str:
    buf = io.BytesIO()
    fig.savefig(
        buf, format="png", dpi=150, bbox_inches="tight",
        transparent=True, pad_inches=0.05,
    )
    plt.close(fig)
    buf.seek(0)
    b64 = base64.b64encode(buf.read()).decode("ascii")
    return f"data:image/png;base64,{b64}"


def _empty_uri(label: str) -> str:
    fig, ax = plt.subplots(figsize=(4.2, 1.7))
    ax.text(0.5, 0.5, f"{label}\n(нет данных)", ha="center", va="center",
            color=_TEXT, fontsize=8)
    ax.axis("off")
    return _fig_to_uri(fig)


def line_chart(series: TimeSeries, color: str, title: str = "") -> str:
    xs, ys, is_dates = _clean(series)
    if not any(v is not None for v in ys):
        return _empty_uri(title or series.name)
    fig, ax = plt.subplots(figsize=(4.4, 1.8))
    ax.plot(xs, ys, color=color, linewidth=1.1)
    _style_axes(ax, is_dates)
    if title:
        ax.set_title(title, color=_TEXT, fontsize=8, loc="left")
    return _fig_to_uri(fig)


def area_chart(series: TimeSeries, color: str, title: str = "") -> str:
    xs, ys, is_dates = _clean(series)
    if not any(v is not None for v in ys):
        return _empty_uri(title or series.name)
    fig, ax = plt.subplots(figsize=(4.4, 1.8))
    ax.fill_between(xs, ys, color=color, alpha=0.45, linewidth=0)
    ax.plot(xs, ys, color=color, linewidth=1.0)
    ax.yaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{v:,.0f}"))
    _style_axes(ax, is_dates)
    if title:
        ax.set_title(title, color=_TEXT, fontsize=8, loc="left")
    return _fig_to_uri(fig)


def render_all(charts: ChartSet) -> dict[str, str]:
    """Render every page-2 chart and return {slot: data-uri}."""
    return {
        "system_liquidity": line_chart(
            charts.system_liquidity, _RED, "Общая ликвидность (итог корр. счетов в ЦБ)"
        ),
        "cb_operations": area_chart(
            charts.cb_operations, _GREEN, "Операции ЦБ по привлечению ликвидности"
        ),
        "vix": line_chart(charts.vix, get_settings().accent_gold and "#8a7f6a", "VIX"),
        "embi": line_chart(charts.embi, _RED, "EMBI"),
    }
