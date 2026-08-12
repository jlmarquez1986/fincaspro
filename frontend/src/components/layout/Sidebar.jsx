const NAV = [
  { page: "dashboard", icon: "📊", label: "Dashboard" },
  { page: "tickets", icon: "🔧", label: "Averías", badge: "tickets" },
  { page: "paqueteria", icon: "📦", label: "Paquetería", badge: "paquetes" },
  { page: "llaves", icon: "🔑", label: "Llaves" },
  { page: "avisos", icon: "📢", label: "Avisos" },
  { page: "vecinos", icon: "👥", label: "Vecinos" },
  // Nuevos módulos
  { page: "quejas", icon: "💬", label: "Quejas y mejoras" },
  { page: "piscina", icon: "🏊", label: "Piscina" },
  { page: "administradores", icon: "🏢", label: "Administradores" },
  { page: "estados", icon: "💰", label: "Estados de cuenta" },
  { page: "delegaciones", icon: "📝", label: "Delegaciones" },
  { page: "telefonos", icon: "📞", label: "Teléfonos" },
];

export default function Sidebar({ page, setPage, badges, user, onLogout, communityName }) {
  return (
    <div className="sidebar">
      <div className="sidebar-logo">
        <div className="logo-icon">🏢</div>
        <div>
          <div className="logo-text">FincasPro</div>
          <div className="logo-sub">{communityName || "Comunidad"}</div>
        </div>
      </div>
      <div className="nav-scroll" style={{ flex: 1, overflowY: "auto", padding: "8px 0" }}>
        {NAV.map((n) => (
          <div
            key={n.page}
            className={`nav-item ${page === n.page ? "active" : ""}`}
            onClick={() => setPage(n.page)}
          >
            <span style={{ fontSize: 16 }}>{n.icon}</span>
            <span>{n.label}</span>
            {n.badge && badges[n.badge] > 0 && (
              <span className="nav-badge">{badges[n.badge]}</span>
            )}
          </div>
        ))}
      </div>
      <div className="sidebar-bottom">
        <div className="user-pill" onClick={onLogout} title="Cerrar sesión">
          <div className="avatar">{user?.nombre?.slice(0, 2).toUpperCase()}</div>
          <div>
            <div style={{ fontSize: 12, fontWeight: 500 }}>{user?.nombre}</div>
            <div style={{ fontSize: 11, color: "var(--text-secondary)" }}>
              {user?.rol}
            </div>
          </div>
          <span style={{ marginLeft: "auto", fontSize: 12, color: "var(--text-tertiary)" }}>
            ⎋
          </span>
        </div>
      </div>
    </div>
  );
}