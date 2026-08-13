// Formateo de fechas según el idioma y zona horaria del navegador.

export function fmtDate(d) {
  if (!d) return "—";

  return new Date(d).toLocaleString(navigator.language || "es-ES", {
    day: "2-digit",
    month: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
  });
}