"""Design-mode layout config: defaults, persistence, render wiring."""

from app.core import layout_store
from app.models.layout import LayoutConfig


def test_defaults_match_reference():
    d = layout_store.default_layout()
    assert d.accent_gold == "#f4e7d4"
    assert d.title_size == 38.5
    assert d.display_font == "Bebas"


def test_save_load_reset_roundtrip(tmp_path, monkeypatch):
    path = tmp_path / "layout.json"
    monkeypatch.setattr(layout_store, "_path", lambda: path)

    cfg = LayoutConfig(accent_gold="#112233", title_size=50, show_charts=False)
    layout_store.save_layout(cfg)
    assert path.exists()

    loaded = layout_store.load_layout()
    assert loaded.accent_gold == "#112233"
    assert loaded.title_size == 50
    assert loaded.show_charts is False

    layout_store.reset_layout()
    assert not path.exists()
    assert layout_store.load_layout().accent_gold == "#f4e7d4"


def test_partial_save_merges_over_defaults(tmp_path, monkeypatch):
    path = tmp_path / "layout.json"
    path.write_text('{"accent_gold": "#abcdef"}', encoding="utf-8")
    monkeypatch.setattr(layout_store, "_path", lambda: path)
    loaded = layout_store.load_layout()
    assert loaded.accent_gold == "#abcdef"
    assert loaded.title_size == 38.5  # default preserved
