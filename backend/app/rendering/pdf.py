"""HTML -> PDF rendering via Jinja2 + Playwright (headless Chromium).

`render_html` fills the template (charts embedded as data-URIs, assets inlined
so Chromium needs no file access). `render_pdf` prints it to A4 landscape.
"""

from __future__ import annotations

import base64
import mimetypes
from pathlib import Path
from typing import Optional

from jinja2 import Environment, FileSystemLoader, select_autoescape

from app.core.config import get_settings
from app.models.newsletter import Newsletter
from app.rendering import charts as charts_mod
from app.rendering.fonts import font_face_css

_TEMPLATE_DIR = Path(__file__).parent / "templates"


def _asset_data_uri(path: str | Path) -> Optional[str]:
    p = Path(path)
    if not p.exists():
        return None
    mime = mimetypes.guess_type(str(p))[0] or "image/png"
    b64 = base64.b64encode(p.read_bytes()).decode("ascii")
    return f"data:{mime};base64,{b64}"


def _env() -> Environment:
    return Environment(
        loader=FileSystemLoader(str(_TEMPLATE_DIR)),
        autoescape=select_autoescape(["html", "xml", "j2"]),
        trim_blocks=True,
        lstrip_blocks=True,
    )


def render_html(data: Newsletter) -> str:
    settings = get_settings()
    chart_uris = charts_mod.render_all(data.charts)

    template = _env().get_template("newsletter.html.j2")
    return template.render(
        font_face_css=font_face_css(),
        accent_gold=settings.accent_gold,
        page_bg=settings.page_bg,
        background_uri=_asset_data_uri(settings.background_asset),
        background_placement=settings.background_placement,
        background_opacity=settings.background_opacity,
        logo_uri=_asset_data_uri(settings.logo_asset),
        meta=data.meta,
        news=data.news,
        cbu_fx=data.cbu_fx,
        money_market=data.money_market,
        bloomberg=data.bloomberg,
        stocks=data.stocks,
        charts=chart_uris,
    )


async def render_pdf(data: Newsletter) -> bytes:
    """Render the newsletter to PDF bytes using Playwright."""
    from playwright.async_api import async_playwright

    html = render_html(data)
    launch_kwargs: dict = {"args": ["--no-sandbox"]}
    exe = get_settings().playwright_executable_path
    if exe:
        launch_kwargs["executable_path"] = exe
    async with async_playwright() as pw:
        browser = await pw.chromium.launch(**launch_kwargs)
        page = await browser.new_page()
        await page.set_content(html, wait_until="networkidle")
        pdf_bytes = await page.pdf(
            width="420mm",
            height="297mm",
            landscape=True,
            print_background=True,
            margin={"top": "0", "bottom": "0", "left": "0", "right": "0"},
        )
        await browser.close()
        return pdf_bytes
