import { useState } from "react";
import { api } from "../../api/client";

export default function LoginStaff({ onLogin, communityName }) {
  const [u, setU] = useState("conserje");
  const [p, setP] = useState("conserje123");
  const [err, setErr] = useState("");

  const submit = async () => {
    setErr("");
    const res = await api.login(u, p);
    if (res.access_token) {
      localStorage.setItem("token", res.access_token);
      localStorage.setItem("user", JSON.stringify(res.usuario));
      onLogin(res.usuario);
    } else {
      setErr(res.detail || "Error al iniciar sesión");
    }
  };

  return (
    <div className="auth-shell">
      <div className="auth-card">
        <div style={{ textAlign: "center", marginBottom: 24 }}>
          <div className="auth-mark staff">🏢</div>
          <h2 className="auth-title">FincasPro</h2>
          <p className="auth-subtitle">Acceso Staff — Conserjería y Administración</p>
          {communityName && (
            <p className="auth-subtitle" style={{ marginTop: -2 }}>
              {communityName}
            </p>
          )}
        </div>
        <div className="form-group">
          <label>Usuario</label>
          <input
            value={u}
            onChange={(e) => setU(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && submit()}
          />
        </div>
        <div className="form-group">
          <label>Contraseña</label>
          <input
            type="password"
            value={p}
            onChange={(e) => setP(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && submit()}
          />
        </div>
        {err && (
          <p style={{ color: "#ef4444", fontSize: 12, marginBottom: 8 }}>
            {err}
          </p>
        )}
        <button
          className="btn btn-primary"
          style={{ width: "100%", justifyContent: "center", marginTop: 4 }}
          onClick={submit}
        >
          Entrar
        </button>
        <p className="auth-demo">Demo: conserje / conserje123</p>
      </div>
    </div>
  );
}