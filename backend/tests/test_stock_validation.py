"""Stock-table validation: recompute change_pct and flag disagreements."""

from app.fetchers.telegram_stocks import _build_rows


def test_flags_mismatch_beyond_tolerance():
    rows = _build_rows([
        {"ticker": "IPTB", "price_prev": 3.23, "price_curr": 3.20, "change_pct": -0.96},
    ])
    r = rows[0]
    # recompute = (3.20-3.23)/3.23*100 = -0.93 -> differs from -0.96 by 0.03 < 0.05
    assert r.change_pct_calc == -0.93
    assert r.flagged is False


def test_flags_clear_disagreement():
    rows = _build_rows([
        {"ticker": "XXX", "price_prev": 100, "price_curr": 110, "change_pct": 5.0},
    ])
    r = rows[0]
    assert r.change_pct_calc == 10.0
    assert r.flagged is True
    assert r.note


def test_handles_missing_prices():
    rows = _build_rows([{"ticker": "NA", "price_prev": None, "price_curr": None, "change_pct": None}])
    assert rows[0].change_pct_calc is None
    assert rows[0].flagged is False
