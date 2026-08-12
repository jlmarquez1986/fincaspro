import { useState, useEffect } from "react";
import { api } from "../../api/client";
import { Badge } from "../../utils/helpers";

export default function Vecinos() {
  const [items, setItems] = useState([]);
  const [modal, setModal] = useState(false);
  const [form, setForm] = useState({
    nombre: "",
    email: "",
    telefono: "",
    piso: "",
    tipo: "propietario",
  });

  const load = () => api.vecinos.list().then(setItems);
  useEffect(() => {
    load();
  }, []);

  const create = async () => {
    await api.vecinos.create(form);
    setModal(false);
    setForm({
      nombre: "",
      email: "",
      telefono: "",
      piso: "",
      tipo: "propietario",
    });
    load();
  };

  return (
    <div>
      <div style={{ display: "flex", justifyContent: "flex-end", marginBottom: 14 }}>
        <button className="btn btn-primary btn-sm" onClick={() => setModal(true)}>
          + Añadir vecino
        </button>
      </div>
      <div className="card" style={{ padding: 0, overflow: "hidden" }}>
        <table className="table">
          <thead>
            <tr>
              <th style={{ paddingLeft: 16 }}>Nombre</th>
              <th>Piso</th>
              <th>Teléfono</th>
              <th>Email</th>
              <th>Tipo</th>
              <th>Portal</th>
            </tr>
          </thead>
          <tbody>
            {items.map((v) => {
              const portalStatus = v.portal_activo === "true" ? "✅ Activo" : "—";
              return (
                <tr key={v.id}>
                  <td style={{ paddingLeft: 16 }}>
                    <strong>{v.nombre}</strong>
                  </td>
                  <td>
                    <span className="badge badge-blue">{v.piso}</span>
                  </td>
                  <td style={{ color: "var(--text-secondary)" }}>
                    {v.telefono || "—"}
                  </td>
                  <td style={{ color: "var(--text-secondary)", fontSize: 12 }}>
                    {v.email || "—"}
                  </td>
                  <td>
                    <Badge val={v.tipo} />
                  </td>
                  <td style={{ fontSize: 12 }}>{portalStatus}</td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
      {modal && (
        <div
          className="modal-bg open"
          onClick={(e) =>
            e.target.className.includes("modal-bg") && setModal(false)
          }
        >
          <div className="modal">
            <div className="modal-head">
              <span style={{ fontSize: 15, fontWeight: 500 }}>Añadir vecino</span>
              <button className="btn btn-sm" onClick={() => setModal(false)}>
                ✕
              </button>
            </div>
            <div className="form-row">
              <div className="form-group">
                <label>Nombre *</label>
                <input
                  value={form.nombre}
                  onChange={(e) =>
                    setForm((f) => ({ ...f, nombre: e.target.value }))
                  }
                />
              </div>
              <div className="form-group">
                <label>Piso *</label>
                <input
                  value={form.piso}
                  onChange={(e) =>
                    setForm((f) => ({ ...f, piso: e.target.value }))
                  }
                  placeholder="Ej: 3B"
                />
              </div>
            </div>
            <div className="form-row">
              <div className="form-group">
                <label>Teléfono</label>
                <input
                  value={form.telefono}
                  onChange={(e) =>
                    setForm((f) => ({ ...f, telefono: e.target.value }))
                  }
                />
              </div>
              <div className="form-group">
                <label>Email</label>
                <input
                  value={form.email}
                  onChange={(e) =>
                    setForm((f) => ({ ...f, email: e.target.value }))
                  }
                />
              </div>
            </div>
            <div className="form-group">
              <label>Tipo</label>
              <select
                value={form.tipo}
                onChange={(e) =>
                  setForm((f) => ({ ...f, tipo: e.target.value }))
                }
              >
                <option value="propietario">Propietario</option>
                <option value="inquilino">Inquilino</option>
              </select>
            </div>
            <div
              style={{
                display: "flex",
                gap: 8,
                justifyContent: "flex-end",
                marginTop: 8,
              }}
            >
              <button className="btn" onClick={() => setModal(false)}>
                Cancelar
              </button>
              <button
                className="btn btn-primary"
                onClick={create}
                disabled={!form.nombre || !form.piso}
              >
                Guardar
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}