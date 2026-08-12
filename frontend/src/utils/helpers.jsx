// ── Badge ──────────────────────────────────────────────
const BADGE = {
  pendiente:  "badge-blue",
  en_proceso: "badge-amber",
  resuelto:   "badge-green",
  cancelado:  "badge-gray",
  urgente:    "badge-red",
  media:      "badge-amber",
  normal:     "badge-blue",
  baja:       "badge-gray",
  disponible: "badge-green",
  prestada:   "badge-amber",
  entregado:  "badge-green",
  info:       "badge-blue",
  aviso:      "badge-amber",
  propietario:"badge-blue",
  inquilino:  "badge-amber",
};

export function Badge({ val }) {
  const label = val?.replace("_", " ") || "";
  return <span className={`badge ${BADGE[val] || "badge-gray"}`}>{label}</span>;
}

// ── Formateo de fechas ────────────────────────────────
export function fmtDate(d) {
  if (!d) return "—";
  return new Date(d).toLocaleString(navigator.language || "es-ES", {
    day: "2-digit",
    month: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
  });
}