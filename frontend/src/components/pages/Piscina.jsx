import { useState, useEffect } from "react";
import { api } from "../../api/client";
import { fmtDate } from "../../utils/helpers";

export default function Piscina() {
  const [carnets, setCarnets] = useState([]);
  const [vecinos, setVecinos] = useState([]);
  const [registros, setRegistros] = useState([]);
  const [saldoInvitaciones, setSaldoInvitaciones] = useState(null);
  const [tab, setTab] = useState("carnets");
  const [modalCarnet, setModalCarnet] = useState(false);
  const [modalRegistro, setModalRegistro] = useState(false);
  const [formCarnet, setFormCarnet] = useState({ vecino_id: "", numero_carnet: "", activo: true });
  const [formRegistro, setFormRegistro] = useState({ vecino_id: "", tipo: "propio", nombre_invitado: "" });
  const [configInvitaciones, setConfigInvitaciones] = useState(10);
  const [err, setErr] = useState("");
  const [enviando, setEnviando] = useState(false);

  const load = () => {
    Promise.all([
      api.piscina.carnets.list(),
      api.vecinos.list(),
      api.piscina.registros.list()
    ]).then(([c, v, r]) => {
      setCarnets(c);
      setVecinos(v);
      setRegistros(r);
    }).catch(() => {});
  };
  useEffect(() => { load(); }, []);

  const crearCarnet = async () => {
    setErr("");
    setEnviando(true);
    try {
      await api.piscina.carnets.create(formCarnet);
      setModalCarnet(false);
      setFormCarnet({ vecino_id: "", numero_carnet: "", activo: true });
      load();
    } catch (e) {
      setErr(e.message || "No se pudo crear el carnet");
    } finally {
      setEnviando(false);
    }
  };

  const registrarAcceso = async () => {
    setErr("");
    setEnviando(true);
    try {
      await api.piscina.registros.create(formRegistro);
      setModalRegistro(false);
      setFormRegistro({ vecino_id: "", tipo: "propio", nombre_invitado: "" });
      load();
    } catch (e) {
      setErr(e.message || "No se pudo registrar el acceso");
    } finally {
      setEnviando(false);
    }
  };

  const verificarCarnet = async (numero) => {
    try {
      const res = await api.piscina.carnets.verificar(numero);
      alert(`✅ Carnet válido\nVecino: ${res.nombre}\nPiso: ${res.piso}`);
    } catch (e) {
      alert(`❌ ${e.message || "Carnet no válido"}`);
    }
  };

  const verSaldoInvitaciones = async (vecinoId) => {
    try {
      const res = await api.piscina.invitaciones.saldo(vecinoId);
      setSaldoInvitaciones(res);
    } catch {
      alert("Error al consultar saldo");
    }
  };

  const actualizarConfig = async () => {
    await api.piscina.invitaciones.config(configInvitaciones);
    alert(`Configuración actualizada a ${configInvitaciones} invitaciones/mes`);
  };

  const vecinoPorId = (id) => vecinos.find(v => v.id === id);

  return (
    <div>
      <div className="grid-3" style={{ marginBottom: 16 }}>
        <div className="metric">
          <div className="metric-label">Total carnets</div>
          <div className="metric-value">{carnets.length}</div>
        </div>
        <div className="metric">
          <div className="metric-label">Activos</div>
          <div className="metric-value" style={{ color: "#16a34a" }}>{carnets.filter(c => c.activo).length}</div>
        </div>
        <div className="metric">
          <div className="metric-label">Accesos hoy</div>
          <div className="metric-value" style={{ color: "#2563eb" }}>
            {registros.filter(r => new Date(r.fecha_hora).toDateString() === new Date().toDateString()).length}
          </div>
        </div>
      </div>

      <div style={{ display: "flex", gap: 8, marginBottom: 14, flexWrap: "wrap" }}>
        {[
          { key: "carnets", label: "🎫 Carnets" },
          { key: "registros", label: "📋 Registros" },
          { key: "config", label: "⚙️ Configuración" },
        ].map(t => (
          <button key={t.key} className={`btn ${tab === t.key ? "btn-primary" : ""}`} onClick={() => setTab(t.key)}>
            {t.label}
          </button>
        ))}
        <button className="btn btn-primary" style={{ marginLeft: "auto" }} onClick={() => { setModalRegistro(true); setErr(""); }}>+ Registrar acceso</button>
      </div>

      {tab === "carnets" && (
        <div>
          <div style={{ display: "flex", justifyContent: "flex-end", marginBottom: 14 }}>
            <button className="btn btn-primary btn-sm" onClick={() => { setModalCarnet(true); setErr(""); }}>+ Generar carnet</button>
          </div>
          <div className="card" style={{ padding: 0, overflow: "hidden" }}>
            <table className="table">
              <thead>
                <tr>
                  <th style={{ paddingLeft: 16 }}>Vecino</th>
                  <th>Piso</th>
                  <th>Nº Carnet</th>
                  <th>Estado</th>
                  <th>Expedición</th>
                  <th></th>
                </tr>
              </thead>
              <tbody>
                {carnets.map(c => {
                  const v = vecinoPorId(c.vecino_id);
                  return (
                    <tr key={c.id}>
                      <td style={{ paddingLeft: 16 }}>{v?.nombre || "—"}</td>
                      <td>{v?.piso || "—"}</td>
                      <td style={{ fontFamily: "monospace", fontWeight: 600, color: "var(--accent)" }}>{c.numero_carnet}</td>
                      <td><span className={`badge ${c.activo ? "badge-green" : "badge-gray"}`}>{c.activo ? "Activo" : "Inactivo"}</span></td>
                      <td style={{ fontSize: 12 }}>{fmtDate(c.fecha_expedicion)}</td>
                      <td>
                        <button className="btn btn-sm" onClick={() => verificarCarnet(c.numero_carnet)}>🔍 Verificar</button>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
            {carnets.length === 0 && (
              <div style={{ padding: 24, textAlign: "center", color: "var(--text-secondary)" }}>
                No hay carnets generados.
              </div>
            )}
          </div>
        </div>
      )}

      {tab === "registros" && (
        <div className="card" style={{ padding: 0, overflow: "hidden" }}>
          <table className="table">
            <thead>
              <tr>
                <th style={{ paddingLeft: 16 }}>Vecino</th>
                <th>Piso</th>
                <th>Tipo</th>
                <th>Invitado</th>
                <th>Fecha/Hora</th>
              </tr>
            </thead>
            <tbody>
              {registros.map(r => {
                const v = vecinoPorId(r.vecino_id);
                return (
                  <tr key={r.id}>
                    <td style={{ paddingLeft: 16 }}>{v?.nombre || "—"}</td>
                    <td>{v?.piso || "—"}</td>
                    <td><span className={`badge ${r.tipo === "propio" ? "badge-blue" : "badge-amber"}`}>{r.tipo}</span></td>
                    <td>{r.nombre_invitado || "—"}</td>
                    <td style={{ fontSize: 12 }}>{fmtDate(r.fecha_hora)}</td>
                  </tr>
                );
              })}
            </tbody>
          </table>
          {registros.length === 0 && (
            <div style={{ padding: 24, textAlign: "center", color: "var(--text-secondary)" }}>
              No hay registros de acceso.
            </div>
          )}
        </div>
      )}

      {tab === "config" && (
        <div className="card">
          <h3 style={{ marginBottom: 12 }}>⚙️ Configuración de invitaciones</h3>
          <div className="form-row">
            <div className="form-group">
              <label>Invitaciones por vecino/mes</label>
              <input type="number" value={configInvitaciones} onChange={e => setConfigInvitaciones(parseInt(e.target.value) || 0)} min={0} />
            </div>
            <div className="form-group" style={{ display: "flex", alignItems: "flex-end" }}>
              <button className="btn btn-primary" onClick={actualizarConfig}>Actualizar</button>
            </div>
          </div>
          <p style={{ fontSize: 12, color: "var(--text-secondary)", marginTop: 8 }}>
            💡 Esta configuración afecta a las invitaciones mensuales de todos los vecinos.
          </p>
          <hr style={{ borderColor: "var(--border)", margin: "16px 0" }} />
          <h4 style={{ marginBottom: 8 }}>Consultar saldo de invitaciones</h4>
          <div className="form-row">
            <div className="form-group">
              <label>Seleccionar vecino</label>
              <select onChange={e => verSaldoInvitaciones(parseInt(e.target.value))}>
                <option value="">Seleccionar...</option>
                {vecinos.map(v => <option key={v.id} value={v.id}>{v.nombre} — {v.piso}</option>)}
              </select>
            </div>
          </div>
          {saldoInvitaciones && (
            <div style={{ background: "var(--bg-primary)", padding: 12, borderRadius: 8, marginTop: 8 }}>
              <p><strong>Saldo del mes {saldoInvitaciones.mes}/{saldoInvitaciones.anio}</strong></p>
              <p>Total: {saldoInvitaciones.total} | Usadas: {saldoInvitaciones.usadas} | Disponibles: <strong>{saldoInvitaciones.disponibles}</strong></p>
            </div>
          )}
        </div>
      )}

      {/* Modal Carnet */}
      {modalCarnet && (
        <div className="modal-bg open" onClick={e => e.target.className.includes("modal-bg") && setModalCarnet(false)}>
          <div className="modal">
            <div className="modal-head">
              <span style={{ fontSize: 15, fontWeight: 500 }}>Generar carnet de piscina</span>
              <button className="btn btn-sm" onClick={() => setModalCarnet(false)}>✕</button>
            </div>
            <div className="form-group">
              <label>Vecino *</label>
              <select value={formCarnet.vecino_id} onChange={e => setFormCarnet(f => ({ ...f, vecino_id: e.target.value }))}>
                <option value="">Seleccionar...</option>
                {vecinos.filter(v => !carnets.some(c => c.vecino_id === v.id)).map(v => (
                  <option key={v.id} value={v.id}>{v.nombre} — {v.piso}</option>
                ))}
              </select>
            </div>
            <div className="form-group">
              <label>Número de carnet (dejar en blanco para auto-generar)</label>
              <input value={formCarnet.numero_carnet} onChange={e => setFormCarnet(f => ({ ...f, numero_carnet: e.target.value }))} placeholder="Ej: P-XXXX" />
            </div>
            {err && <p style={{ color: "#ef4444", fontSize: 12, marginBottom: 8 }}>{err}</p>}
            <div style={{ display: "flex", gap: 8, justifyContent: "flex-end", marginTop: 8 }}>
              <button className="btn" onClick={() => setModalCarnet(false)}>Cancelar</button>
              <button className="btn btn-primary" onClick={crearCarnet} disabled={!formCarnet.vecino_id || enviando}>
                {enviando ? "Generando..." : "Generar"}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Modal Registro Acceso */}
      {modalRegistro && (
        <div className="modal-bg open" onClick={e => e.target.className.includes("modal-bg") && setModalRegistro(false)}>
          <div className="modal">
            <div className="modal-head">
              <span style={{ fontSize: 15, fontWeight: 500 }}>Registrar acceso a piscina</span>
              <button className="btn btn-sm" onClick={() => setModalRegistro(false)}>✕</button>
            </div>
            <div className="form-group">
              <label>Vecino *</label>
              <select value={formRegistro.vecino_id} onChange={e => setFormRegistro(f => ({ ...f, vecino_id: e.target.value }))}>
                <option value="">Seleccionar...</option>
                {vecinos.map(v => <option key={v.id} value={v.id}>{v.nombre} — {v.piso}</option>)}
              </select>
            </div>
            <div className="form-group">
              <label>Tipo de acceso</label>
              <select value={formRegistro.tipo} onChange={e => setFormRegistro(f => ({ ...f, tipo: e.target.value }))}>
                <option value="propio">Propio</option>
                <option value="invitacion">Invitación</option>
              </select>
            </div>
            {formRegistro.tipo === "invitacion" && (
              <div className="form-group">
                <label>Nombre del invitado</label>
                <input value={formRegistro.nombre_invitado} onChange={e => setFormRegistro(f => ({ ...f, nombre_invitado: e.target.value }))} placeholder="Nombre de la persona invitada" />
              </div>
            )}
            {err && <p style={{ color: "#ef4444", fontSize: 12, marginBottom: 8 }}>{err}</p>}
            <div style={{ display: "flex", gap: 8, justifyContent: "flex-end", marginTop: 8 }}>
              <button className="btn" onClick={() => setModalRegistro(false)}>Cancelar</button>
              <button className="btn btn-primary" onClick={registrarAcceso} disabled={!formRegistro.vecino_id || enviando}>
                {enviando ? "Registrando..." : "Registrar"}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}