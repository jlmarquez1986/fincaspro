export default function Landing({ onSelect, communityName }) {
  return (
    <div className="landing-container">
      <div className="landing-content">
        <div className="landing-header">
          <div className="landing-logo">🏢</div>
          <h1 className="landing-title">FincasPro</h1>
          <p className="landing-subtitle">{communityName || "Comunidad"}</p>
          <p className="landing-description">
            Gestión integral para comunidades de propietarios y conserjería
          </p>
        </div>

        <div className="landing-cards">
          <div className="landing-card staff-card" onClick={() => onSelect("staff")}>
            <div className="card-icon">🔑</div>
            <h3>Staff</h3>
            <p>Conserjería y administración</p>
            <span className="card-badge">Acceso restringido</span>
            <div className="card-hover-effect"></div>
          </div>

          <div className="landing-card portal-card" onClick={() => onSelect("portal")}>
            <div className="card-icon">🏠</div>
            <h3>Portal del Vecino</h3>
            <p>Tu espacio personal</p>
            <span className="card-badge">Acceso con credenciales</span>
            <div className="card-hover-effect"></div>
          </div>
        </div>

        <div className="landing-footer">
          <span>v2.0 · 🔒 SSL · 📧 Notificaciones</span>
        </div>
      </div>
    </div>
  );
}