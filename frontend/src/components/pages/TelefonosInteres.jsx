import { useState, useEffect } from "react";
import { api } from "../../api/client";

export default function TelefonosInteres() {
  const [items, setItems] = useState([]);
  const [modal, setModal] = useState(false);
  const [form, setForm] = useState({ nombre: "", telefono: "", descripcion: "", categoria: "" });
  const [err, setErr] = useState("");
  const [enviando, setEnviando] = useState(false);

  const load = () => api.telefonosInteres.list().then(setItems).catch(() => {});
  useEffect(() => { load(); }, []);

  const create = async () => {
    setErr("");
    setEnviando(true);
    try {
      await api.telefonosInteres.create(form);
      setModal(false);
      setForm({ nombre: "", telefono: "", descripcion: "", categoria: "" });
      load();
    } catch (e) {
      setErr(e.message || "No se pudo crear el contacto");
    } finally {
      setEnviando(false);
    }
  };

  const del = async (id) => {
    if (window.confirm("¿Eliminar este contacto?")) {
      await api.telefonosInteres.delete(id);
      load();
    }
  };

  // Agrupar por categoría
  const categorias = [...new Set(items.map(i => i.categoria || "Sin categoría"))];

  return (
    <div>
      <div style={{ display: "flex", justifyContent: "flex-end", marginBottom: 14 }}>
        <button className="btn btn-primary btn-sm" onClick={() => { setModal(true); setErr(""); }}>
          + Añadir contacto
        </button>
      </div>

      {categorias.map(cat => (
        <div key={cat} style={{ marginBottom: 16 }}>
          <h4 style={{ fontSize: 14, fontWeight: 600, color: "var(--text-secondary)", marginBottom: 8 }}>
            {cat}
          </h4>
          {items.filter(i => (i.categoria || "Sin categoría") === cat).map(item => (
            <div
              key={item.id}
              style={{
                display: "flex",
                justifyContent: "space-between",
                alignItems: "center",
                padding: "10px 14px",
                background: "var(--bg-secondary)",
                borderRadius: 8,
                marginBottom: 6,
                border: "1px solid var(--border)",
              }}
            >
              <div>
                <strong>{item.nombre}</strong>
                {item.descripcion && (
                  <span style={{ color: "var(--text-secondary)", fontSize: 12, marginLeft: 8 }}>
                    {item.descripcion}
                  </span>
                )}
              </div>
              <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
                <span style={{ fontFamily: "monospace", fontSize: 14 }}>{item.telefono}</span>
                <button className="btn btn-sm" onClick={() => del(item.id)}>🗑</button>
              </div>
            </div>
          ))}
        </div>
      ))}

      {items.length === 0 && (
        <div style={{ padding: 24, textAlign: "center", color: "var(--text-secondary)" }}>
          No hay contactos registrados.
        </div>
      )}

      {modal && (
        <div className="modal-bg open" onClick={e => e.target.className.includes("modal-bg") && setModal(false)}>
          <div className="modal">
            <div className="modal-head">
              <span style={{ fontSize: 15, fontWeight: 500 }}>Añadir contacto</span>
              <button className="btn btn-sm" onClick={() => setModal(false)}>✕</button>
            </div>
            <div className="form-group">
              <label>Nombre *</label>
              <input value={form.nombre} onChange={e => setForm(f => ({ ...f, nombre: e.target.value }))} />
            </div>
            <div className="form-group">
              <label>Teléfono *</label>
              <input value={form.telefono} onChange={e => setForm(f => ({ ...f, telefono: e.target.value }))} />
            </div>
            <div className="form-group">
              <label>Descripción</label>
              <input value={form.descripcion} onChange={e => setForm(f => ({ ...f, descripcion: e.target.value }))} placeholder="Ej: Emergencias 24h" />
            </div>
            <div className="form-group">
              <label>Categoría</label>
              <input value={form.categoria} onChange={e => setForm(f => ({ ...f, categoria: e.target.value }))} placeholder="Ej: Seguros, Ascensores, Luz, Agua..." />
            </div>
            {err && <p style={{ color: "#ef4444", fontSize: 12, marginBottom: 8 }}>{err}</p>}
            <div style={{ display: "flex", gap: 8, justifyContent: "flex-end", marginTop: 8 }}>
              <button className="btn" onClick={() => setModal(false)}>Cancelar</button>
              <button className="btn btn-primary" onClick={create} disabled={!form.nombre || !form.telefono || enviando}>
                {enviando ? "Guardando..." : "Guardar"}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}