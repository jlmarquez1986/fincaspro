import { useState, useEffect } from "react";
import { api } from "../../api/client";
import { Badge, fmtDate } from "../../utils/helpers";

export default function QuejasMejoras() {
  const [items, setItems] = useState([]);
  const [filter, setFilter] = useState("");
  const [modal, setModal] = useState(false);
  const [form, setForm] = useState({ tipo: "queja", categoria: "mantenimiento", asunto: "", descripcion: "", prioridad: "media", vecino_id: "" });
  const [vecinos, setVecinos] = useState([]);
  const [err, setErr] = useState("");
  const [enviando, setEnviando] = useState(false);

  const load = () => {
    const params = filter ? `?estado=${filter}` : "";
    api.quejasMejoras.list(params).then(setItems).catch(() => {});
    api.vecinos.list().then(setVecinos).catch(() => {});
  };
  useEffect(() => { load(); }, [filter]);

  const create = async () => {
    setErr("");
    setEnviando(true);
    try {
      await api.quejasMejoras.create(form);
      setModal(false);
      setForm({ tipo: "queja", categoria: "mantenimiento", asunto: "", descripcion: "", prioridad: "media", vecino_id: "" });
      load();
    } catch (e) {
      setErr(e.message || "No se pudo crear");
    } finally {
      setEnviando(false);
    }
  };

  const update = async (id, estado) => {
    await api.quejasMejoras.update(id, { estado });
    load();
  };

  const del = async (id) => {
    if (window.confirm("¿Eliminar esta queja/mejora?")) {
      await api.quejasMejoras.delete(id);
      load();
    }
  };

  const categorias = ["mantenimiento", "ascensores", "limpieza", "caldera", "piscina", "jardineria", "seguridad", "ruidos", "otros"];
  const estados = ["pendiente", "en_proceso", "resuelto", "rechazado"];
  const tipos = ["queja", "mejora"];

  return (
    <div>
      <div style={{ display: "flex", gap: 8, marginBottom: 14, flexWrap: "wrap", alignItems: "center" }}>
        {["", ...estados].map(f => {
          const count = f ? items.filter(i => i.estado === f).length : items.length;
          return (
            <span key={f} className={`filter-chip ${filter === f ? "on" : ""}`} onClick={() => setFilter(f)}>
              {f || "Todos"} ({count})
            </span>
          );
        })}
        <button className="btn btn-primary btn-sm" style={{ marginLeft: "auto" }} onClick={() => { setModal(true); setErr(""); }}>+ Nueva</button>
      </div>

      <div className="card" style={{ padding: 0, overflow: "hidden" }}>
        <table className="table">
          <thead>
            <tr>
              <th style={{ paddingLeft: 16 }}>Tipo</th>
              <th>Asunto</th>
              <th>Categoría</th>
              <th>Vecino</th>
              <th>Prioridad</th>
              <th>Estado</th>
              <th>Fecha</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            {items.map(item => {
              const vecino = vecinos.find(v => v.id === item.vecino_id);
              return (
                <tr key={item.id}>
                  <td style={{ paddingLeft: 16, textTransform: "capitalize" }}>
                    <span className={`badge ${item.tipo === "queja" ? "badge-red" : "badge-blue"}`}>
                      {item.tipo}
                    </span>
                  </td>
                  <td>{item.asunto}</td>
                  <td style={{ textTransform: "capitalize" }}>{item.categoria}</td>
                  <td>{vecino?.nombre || "—"}</td>
                  <td><Badge val={item.prioridad} /></td>
                  <td><Badge val={item.estado} /></td>
                  <td style={{ fontSize: 12, color: "var(--text-secondary)" }}>{fmtDate(item.creado_en)}</td>
                  <td>
                    <select
                      className="btn btn-sm"
                      value={item.estado}
                      onChange={e => update(item.id, e.target.value)}
                      style={{ fontSize: 11, padding: "2px 6px" }}
                    >
                      {estados.map(e => <option key={e} value={e}>{e.replace("_", " ")}</option>)}
                    </select>
                    <button className="btn btn-sm" onClick={() => del(item.id)}>🗑</button>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
        {items.length === 0 && (
          <div style={{ padding: 24, textAlign: "center", color: "var(--text-secondary)" }}>
            No hay quejas o mejoras registradas.
          </div>
        )}
      </div>

      {modal && (
        <div className="modal-bg open" onClick={e => e.target.className.includes("modal-bg") && setModal(false)}>
          <div className="modal">
            <div className="modal-head">
              <span style={{ fontSize: 15, fontWeight: 500 }}>Nueva queja / mejora</span>
              <button className="btn btn-sm" onClick={() => setModal(false)}>✕</button>
            </div>
            <div className="form-row">
              <div className="form-group">
                <label>Tipo</label>
                <select value={form.tipo} onChange={e => setForm(f => ({ ...f, tipo: e.target.value }))}>
                  {tipos.map(t => <option key={t} value={t}>{t}</option>)}
                </select>
              </div>
              <div className="form-group">
                <label>Categoría</label>
                <select value={form.categoria} onChange={e => setForm(f => ({ ...f, categoria: e.target.value }))}>
                  {categorias.map(c => <option key={c} value={c}>{c}</option>)}
                </select>
              </div>
            </div>
            <div className="form-group">
              <label>Asunto *</label>
              <input value={form.asunto} onChange={e => setForm(f => ({ ...f, asunto: e.target.value }))} />
            </div>
            <div className="form-group">
              <label>Descripción</label>
              <textarea value={form.descripcion} onChange={e => setForm(f => ({ ...f, descripcion: e.target.value }))} rows={3} />
            </div>
            <div className="form-row">
              <div className="form-group">
                <label>Prioridad</label>
                <select value={form.prioridad} onChange={e => setForm(f => ({ ...f, prioridad: e.target.value }))}>
                  {["baja", "media", "alta"].map(p => <option key={p} value={p}>{p}</option>)}
                </select>
              </div>
              <div className="form-group">
                <label>Vecino afectado</label>
                <select value={form.vecino_id} onChange={e => setForm(f => ({ ...f, vecino_id: e.target.value }))}>
                  <option value="">Sin vecino asignado</option>
                  {vecinos.map(v => <option key={v.id} value={v.id}>{v.nombre} — {v.piso}</option>)}
                </select>
              </div>
            </div>
            {err && <p style={{ color: "#ef4444", fontSize: 12, marginBottom: 8 }}>{err}</p>}
            <div style={{ display: "flex", gap: 8, justifyContent: "flex-end", marginTop: 8 }}>
              <button className="btn" onClick={() => setModal(false)}>Cancelar</button>
              <button className="btn btn-primary" onClick={create} disabled={!form.asunto || enviando}>
                {enviando ? "Guardando..." : "Guardar"}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}