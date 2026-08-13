import { useState, useEffect } from "react";
import { api } from "../../api/client";
import { fmtDate } from "../../utils/date";

export default function DelegacionesVoto() {
  const [items, setItems] = useState([]);
  const [vecinos, setVecinos] = useState([]);
  const [modal, setModal] = useState(false);
  const [form, setForm] = useState({ vecino_delegante_id: "", vecino_delegado_id: "", dni_delegante: "", asunto: "", fecha_validez: "", activa: true });
  const [err, setErr] = useState("");
  const [enviando, setEnviando] = useState(false);

  const load = () => Promise.all([
    api.delegacionesVoto.list(),
    api.vecinos.list()
  ]).then(([d, v]) => { setItems(d); setVecinos(v); }).catch(() => {});

  useEffect(() => { load(); }, []);

  const create = async () => {
    setErr("");
    setEnviando(true);
    try {
      await api.delegacionesVoto.create(form);
      setModal(false);
      setForm({ vecino_delegante_id: "", vecino_delegado_id: "", dni_delegante: "", asunto: "", fecha_validez: "", activa: true });
      load();
    } catch (e) {
      setErr(e.message || "No se pudo crear la delegación");
    } finally {
      setEnviando(false);
    }
  };

  const desactivar = async (id) => {
    if (window.confirm("¿Desactivar esta delegación?")) {
      await api.delegacionesVoto.desactivar(id);
      load();
    }
  };

  return (
    <div>
      <div style={{ display: "flex", justifyContent: "flex-end", marginBottom: 14 }}>
        <button className="btn btn-primary btn-sm" onClick={() => { setModal(true); setErr(""); }}>+ Nueva delegación</button>
      </div>

      <div className="card" style={{ padding: 0, overflow: "hidden" }}>
        <table className="table">
          <thead>
            <tr>
              <th style={{ paddingLeft: 16 }}>Delegante</th>
              <th>Delegado</th>
              <th>Asunto</th>
              <th>Fecha</th>
              <th>Válida hasta</th>
              <th>Estado</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            {items.map(item => {
              const delegante = vecinos.find(v => v.id === item.vecino_delegante_id);
              const delegado = vecinos.find(v => v.id === item.vecino_delegado_id);
              return (
                <tr key={item.id}>
                  <td style={{ paddingLeft: 16 }}>{delegante?.nombre || "—"} ({delegante?.piso || "—"})</td>
                  <td>{delegado?.nombre || "—"} ({delegado?.piso || "—"})</td>
                  <td>{item.asunto || "—"}</td>
                  <td style={{ fontSize: 12 }}>{fmtDate(item.fecha)}</td>
                  <td style={{ fontSize: 12 }}>{item.fecha_validez ? fmtDate(item.fecha_validez) : "Sin fecha"}</td>
                  <td>
                    <span className={`badge ${item.activa ? "badge-green" : "badge-gray"}`}>
                      {item.activa ? "Activa" : "Inactiva"}
                    </span>
                  </td>
                  <td>
                    {item.activa && (
                      <button className="btn btn-sm" onClick={() => desactivar(item.id)}>Desactivar</button>
                    )}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
        {items.length === 0 && (
          <div style={{ padding: 24, textAlign: "center", color: "var(--text-secondary)" }}>
            No hay delegaciones de voto registradas.
          </div>
        )}
      </div>

      {modal && (
        <div className="modal-bg open" onClick={e => e.target.className.includes("modal-bg") && setModal(false)}>
          <div className="modal">
            <div className="modal-head">
              <span style={{ fontSize: 15, fontWeight: 500 }}>Nueva delegación de voto</span>
              <button className="btn btn-sm" onClick={() => setModal(false)}>✕</button>
            </div>
            <div className="form-group">
              <label>Vecino que delega *</label>
              <select value={form.vecino_delegante_id} onChange={e => setForm(f => ({ ...f, vecino_delegante_id: e.target.value }))}>
                <option value="">Seleccionar...</option>
                {vecinos.map(v => <option key={v.id} value={v.id}>{v.nombre} — {v.piso}</option>)}
              </select>
            </div>
            <div className="form-group">
              <label>Vecino que recibe la delegación *</label>
              <select value={form.vecino_delegado_id} onChange={e => setForm(f => ({ ...f, vecino_delegado_id: e.target.value }))}>
                <option value="">Seleccionar...</option>
                {vecinos.map(v => <option key={v.id} value={v.id}>{v.nombre} — {v.piso}</option>)}
              </select>
            </div>
            <div className="form-group">
              <label>DNI del delegante</label>
              <input value={form.dni_delegante} onChange={e => setForm(f => ({ ...f, dni_delegante: e.target.value }))} placeholder="Opcional" />
            </div>
            <div className="form-group">
              <label>Asunto / motivo</label>
              <input value={form.asunto} onChange={e => setForm(f => ({ ...f, asunto: e.target.value }))} placeholder="Ej: Junta extraordinaria 15/06" />
            </div>
            <div className="form-group">
              <label>Fecha de validez (opcional)</label>
              <input type="datetime-local" value={form.fecha_validez} onChange={e => setForm(f => ({ ...f, fecha_validez: e.target.value }))} />
            </div>
            {err && <p style={{ color: "#ef4444", fontSize: 12, marginBottom: 8 }}>{err}</p>}
            <div style={{ display: "flex", gap: 8, justifyContent: "flex-end", marginTop: 8 }}>
              <button className="btn" onClick={() => setModal(false)}>Cancelar</button>
              <button className="btn btn-primary" onClick={create} disabled={!form.vecino_delegante_id || !form.vecino_delegado_id || enviando}>
                {enviando ? "Guardando..." : "Guardar"}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
