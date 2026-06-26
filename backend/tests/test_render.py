"""Template renders the sample issue with the brand tokens and key sections."""

from app import sample_data
from app.core.config import get_settings
from app.rendering import pdf as renderer


def test_render_html_contains_brand_and_sections():
    html = renderer.render_html(sample_data.sample_newsletter())
    # Gold accent defined exactly once as the CSS variable.
    assert f"--accent-gold: {get_settings().accent_gold}" in html
    # Both pages / column heads present.
    assert "ОБЗОР РЫНКА" in html
    assert "ЛОКАЛЬНЫЙ РЫНОК" in html
    assert "МЕЖДУНАРОДНЫЙ РЫНОК" in html
    # Charts embedded as data URIs.
    assert "data:image/png;base64," in html
    # Flagged stock row highlighted.
    assert "flagged" in html
