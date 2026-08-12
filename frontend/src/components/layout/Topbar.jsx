export default function Topbar({ title }) {
  return (
    <div className="topbar">
      <div className="page-title">{title}</div>
      <div style={{ fontSize: 12, color: "var(--text-secondary)" }}>
        🟢 Backend conectado · 📧 Email activo · 🏠 Portal activo
      </div>
    </div>
  );
}