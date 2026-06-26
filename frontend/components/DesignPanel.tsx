"use client";

import { Layout } from "@/lib/api";

/** Control schema for Design mode. Each field maps 1:1 to a LayoutConfig key. */
type Field =
  | { k: string; label: string; type: "color" }
  | { k: string; label: string; type: "num"; min?: number; max?: number; step?: number }
  | { k: string; label: string; type: "select"; options: string[] }
  | { k: string; label: string; type: "bool" };

type Group = { title: string; fields: Field[] };

const FONTS = ["Bebas", "Oswald", "Montserrat", "NotoSans", "Lora", "Tinos"];

const GROUPS: Group[] = [
  {
    title: "Цвета",
    fields: [
      { k: "accent_gold", label: "Золотой акцент", type: "color" },
      { k: "page_bg", label: "Фон страницы", type: "color" },
      { k: "gold_line", label: "Золотая рамка", type: "color" },
      { k: "gold_text", label: "Золотой текст (дата)", type: "color" },
      { k: "card_bg", label: "Фон карточек", type: "color" },
      { k: "table_border", label: "Рамка таблиц", type: "color" },
      { k: "grid", label: "Линии ячеек", type: "color" },
      { k: "ink", label: "Текст", type: "color" },
    ],
  },
  {
    title: "Шрифты",
    fields: [
      { k: "display_font", label: "Заголовки", type: "select", options: FONTS },
      { k: "headline_font", label: "Подзаголовки/капшены", type: "select", options: FONTS },
      { k: "body_font", label: "Основной текст", type: "select", options: FONTS },
      { k: "table_font", label: "Данные таблиц", type: "select", options: FONTS },
    ],
  },
  {
    title: "Размеры шрифта (pt)",
    fields: [
      { k: "title_size", label: "Заголовок ОБЗОР РЫНКА", type: "num", min: 16, max: 60, step: 0.5 },
      { k: "date_size", label: "Дата", type: "num", min: 6, max: 24, step: 0.5 },
      { k: "dept_size", label: "Департамент", type: "num", min: 6, max: 24, step: 0.5 },
      { k: "pill_size", label: "Метки (США…)", type: "num", min: 10, max: 36, step: 0.5 },
      { k: "news_size", label: "Текст новостей", type: "num", min: 7, max: 18, step: 0.5 },
      { k: "col_head_size", label: "Заголовки колонок", type: "num", min: 10, max: 30, step: 0.5 },
      { k: "section_head_size", label: "Секции (ДЕНЕЖНЫЙ…)", type: "num", min: 10, max: 30, step: 0.5 },
      { k: "caption_size", label: "Капшены таблиц", type: "num", min: 6, max: 16, step: 0.5 },
      { k: "table_size", label: "Данные таблиц", type: "num", min: 5, max: 14, step: 0.2 },
      { k: "summary_value_size", label: "Итоги (крупные цифры)", type: "num", min: 8, max: 24, step: 0.5 },
      { k: "footnote_size", label: "Сноска", type: "num", min: 6, max: 14, step: 0.5 },
    ],
  },
  {
    title: "Отступы и рамки (pt)",
    fields: [
      { k: "page_padding_mm", label: "Поля страницы (мм)", type: "num", min: 0, max: 20, step: 0.5 },
      { k: "quad_gap", label: "Зазор между карточками", type: "num", min: 0, max: 40, step: 1 },
      { k: "card_padding", label: "Внутр. отступ карточек", type: "num", min: 0, max: 30, step: 1 },
      { k: "table_gap", label: "Зазор между таблицами", type: "num", min: 0, max: 20, step: 1 },
      { k: "card_border_w", label: "Толщина рамки карточек", type: "num", min: 0, max: 5, step: 0.1 },
      { k: "table_border_w", label: "Толщина рамки таблиц", type: "num", min: 0, max: 4, step: 0.1 },
    ],
  },
  {
    title: "Фон / водяной знак",
    fields: [
      { k: "background_placement", label: "Показывать фон", type: "select", options: ["watermark", "none"] },
      { k: "background_opacity", label: "Прозрачность", type: "num", min: 0, max: 1, step: 0.01 },
      { k: "background_grayscale", label: "Обесцвечивание", type: "num", min: 0, max: 1, step: 0.05 },
    ],
  },
  {
    title: "Секции (вкл/выкл)",
    fields: [
      { k: "show_charts", label: "Графики", type: "bool" },
      { k: "show_capital_news", label: "Новости рынка капитала", type: "bool" },
      { k: "show_footnote", label: "Сноска *TSMI", type: "bool" },
    ],
  },
];

export default function DesignPanel({
  layout,
  onChange,
  onReset,
}: {
  layout: Layout;
  onChange: (k: string, v: any) => void;
  onReset: () => void;
}) {
  return (
    <div className="design">
      <div className="design-head">
        <strong>🎨 Режим конструктора</strong>
        <button className="ghost" onClick={onReset}>Сбросить к эталону</button>
      </div>
      <p className="muted">
        Меняйте стиль и макет — предпросмотр справа обновляется живьём. Изменения
        сохраняются автоматически; выключите режим, чтобы продолжить с этим макетом.
      </p>
      {GROUPS.map((g) => (
        <details key={g.title} open>
          <summary>{g.title}</summary>
          <div className="design-grid">
            {g.fields.map((f) => (
              <label key={f.k} className="design-field">
                <span>{f.label}</span>
                {f.type === "color" && (
                  <span className="row" style={{ gap: 4 }}>
                    <input type="color" value={layout[f.k] ?? "#000000"} onChange={(e) => onChange(f.k, e.target.value)} />
                    <input type="text" value={layout[f.k] ?? ""} onChange={(e) => onChange(f.k, e.target.value)} style={{ width: 80 }} />
                  </span>
                )}
                {f.type === "num" && (
                  <input type="number" min={f.min} max={f.max} step={f.step}
                    value={layout[f.k] ?? 0} onChange={(e) => onChange(f.k, e.target.value === "" ? null : Number(e.target.value))} />
                )}
                {f.type === "select" && (
                  <select value={layout[f.k] ?? f.options[0]} onChange={(e) => onChange(f.k, e.target.value)}>
                    {f.options.map((o) => <option key={o} value={o}>{o}</option>)}
                  </select>
                )}
                {f.type === "bool" && (
                  <input type="checkbox" checked={!!layout[f.k]} onChange={(e) => onChange(f.k, e.target.checked)} />
                )}
              </label>
            ))}
          </div>
        </details>
      ))}
    </div>
  );
}
