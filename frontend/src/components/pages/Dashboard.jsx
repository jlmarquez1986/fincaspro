import { useState, useEffect } from "react";
import { api } from "../../api/client";

export default function Dashboard({ setPage }) {
  const [stats, setStats] = useState(null);

  useEffect(() => {
    api.dashboard()
      .then(setStats)
      .catch(() => {});
  }, []);

  if (!stats) {
    return <div style={{ padding: 20, color: "var(--text-secondary)" }}>Cargando...</div>;
  }

  const cards = [
    { label: "Tickets abiertos", value: stats.tickets_abiertos, color: "#ef4444", icon: "🔧", page: "tickets" },
    { label: "Paquetes pendientes", value: stats.pkgs_pendientes, color: "#2563eb", icon: "📦", page: "paqueteria" },
    { label: "Llaves prestadas", value: stats.llaves_prestadas, color: "#d97706", icon: "🔑", page: "llaves" },
    { label: "Tickets resueltos", value: stats.tickets_resueltos, color: "#16a34a", icon: "✅", page: "dashboard" },
  ];

  return (
    <div>
      <div className="grid-4" style={{ marginBottom: 20 }}>
        {cards.map((c) => {
          const isClickable = c.page !== "dashboard";
          return (
            <div
              key={c.label}
              className="metric"
              style={isClickable ? { cursor: "pointer" } : {}}
              onClick={() => isClickable && setPage(c.page)}
            >
              <div className="metric-label">
                {c.icon} {c.label}
              </div>
              <div className="metric-value" style={{ color: c.color }}>
                {c.value}
              </div>
            </div>
          );
        })}
      </div>
      <div style={{ background: "var(--bg-secondary)", borderRadius: 8, padding: 16, border: "0.5px solid var(--border)" }}>
        <p style={{ color: "var(--text-secondary)", fontSize: 13 }}>💡 Nuevas funciones disponibles:</p>
        <ul style={{ color: "var(--text-secondary)", fontSize: 13, marginTop: 8, marginLeft: 18, lineHeight: 1.8 }}>
          <li>📧 Notificaciones automáticas por email a vecinos</li>
          <li>📸 Subida de fotos en tickets de averías</li>
          <li>🏠 Portal del vecino con acceso propio</li>
          <li>🐳 Despliegue con Docker listo para usar</li>
        </ul>
      </div>
    </div>
  );
}