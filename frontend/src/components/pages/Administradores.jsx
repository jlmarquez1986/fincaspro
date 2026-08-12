import { useState, useEffect } from "react";
import { api } from "../../api/client";

export default function Administradores() {
  const [items, setItems] = useState([]);
  const [modal, setModal] = useState(false);
  const [form, setForm] = useState({ entidad: "comunidad", nombre: "", telefono: "", email: "", direccion: "", observaciones: "" });
  const [editId, setEditId] = useState(null);
  const [err, setErr] = useState("");
  const [enviando, setEnviando] = useState(false);

  const load = () => api.administradores.list().then(setItems).catch(() => {});
  useEffect(() => { load(); }, []);

  const openModal = (item = null) => {
    if (item) {
      setForm(item);
      setEditId(item.id);
    } else {
      setForm({ entidad: "comunidad", nombre: "", telefono: "", email: "", direccion: "", observaciones: "" });
      setEditId(null);
    }
    setErr("");
    setModal(true);
  };

  const save = async () => {
    setErr("");
    setEnviando(true);
    try {
      if (editId) {
        await api.administradores.update(editId, form);
      } else {
        await api.administradores.create(form);
      }
      setModal(false);
      load();
    } catch (e) {
      setErr(e.message || "No se pudo guardar");
    } finally {
      setEnviando(false);
    }
  };

  const del = async (id) => {
    if (window.confirm("¿Eliminar este administrador?")) {
      await api.administradores.delete(id);
      load();
    }
  };

  return (
    <div>
      <div style={{ display: "flex", justifyContent: "flex-end", marginBottom: 14 }}>
        <button className="btn btn-primary btn-sm" onClick={() => openModal()}>+ Añadir administrador</button>
      </div>

      <div className="card" style={{ padding: 0, overflow: "hidden" }}>
        <table className="table">
          <thead>
            <tr>
              <th style={{ paddingLeft: 16 }}>Entidad</th>
              <th>Nombre</th>
              <th>Teléfono</th>
              <th>Email</th>
              <th>Dirección</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            {items.map(item => (
              <tr key={item.id}>
                <td style={{ paddingLeft: 16, textTransform: "capitalize" }}>{item.entidad}</td>
                <td><strong>{item.nombre}</strong></td>
                <td>{item.telefono || "—"}</td>
                <td>{item.email || "—"}</td>
                <td style={{ fontSize: 12, color: "var(--text-secondary)" }}>{item.direccion || "—"}</td>
                <td>
                  <button className="btn btn-sm" onClick={() => openModal(item)}>✎</button>
                  <button className="btn btn-sm" onClick={() => del(item.id)}>🗑</button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
        {items.length === 0 && (
          <div style={{ padding: 24, textAlign: "center", color: "var(--text-secondary)" }}>
            No hay administradores registrados.
          </div>
        )}
      </div>

      {modal && (
        <div className="modal-bg open" onClick={e => e.target.className.includes("modal-bg") && setModal(false)}>
          <div className="modal">
            <div className="modal-head">
              <span style={{ fontSize: 15, fontWeight: 500 }}>{editId ? "Editar" : "Añadir"} administrador</span>
              <button className="btn btn-sm" onClick={() => setModal(false)}>✕</button>
            </div>
            <div className="form-group">
              <label>Entidad</label>
              <select value={form.entidad} onChange={e => setForm(f => ({ ...f, entidad: e.target.value }))}>
                <option value="comunidad">Comunidad</option>
                <option value="mancomunidad">Mancomunidad</option>
              </select>
            </div>
            <div className="form-group">
              <label>Nombre *</label>
              <input value={form.nombre} onChange={e => setForm(f => ({ ...f, nombre: e.target.value }))} />
            </div>
            <div className="form-row">
              <div className="form-group">
                <label>Teléfono</label>
                <input value={form.telefono} onChange={e => setForm(f => ({ ...f, telefono: e.target.value }))} />
              </div>
              <div className="form-group">
                <label>Email</label>
                <input type="email" value={form.email} onChange={e => setForm(f => ({ ...f, email: e.target.value }))} />
              </div>
            </div>
            <div className="form-group">
              <label>Dirección</label>
              <input value={form.direccion} onChange={e => setForm(f => ({ ...f, direccion: e.target.value }))} />
            </div>
            <div className="form-group">
              <label>Observaciones</label>
              <input value={form.observaciones} onChange={e => setForm(f => ({ ...f, observaciones: e.target.value }))} />
            </div>
            {err && <p style={{ color: "#ef4444", fontSize: 12, marginBottom: 8 }}>{err}</p>}
            <div style={{ display: "flex", gap: 8, justifyContent: "flex-end", marginTop: 8 }}>
              <button className="btn" onClick={() => setModal(false)}>Cancelar</button>
              <button className="btn btn-primary" onClick={save} disabled={!form.nombre || enviando}>
                {enviando ? "Guardando..." : "Guardar"}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}