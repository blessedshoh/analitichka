"use client";

/** Editable grid for a generic CapitalTable (title + columns + string rows).
 *  Used for the bond tables whose columns differ per table. Supports editing
 *  the title, every cell, and adding/removing rows. */
export interface CapitalTable {
  slot: string;
  title: string;
  columns: string[];
  rows: string[][];
}

export default function CapitalGrid({
  table,
  onChange,
}: {
  table: CapitalTable;
  onChange: (t: CapitalTable) => void;
}) {
  const setCell = (r: number, c: number, v: string) => {
    const rows = table.rows.map((row) => row.slice());
    rows[r][c] = v;
    onChange({ ...table, rows });
  };
  const addRow = () =>
    onChange({ ...table, rows: [...table.rows, table.columns.map(() => "")] });
  const removeRow = (r: number) =>
    onChange({ ...table, rows: table.rows.filter((_, i) => i !== r) });

  return (
    <div style={{ marginBottom: 14 }}>
      <input
        className="cap-title"
        value={table.title}
        onChange={(e) => onChange({ ...table, title: e.target.value })}
      />
      <table className="grid">
        <thead>
          <tr>
            {table.columns.map((c, i) => (
              <th key={i}>{c}</th>
            ))}
            <th style={{ width: 24 }}></th>
          </tr>
        </thead>
        <tbody>
          {table.rows.map((row, r) => (
            <tr key={r}>
              {table.columns.map((_, c) => (
                <td key={c}>
                  <input value={row[c] ?? ""} onChange={(e) => setCell(r, c, e.target.value)} />
                </td>
              ))}
              <td style={{ textAlign: "center" }}>
                <button type="button" className="rowx" onClick={() => removeRow(r)} title="Удалить строку">×</button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
      <button type="button" className="ghost" style={{ marginTop: 4, fontSize: 12 }} onClick={addRow}>
        + строка
      </button>
    </div>
  );
}
