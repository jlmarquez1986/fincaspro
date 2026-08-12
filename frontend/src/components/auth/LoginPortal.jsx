import { useState } from "react";
import { api } from "../../api/client";

export default function LoginPortal({ onLogin, communityName }) {
  const [modo, setModo] = useState("login");
  const [email, setEmail] = useState("maria@email.com");
  const [p, setP] = useState("vecino123");
  const [err, setErr] = useState("");
  const [reg, setReg] = useState({ piso: "", nombre: "", email: "", password: "" });
  const [regMsg, setRegMsg] = useState("");
  const [enviando, setEnviando] = useState(false);

  const submit = async () => {
    setErr("");
    try {
      const res = await api.vecinoLogin(email, p);
      if (res.access_token) {
        localStorage.setItem("vecino_token", res.access_token);
        localStorage.setItem("vecino", JSON.stringify(res.vecino));
        onLogin(res.vecino);
      } else {
        setErr(res.detail || "Error al iniciar sesión");
      }
    } catch (e) {
      setErr(e.message);
    }
  };

  const registrar = async () => {
    setErr("");
    setRegMsg("");
    setEnviando(true);
    try {
      await api.vecinos.portalRegistro(reg);
      setRegMsg("Cuenta activada. Ya puedes iniciar sesión con tu email y contraseña.");
      setEmail(reg.email);
      setP("");
      setModo("login");
    } catch (e) {
      setErr(e.message || "No se pudo completar el registro");
    } finally {
      setEnviando(false);
    }
  };

  if (modo === "registro") {
    return (
      <div className="auth-shell">
        <div className="auth-card">
          <div style={{ textAlign: "center", marginBottom: 24 }}>
            <div className="auth-mark portal">🏠</div>
            <h2 className="auth-title">Activa tu cuenta</h2>
            <p className="auth-subtitle">
              Tu piso ya debe estar registrado por la conserjería
            </p>
          </div>
          <div className="form-group">
            <label>Piso (ej: 3ºB)</label>
            <input
              value={reg.piso}
              onChange={(e) => setReg((r) => ({ ...r, piso: e.target.value }))}
            />
          </div>
          <div className="form-group">
            <label>Tu nombre</label>
            <input
              value={reg.nombre}
              onChange={(e) => setReg((r) => ({ ...r, nombre: e.target.value }))}
            />
          </div>
          <div className="form-group">
            <label>Email</label>
            <input
              type="email"
              value={reg.email}
              onChange={(e) => setReg((r) => ({ ...r, email: e.target.value }))}
            />
          </div>
          <div className="form-group">
            <label>Elige una contraseña (mín. 8 caracteres)</label>
            <input
              type="password"
              value={reg.password}
              onChange={(e) => setReg((r) => ({ ...r, password: e.target.value }))}
            />
          </div>
          {err && (
            <p style={{ color: "#ef4444", fontSize: 12, marginBottom: 8 }}>
              {err}
            </p>
          )}
          <button
            className="btn btn-primary"
            style={{
              width: "100%",
              justifyContent: "center",
              marginTop: 4,
              background: "var(--portal)",
              borderColor: "var(--portal)",
              color: "#fff",
            }}
            disabled={
              !reg.piso ||
              !reg.nombre ||
              !reg.email ||
              reg.password.length < 8 ||
              enviando
            }
            onClick={registrar}
          >
            {enviando ? "Activando..." : "Activar cuenta"}
          </button>
          <p
            className="auth-demo"
            style={{ cursor: "pointer" }}
            onClick={() => {
              setModo("login");
              setErr("");
            }}
          >
            ← Ya tengo cuenta, quiero entrar
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="auth-shell">
      <div className="auth-card">
        <div style={{ textAlign: "center", marginBottom: 24 }}>
          <div className="auth-mark portal">🏠</div>
          <h2 className="auth-title">Portal del Vecino</h2>
          <p className="auth-subtitle">{communityName || "Comunidad"}</p>
        </div>
        <div className="form-group">
          <label>Email</label>
          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
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
        {regMsg && (
          <p style={{ color: "var(--portal)", fontSize: 12, marginBottom: 8 }}>
            {regMsg}
          </p>
        )}
        {err && (
          <p style={{ color: "#ef4444", fontSize: 12, marginBottom: 8 }}>
            {err}
          </p>
        )}
        <button
          className="btn btn-primary"
          style={{
            width: "100%",
            justifyContent: "center",
            marginTop: 4,
            background: "var(--portal)",
            borderColor: "var(--portal)",
            color: "#fff",
          }}
          onClick={submit}
        >
          Entrar al Portal
        </button>
        <p
          className="auth-demo"
          style={{ cursor: "pointer" }}
          onClick={() => {
            setModo("registro");
            setErr("");
            setRegMsg("");
          }}
        >
          ¿Aún no tienes cuenta? Actívala aquí →
        </p>
        <p className="auth-demo">Demo: maria@email.com / vecino123</p>
      </div>
    </div>
  );
}