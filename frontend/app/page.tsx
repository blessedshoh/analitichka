"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { api, API_BASE, Newsletter, Layout } from "@/lib/api";
import EditableGrid, { Col } from "@/components/EditableGrid";
import FileDrop from "@/components/FileDrop";
import MetaBadge from "@/components/MetaBadge";
import DesignPanel from "@/components/DesignPanel";
import CapitalGrid from "@/components/CapitalGrid";

const CHANGE_COLS = (label: string): Col[] => [
  { key: "name", label },
  { key: "price", label: "Цена", type: "number" },
  { key: "change_1m", label: "1m", type: "number" },
  { key: "change_6m", label: "6m", type: "number" },
  { key: "change_12m", label: "12m", type: "number" },
];

export default function Home() {
  const [nl, setNl] = useState<Newsletter | null>(null);
  const [busy, setBusy] = useState<string | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string>("");
  const [designMode, setDesignMode] = useState(false);
  const [layout, setLayout] = useState<Layout | null>(null);
  const debounce = useRef<any>(null);
  const layoutDebounce = useRef<any>(null);

  // Load reference/sample payload so the form opens pre-filled.
  useEffect(() => {
    api.config()
      .then((c) => document.documentElement.style.setProperty("--accent-gold", c.accent_gold))
      .catch(() => {});
    api.sample().then(setNl).catch((e) => console.error(e));
    api.getLayout().then(setLayout).catch((e) => console.error(e));
  }, []);

  // Live HTML preview, debounced on every edit.
  const refreshPreview = useCallback((data: Newsletter) => {
    clearTimeout(debounce.current);
    debounce.current = setTimeout(async () => {
      try {
        const html = await api.preview(data);
        const blob = new Blob([html], { type: "text/html" });
        setPreviewUrl((old) => {
          if (old) URL.revokeObjectURL(old);
          return URL.createObjectURL(blob);
        });
      } catch (e) { console.error(e); }
    }, 500);
  }, []);

  // Design mode: persist the edited layout (debounced) then re-preview, since
  // the preview endpoint renders from the saved layout.
  const onLayoutChange = useCallback((k: string, v: any) => {
    setLayout((prev) => {
      const next = { ...(prev || {}), [k]: v };
      clearTimeout(layoutDebounce.current);
      layoutDebounce.current = setTimeout(async () => {
        try {
          await api.saveLayout(next);
          if (nl) refreshPreview(nl);
        } catch (e) { console.error(e); }
      }, 350);
      return next;
    });
  }, [nl, refreshPreview]);

  const resetLayout = useCallback(async () => {
    const def = await api.resetLayout();
    setLayout(def);
    if (nl) refreshPreview(nl);
  }, [nl, refreshPreview]);

  useEffect(() => { if (nl) refreshPreview(nl); }, [nl, refreshPreview]);

  if (!nl) return <div style={{ padding: 40 }}>Загрузка…</div>;

  const patch = (updater: (d: Newsletter) => void) => {
    const next = structuredClone(nl);
    updater(next);
    setNl(next);
  };

  const run = async (name: string, fn: () => Promise<void>) => {
    setBusy(name);
    try { await fn(); } catch (e: any) { alert(`Ошибка: ${e.message}`); }
    finally { setBusy(null); }
  };

  const generate = async () => {
    setBusy("generate");
    try {
      const res = await fetch(api.generateUrl(), {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(nl),
      });
      if (!res.ok) throw new Error(`${res.status}`);
      const blob = await res.blob();
      const url = URL.createObjectURL(blob);
      setPreviewUrl(url);
      const a = document.createElement("a");
      a.href = url;
      a.download = `nbu-review-${nl.meta?.issue_date || "issue"}.pdf`;
      a.click();
    } catch (e: any) { alert(`Ошибка генерации: ${e.message}`); }
    finally { setBusy(null); }
  };

  return (
    <div className="app">
      <div className="panel left">
        <h1>NBU — Обзор рынка</h1>
        <p className="sub">Введите новости, обновите данные, нажмите «Сгенерировать PDF».</p>

        {designMode && layout ? (
          <DesignPanel layout={layout} onChange={onLayoutChange} onReset={resetLayout} />
        ) : (
        <>
        <button disabled={busy === "all"} onClick={() => run("all", async () => {
          const fresh = await api.refreshAll();
          setNl(fresh);
        })} style={{ marginTop: 6 }}>
          {busy === "all" ? "Обновление…" : "⟳ Обновить всё (CBU + новости)"}
        </button>

        {/* ----- Header meta ----- */}
        <h2>Выпуск</h2>
        <div className="row">
          <div style={{ flex: 1 }}>
            <label className="field">День недели</label>
            <input value={nl.meta?.weekday || ""} onChange={(e) => patch((d) => (d.meta.weekday = e.target.value))} />
          </div>
          <div style={{ flex: 1 }}>
            <label className="field">Дата</label>
            <input value={nl.meta?.issue_date || ""} onChange={(e) => patch((d) => (d.meta.issue_date = e.target.value))} />
          </div>
          <div style={{ width: 90 }}>
            <label className="field">№</label>
            <input value={nl.meta?.issue_number ?? ""} onChange={(e) => patch((d) => (d.meta.issue_number = Number(e.target.value) || null))} />
          </div>
        </div>

        {/* ----- News ----- */}
        <h2>Новости (свободный текст)</h2>
        <button className="ghost" disabled={busy === "news"} onClick={() => run("news", async () => {
          const drafts = await api.newsDrafts();
          patch((d) => {
            (["us", "europe", "asia", "cis"] as const).forEach((k) => {
              if (drafts[k]?.length) d.news[k] = drafts[k].join("\n");
            });
            if (drafts.capital_markets?.length) d.news.capital_markets = drafts.capital_markets;
          });
        })} style={{ marginBottom: 8 }}>
          {busy === "news" ? "Загрузка…" : "↧ Черновики новостей из Telegram"}
        </button>
        {([["us", "США"], ["europe", "ЕВРОПА"], ["asia", "АЗИЯ"], ["cis", "СНГ"]] as const).map(([k, lbl]) => (
          <div key={k}>
            <label className="field">{lbl}</label>
            <textarea value={nl.news?.[k] || ""} onChange={(e) => patch((d) => (d.news[k] = e.target.value))} />
          </div>
        ))}
        <label className="field">Новости рынка капитала (по одной на строку)</label>
        <textarea
          value={(nl.news?.capital_markets || []).join("\n")}
          onChange={(e) => patch((d) => (d.news.capital_markets = e.target.value.split("\n").filter(Boolean)))}
        />

        {/* ----- CBU currency ----- */}
        <h2>Курсы валют (ЦБ РУз)</h2>
        <button disabled={busy === "cbu"} onClick={() => run("cbu", async () => {
          const t = await api.fetchCbuCurrency();
          patch((d) => (d.cbu_fx = t));
        })}>{busy === "cbu" ? "Обновление…" : "Обновить курсы ЦБ"}</button>
        <MetaBadge meta={nl.cbu_fx?.meta} />
        {nl.cbu_fx && (
          <EditableGrid
            cols={[
              { key: "code", label: "Курс" },
              { key: "price", label: "Цена", type: "number" },
              { key: "change_1m", label: "1m", type: "number" },
              { key: "change_6m", label: "6m", type: "number" },
              { key: "change_12m", label: "12m", type: "number" },
            ]}
            rows={nl.cbu_fx.rows}
            onChange={(rows) => patch((d) => (d.cbu_fx.rows = rows))}
          />
        )}

        {/* ----- Money market ----- */}
        <h2>Денежный рынок (UZONIA / РЕПО / межбанк)</h2>
        <button disabled={busy === "mm"} onClick={() => run("mm", async () => {
          const t = await api.fetchMoneyMarket();
          patch((d) => (d.money_market = t));
        })}>{busy === "mm" ? "…" : "Подтянуть/обновить (ручное подтверждение)"}</button>
        <MetaBadge meta={nl.money_market?.uzonia?.meta} />
        {nl.money_market && (
          <>
            <label className="field">UZONIA (%)</label>
            <EditableGrid
              cols={[
                { key: "date", label: "Дата" }, { key: "on", label: "O/N", type: "number" },
                { key: "w1", label: "1W", type: "number" }, { key: "m1", label: "1M", type: "number" },
                { key: "m3", label: "3M", type: "number" }, { key: "m6", label: "6M", type: "number" },
              ]}
              rows={nl.money_market.uzonia.rows}
              onChange={(rows) => patch((d) => (d.money_market.uzonia.rows = rows))}
            />
            <label className="field">Межбанковские депозиты</label>
            <EditableGrid
              cols={[
                { key: "tenor", label: "Период" }, { key: "date", label: "Дата" },
                { key: "rate", label: "Ставка", type: "number" }, { key: "trend", label: "Тренд", type: "number" },
                { key: "volume", label: "Объём млн", type: "number" },
              ]}
              rows={nl.money_market.interbank.rows}
              onChange={(rows) => patch((d) => (d.money_market.interbank.rows = rows))}
            />
            <label className="field">РЕПО</label>
            <EditableGrid
              cols={[
                { key: "date", label: "Дата" }, { key: "deals", label: "Сделок", type: "number" },
                { key: "avg_rate", label: "Ср. ставка", type: "number" }, { key: "volume", label: "Объём млн", type: "number" },
              ]}
              rows={nl.money_market.repo.rows}
              onChange={(rows) => patch((d) => (d.money_market.repo.rows = rows))}
            />
            <label className="field">Общая ликвидность банковской системы (нижняя плашка)</label>
            <div className="row">
              {([
                ["total_liquidity", "Общая ликв. (трлн)"],
                ["deviation_from_norm", "Откл. от нормы (трлн)"],
                ["cb_withdrawal_ops", "Привлечение ЦБ (трлн)"],
                ["cb_provision_ops", "Предоставление ЦБ"],
              ] as const).map(([k, lbl]) => (
                <div key={k} style={{ flex: 1, minWidth: 120 }}>
                  <label className="field">{lbl}</label>
                  <input value={nl.money_market.summary?.[k] ?? ""}
                    onChange={(e) => patch((d) => (d.money_market.summary[k] = e.target.value === "" ? null : Number(e.target.value)))} />
                </div>
              ))}
            </div>
          </>
        )}

        {/* ----- Bloomberg ----- */}
        <h2>Bloomberg экспорт (.xlsx)</h2>
        <FileDrop accept=".xlsx,.xlsm" label="Перетащите файл Bloomberg сюда или нажмите"
          onFile={(f) => run("bb", async () => {
            const t = await api.uploadBloomberg(f);
            patch((d) => (d.bloomberg = t));
          })} />
        <MetaBadge meta={nl.bloomberg?.meta} />
        {nl.bloomberg && (
          <>
            <label className="field">Курсы валют (международные)</label>
            <EditableGrid
              cols={[
                { key: "code", label: "Кросс" }, { key: "price", label: "Цена", type: "number" },
                { key: "change_1m", label: "1m", type: "number" }, { key: "change_6m", label: "6m", type: "number" },
                { key: "change_12m", label: "12m", type: "number" },
              ]}
              rows={nl.bloomberg.fx.rows}
              addable newRow={() => ({ code: "", price: null })}
              onChange={(rows) => patch((d) => (d.bloomberg.fx.rows = rows))} />

            <label className="field">Сырьевой рынок</label>
            <EditableGrid cols={CHANGE_COLS("Сырьё")} rows={nl.bloomberg.commodities.rows}
              addable newRow={() => ({ name: "", price: null })}
              onChange={(rows) => patch((d) => (d.bloomberg.commodities.rows = rows))} />

            <label className="field">Индексы фондового рынка</label>
            <EditableGrid cols={CHANGE_COLS("Индекс")} rows={nl.bloomberg.equities.rows}
              addable newRow={() => ({ name: "", price: null })}
              onChange={(rows) => patch((d) => (d.bloomberg.equities.rows = rows))} />

            <label className="field">Облигации казначейства США</label>
            <EditableGrid
              cols={[
                { key: "tenor", label: "Срок" }, { key: "yld", label: "Доходность", type: "number" },
                { key: "change_1m", label: "1m", type: "number" }, { key: "change_6m", label: "6m", type: "number" },
                { key: "change_12m", label: "12m", type: "number" },
              ]}
              rows={nl.bloomberg.treasuries.rows}
              addable newRow={() => ({ tenor: "", yld: null })}
              onChange={(rows) => patch((d) => (d.bloomberg.treasuries.rows = rows))} />

            <details style={{ marginTop: 8 }}>
              <summary style={{ cursor: "pointer", fontWeight: 600 }}>Ставки (кривые): SOFR, EURIBOR, …</summary>
              {nl.bloomberg.rate_curves.map((c: any, ci: number) => (
                <div key={ci}>
                  <label className="field">{c.name}</label>
                  <EditableGrid
                    cols={[
                      { key: "date", label: "Дата" }, { key: "on", label: "O/N", type: "number" },
                      { key: "m1", label: "1M", type: "number" }, { key: "m3", label: "3M", type: "number" },
                      { key: "m6", label: "6M", type: "number" }, { key: "m12", label: "12M", type: "number" },
                    ]}
                    rows={c.rows}
                    onChange={(rows) => patch((d) => (d.bloomberg.rate_curves[ci].rows = rows))} />
                </div>
              ))}
            </details>
          </>
        )}

        {/* ----- Stocks (Telegram + Claude) ----- */}
        <h2>Итоги торгов (Telegram → Claude)</h2>
        <div className="row">
          <button disabled={busy === "tg"} onClick={() => run("tg", async () => {
            const t = await api.fetchStocks();
            patch((d) => (d.stocks = t));
          })}>{busy === "tg" ? "Извлечение…" : "Подтянуть из Telegram"}</button>
          <FileDrop accept="image/*" label="…или загрузить фото вручную"
            onFile={(f) => run("tg", async () => {
              const t = await api.uploadStockImage(f);
              patch((d) => (d.stocks = t));
            })} />
        </div>
        <MetaBadge meta={nl.stocks?.meta} />
        {nl.stocks && (
          <>
            <p className="muted">Подсвеченные строки: извлечённый % расходится с пересчитанным — проверьте.</p>
            <EditableGrid
              cols={[
                { key: "ticker", label: "Тикер" },
                { key: "price_prev", label: "Цена пред.", type: "number" },
                { key: "price_curr", label: "Цена тек.", type: "number" },
                { key: "change_pct", label: "% (извл.)", type: "number" },
                { key: "change_pct_calc", label: "% (расчёт)", type: "number", readOnly: true },
              ]}
              rows={nl.stocks.rows}
              rowFlag={(r) => r.flagged}
              rowNote={(r) => r.note}
              onChange={(rows) => patch((d) => (d.stocks.rows = rows))}
            />
          </>
        )}

        {/* ----- Capital-market bond tables ----- */}
        <h2>Рынок капитала — облигации</h2>
        <p className="muted">Корпоративные / гос. облигации и еврооблигации. Редактируйте ячейки, добавляйте строки.</p>
        {(nl.capital_tables || []).map((t: any, i: number) => (
          <CapitalGrid key={t.slot || i} table={t}
            onChange={(nt) => patch((d) => { d.capital_tables[i] = nt; })} />
        ))}

        <div style={{ height: 30 }} />
        </>
        )}
      </div>

      {/* ----- Preview ----- */}
      <div className="preview">
        <div className="preview-bar">
          <button className="primary" disabled={busy === "generate"} onClick={generate}>
            {busy === "generate" ? "Генерация…" : "⬇ Сгенерировать PDF"}
          </button>
          <button className={designMode ? "" : "ghost"} onClick={() => setDesignMode((v) => !v)}
            style={designMode ? {} : { color: "#eee", borderColor: "#555" }}>
            {designMode ? "✓ Конструктор включён" : "🎨 Конструктор макета"}
          </button>
          <span className="muted" style={{ color: "#bbb" }}>
            {designMode ? "Меняйте стиль — сохраняется автоматически" : "Живой предпросмотр · API: " + API_BASE}
          </span>
        </div>
        <iframe src={previewUrl} title="preview" />
      </div>
    </div>
  );
}
