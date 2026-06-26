"""CBU currency helpers + graceful degradation (offline-safe)."""

from app.fetchers.cbu_currency import _pct_change, _to_float


def test_pct_change():
    assert _pct_change(110, 100) == 10.0
    assert _pct_change(90, 100) == -10.0
    assert _pct_change(100, 0) is None
    assert _pct_change(None, 100) is None


def test_to_float_handles_locale_and_blanks():
    assert _to_float("12 990,26".replace(" ", "")) == 12990.26
    assert _to_float("11990.26") == 11990.26
    assert _to_float("-") is None
    assert _to_float(None) is None
