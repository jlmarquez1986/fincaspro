import { useState, useEffect } from "react";
import { api } from "../../api/client";
import { Badge } from "../../utils/helpers";
import { fmtDate } from "../../utils/date";

export default function Avisos() {
  const [items, setItems] = useState([]);
  const [modal, setModal] = useState(false);
  const [form, setForm] = useState({
    titulo: "",
    contenido: "",
    tipo: "info",
  });

  const load = () => api.avisos.list().then(setItems);
  useEffect(() => {
    load();
  }, []);

  const create = async () => {
    await api.avisos.create(form);
    setModal(false);
    setForm({ titulo: "", contenido: "", tipo: "info" });
    load();
  };

  const archive = async (id) => {
    await api.avisos.archive(id);
    load();
  };

  const BORDER = {
    info: "#2563eb",
    aviso: "#f59e0b",
    urgente: "#ef4444",
  };

  return (
    <div>
      <div style={{ display: "flex", justifyContent: "flex-end", marginBottom: 14 }}>
        <button className="btn btn-primary btn-sm" onClick={() => setModal(true)}>
          + Publicar aviso
        </button>
      </div>
      {items.map((a) => {
        const borderColor = BORDER[a.tipo] || "#2563eb";
        return (
          <div
            key={a.id}
            style={{
              borderLeft: `3px solid ${borderColor}`,
              padding: "12px 14px",
              background: "var(--bg-secondary)",
              borderRadius: "0 8px 8px 0",
              marginBottom: 10,
            }}
          >
            <div
              style={{
                display: "flex",
                justifyContent: "space-between",
                alignItems: "flex-start",
                gap: 10,
              }}
            >
              <div>
                <div style={{ fontSize: 13, fontWeight: 600, marginBottom: 4 }}>
                  {a.titulo}
                </div>
                <div style={{ fontSize: 13, color: "var(--text-primary)" }}>
                  {a.contenido}
                </div>
                <div
                  style={{
                    fontSize: 11,
                    color: "var(--text-secondary)",
                    marginTop: 6,
                  }}
                >
                  {fmtDate(a.creado_en)}
                </div>
              </div>
              <div
                style={{
                  display: "flex",
                  gap: 6,
                  alignItems: "center",
                  flexShrink: 0,
                }}
              >
                <Badge val={a.tipo} />
                <button className="btn btn-sm" onClick={() => archive(a.id)}>
                  Archivar
                </button>
              </div>
            </div>
          </div>
        );
      })}
      {items.length === 0 && (
        <div
          style={{
            padding: 24,
            textAlign: "center",
            color: "var(--text-secondary)",
          }}
        >
          No hay avisos activos.
        </div>
      )}
      {modal && (
        <div
          className="modal-bg open"
          onClick={(e) =>
            e.target.className.includes("modal-bg") && setModal(false)
          }
        >
          <div className="modal">
            <div className="modal-head">
              <span style={{ fontSize: 15, fontWeight: 500 }}>Publicar aviso</span>
              <button className="btn btn-sm" onClick={() => setModal(false)}>
                ✕
              </button>
            </div>
            <div className="form-group">
              <label>Título *</label>
              <input
                value={form.titulo}
                onChange={(e) =>
                  setForm((f) => ({ ...f, titulo: e.target.value }))
                }
              />
            </div>
            <div className="form-group">
              <label>Contenido *</label>
              <textarea
                value={form.contenido}
                onChange={(e) =>
                  setForm((f) => ({ ...f, contenido: e.target.value }))
                }
                rows={4}
              />
            </div>
            <div className="form-group">
              <label>Tipo</label>
              <select
                value={form.tipo}
                onChange={(e) =>
                  setForm((f) => ({ ...f, tipo: e.target.value }))
                }
              >
                <option value="info">Informativo</option>
                <option value="aviso">Aviso</option>
                <option value="urgente">Urgente</option>
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
                disabled={!form.titulo || !form.contenido}
              >
                Publicar
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

