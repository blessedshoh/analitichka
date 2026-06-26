"use client";

export interface Col {
  key: string;
  label: string;
  type?: "text" | "number";
  readOnly?: boolean;
}

interface Props {
  cols: Col[];
  rows: any[];
  onChange: (rows: any[]) => void;
  // mark whole row highlighted (e.g. validation flag)
  rowFlag?: (row: any) => boolean;
  rowNote?: (row: any) => string | null | undefined;
  // when set, show add/remove-row controls; newRow() builds a blank row
  addable?: boolean;
  newRow?: () => any;
}

/** A spreadsheet-like editable grid. Every fetched value is editable here
 *  before generation; flagged rows are highlighted for one-glance review. */
export default function EditableGrid({ cols, rows, onChange, rowFlag, rowNote, addable, newRow }: Props) {
  const update = (i: number, key: string, raw: string, type?: string) => {
    const next = rows.slice();
    let val: any = raw;
    if (type === "number") val = raw === "" ? null : Number(raw);
    next[i] = { ...next[i], [key]: val };
    onChange(next);
  };
  const removeRow = (i: number) => onChange(rows.filter((_, j) => j !== i));
  const addRow = () => onChange([...rows, newRow ? newRow() : {}]);

  return (
    <>
      <table className="grid">
        <thead>
          <tr>
            {cols.map((c) => (
              <th key={c.key}>{c.label}</th>
            ))}
            {addable && <th style={{ width: 24 }}></th>}
          </tr>
        </thead>
        <tbody>
          {rows.map((row, i) => {
            const flagged = rowFlag?.(row);
            const note = rowNote?.(row);
            return (
              <tr key={i} className={flagged ? "flagged" : ""} title={note || ""}>
                {cols.map((c) => (
                  <td key={c.key}>
                    <input
                      type="text"
                      inputMode={c.type === "number" ? "decimal" : "text"}
                      readOnly={c.readOnly}
                      value={row[c.key] ?? ""}
                      onChange={(e) => update(i, c.key, e.target.value, c.type)}
                    />
                  </td>
                ))}
                {addable && (
                  <td style={{ textAlign: "center" }}>
                    <button type="button" className="rowx" onClick={() => removeRow(i)} title="Удалить строку">×</button>
                  </td>
                )}
              </tr>
            );
          })}
        </tbody>
      </table>
      {addable && (
        <button type="button" className="ghost" style={{ marginTop: 4, fontSize: 12 }} onClick={addRow}>
          + строка
        </button>
      )}
    </>
  );
}
