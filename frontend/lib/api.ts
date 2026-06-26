// Thin typed client for the FastAPI backend.
export const API_BASE =
  process.env.NEXT_PUBLIC_API_BASE || "http://localhost:8000";

// ---- Types (mirror backend pydantic models, loosely) ----------------------
export interface SourceMeta {
  source: string;
  status: "ok" | "stale" | "empty" | "error" | "manual";
  warning?: string | null;
  fetched_at?: string | null;
}

export interface CbuRate {
  code: string;
  price?: number | null;
  change_1m?: number | null;
  change_6m?: number | null;
  change_12m?: number | null;
}
export interface CbuFxTable { rows: CbuRate[]; meta: SourceMeta; }

export interface StockRow {
  ticker: string;
  price_prev?: number | null;
  price_curr?: number | null;
  change_pct?: number | null;
  change_pct_calc?: number | null;
  flagged: boolean;
  note?: string | null;
}
export interface StockTable { rows: StockRow[]; meta: SourceMeta; }

// The full Newsletter payload is large & dynamic; keep it loose.
export type Newsletter = any;

async function jsonOrThrow(res: Response) {
  if (!res.ok) throw new Error(`${res.status} ${res.statusText}`);
  return res.json();
}

export type Layout = Record<string, any>;

export const api = {
  config: () => fetch(`${API_BASE}/api/config`).then(jsonOrThrow),

  getLayout: (): Promise<Layout> => fetch(`${API_BASE}/api/layout`).then(jsonOrThrow),
  saveLayout: (l: Layout): Promise<Layout> =>
    fetch(`${API_BASE}/api/layout`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(l),
    }).then(jsonOrThrow),
  resetLayout: (): Promise<Layout> =>
    fetch(`${API_BASE}/api/layout/reset`, { method: "POST" }).then(jsonOrThrow),
  sample: (): Promise<Newsletter> =>
    fetch(`${API_BASE}/api/sample`).then(jsonOrThrow),

  fetchCbuCurrency: (): Promise<CbuFxTable> =>
    fetch(`${API_BASE}/api/fetch/cbu-currency`, { method: "POST" }).then(jsonOrThrow),
  fetchMoneyMarket: () =>
    fetch(`${API_BASE}/api/fetch/money-market`, { method: "POST" }).then(jsonOrThrow),
  fetchStocks: (): Promise<StockTable> =>
    fetch(`${API_BASE}/api/fetch/stocks`, { method: "POST" }).then(jsonOrThrow),
  newsDrafts: (): Promise<Record<string, string[]>> =>
    fetch(`${API_BASE}/api/news/drafts`, { method: "POST" }).then(jsonOrThrow),
  refreshAll: (): Promise<Newsletter> =>
    fetch(`${API_BASE}/api/refresh-all`, { method: "POST" }).then(jsonOrThrow),

  uploadBloomberg: (file: File) => {
    const fd = new FormData();
    fd.append("file", file);
    return fetch(`${API_BASE}/api/upload/bloomberg`, { method: "POST", body: fd }).then(jsonOrThrow);
  },
  uploadStockImage: (file: File): Promise<StockTable> => {
    const fd = new FormData();
    fd.append("file", file);
    return fetch(`${API_BASE}/api/upload/stock-image`, { method: "POST", body: fd }).then(jsonOrThrow);
  },

  preview: (data: Newsletter): Promise<string> =>
    fetch(`${API_BASE}/api/preview`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data),
    }).then((r) => r.text()),

  generateUrl: () => `${API_BASE}/api/generate`,
};
