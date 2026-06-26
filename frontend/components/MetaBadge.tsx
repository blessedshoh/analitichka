import { SourceMeta } from "@/lib/api";

const LABELS: Record<string, string> = {
  ok: "OK",
  stale: "Кэш (устар.)",
  empty: "Пусто — ввод вручную",
  error: "Ошибка",
  manual: "Ручной ввод",
};

export default function MetaBadge({ meta }: { meta?: SourceMeta }) {
  if (!meta) return null;
  return (
    <div style={{ marginTop: 4 }}>
      <span className={`badge ${meta.status}`}>
        {LABELS[meta.status] || meta.status} · {meta.source}
      </span>
      {meta.warning && <div className="warn">⚠ {meta.warning}</div>}
    </div>
  );
}
