import { useState, useEffect, useCallback } from "react";
import { api } from "../../api/client";
import { Badge } from "../../utils/helpers";
import { fmtDate } from "../../utils/date";

export default function Tickets() {
  const [allItems, setAllItems] = useState([]); // Todos los tickets (sin filtrar)
  const [items, setItems] = useState([]);       // Tickets filtrados (para mostrar)
  const [filter, setFilter] = useState("");
  const [modal, setModal] = useState(false);
  const [detail, setDetail] = useState(null);
  const [form, setForm] = useState({
    asunto: "",
    descripcion: "",
    categoria: "fontaneria",
    prioridad: "normal",
    piso: "",
    asignado_a: "",
    vecino_id: "",
  });
  const [photo, setPhoto] = useState(null);
  const [photoPreview, setPhotoPreview] = useState(null);
  const [vecinos, setVecinos] = useState([]);
  const [err, setErr] = useState("");

  // Cargar todos los tickets y vecinos
  const loadAll = useCallback(() => {
  api.tickets.list().then(setAllItems);
  api.vecinos.list().then(setVecinos);
}, []);

  useEffect(() => {
  loadAll();
}, [loadAll]); // Solo al montar

  // Cuando cambia el filtro, filtrar sobre allItems
  useEffect(() => {
    if (filter) {
      setItems(allItems.filter((t) => t.estado === filter));
    } else {
      setItems(allItems);
    }
  }, [filter, allItems]);

  const handlePhotoChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      setPhoto(file);
      setPhotoPreview(URL.createObjectURL(file));
    }
  };

  const create = async () => {
    setErr("");
    try {
      if (photo) {
        const fd = new FormData();
        fd.append("asunto", form.asunto);
        fd.append("descripcion", form.descripcion);
        fd.append("categoria", form.categoria);
        fd.append("prioridad", form.prioridad);
        fd.append("piso", form.piso);
        if (form.vecino_id) fd.append("vecino_id", form.vecino_id);
        fd.append("asignado_a", form.asignado_a);
        fd.append("foto", photo);
        await api.tickets.createWithPhoto(fd);
      } else {
        await api.tickets.create(form);
      }
      // Éxito: cerrar modal, resetear y recargar
      setModal(false);
      setForm({
        asunto: "",
        descripcion: "",
        categoria: "fontaneria",
        prioridad: "normal",
        piso: "",
        asignado_a: "",
        vecino_id: "",
      });
      setPhoto(null);
      setPhotoPreview(null);
      loadAll(); // Recargar todos los tickets
    } catch (e) {
      setErr(e.message || "Error al crear el ticket");
    }
  };

  const cambiarEstado = async (id, estado) => {
    await api.tickets.update(id, { estado });
    if (detail?.id === id) setDetail((d) => ({ ...d, estado }));
    loadAll(); // Recargar todos los tickets
  };

  if (detail) {
    return (
      <div>
        <button
          className="btn btn-sm"
          onClick={() => setDetail(null)}
          style={{ marginBottom: 14 }}
        >
          ← Volver
        </button>
        <div className="card">
          <div
            style={{
              display: "flex",
              alignItems: "flex-start",
              justifyContent: "space-between",
              gap: 12,
              marginBottom: 16,
            }}
          >
            <div>
              <h3 style={{ fontSize: 16, fontWeight: 600 }}>{detail.asunto}</h3>
              <div
                style={{
                  fontSize: 12,
                  color: "var(--text-secondary)",
                  marginTop: 4,
                }}
              >
                #{detail.id} · {detail.piso} · {fmtDate(detail.creado_en)}
              </div>
            </div>
            <Badge val={detail.estado} />
          </div>
          <p style={{ fontSize: 13, color: "var(--text-secondary)", marginBottom: 16 }}>
            {detail.descripcion || "Sin descripción."}
          </p>
          {detail.foto_path && (
            <div style={{ marginBottom: 16 }}>
              <div
                style={{
                  fontSize: 12,
                  color: "var(--text-secondary)",
                  marginBottom: 6,
                }}
              >
                📸 Foto adjunta:
              </div>
              <img
                src={detail.foto_path}
                alt="Foto del ticket"
                style={{
                  maxWidth: "100%",
                  maxHeight: 300,
                  borderRadius: 8,
                  border: "1px solid var(--border)",
                }}
              />
            </div>
          )}
          <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
            {["pendiente", "en_proceso", "resuelto", "cancelado"].map((e) => (
              <button
                key={e}
                className={`btn btn-sm ${detail.estado === e ? "btn-primary" : ""}`}
                onClick={() => cambiarEstado(detail.id, e)}
              >
                {e.replace("_", " ")}
              </button>
            ))}
          </div>
        </div>
      </div>
    );
  }

  // Calcular contadores usando allItems (sin filtrar)
  const totalCount = allItems.length;
  const pendienteCount = allItems.filter((t) => t.estado === "pendiente").length;
  const enProcesoCount = allItems.filter((t) => t.estado === "en_proceso").length;
  const resueltoCount = allItems.filter((t) => t.estado === "resuelto").length;
  const canceladoCount = allItems.filter((t) => t.estado === "cancelado").length;

  return (
    <div>
      <div
        style={{
          display: "flex",
          gap: 8,
          marginBottom: 14,
          flexWrap: "wrap",
          alignItems: "center",
        }}
      >
        <span
          className={`filter-chip ${filter === "" ? "on" : ""}`}
          onClick={() => setFilter("")}
        >
          Todos ({totalCount})
        </span>
        <span
          className={`filter-chip ${filter === "pendiente" ? "on" : ""}`}
          onClick={() => setFilter("pendiente")}
        >
          Pendiente ({pendienteCount})
        </span>
        <span
          className={`filter-chip ${filter === "en_proceso" ? "on" : ""}`}
          onClick={() => setFilter("en_proceso")}
        >
          En proceso ({enProcesoCount})
        </span>
        <span
          className={`filter-chip ${filter === "resuelto" ? "on" : ""}`}
          onClick={() => setFilter("resuelto")}
        >
          Resuelto ({resueltoCount})
        </span>
        <span
          className={`filter-chip ${filter === "cancelado" ? "on" : ""}`}
          onClick={() => setFilter("cancelado")}
        >
          Cancelado ({canceladoCount})
        </span>
        <button
          className="btn btn-primary btn-sm"
          style={{ marginLeft: "auto" }}
          onClick={() => setModal(true)}
        >
          + Nueva avería
        </button>
      </div>

      <div className="card" style={{ padding: 0, overflow: "hidden" }}>
        <table className="table">
          <thead>
            <tr>
              <th style={{ paddingLeft: 16 }}>ID</th>
              <th>Asunto</th>
              <th>Piso</th>
              <th>Categoría</th>
              <th>Prioridad</th>
              <th>Estado</th>
              <th>Foto</th>
              <th>Fecha</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            {items.map((t) => {
              return (
                <tr
                  key={t.id}
                  className="ticket-row"
                  onClick={() => setDetail(t)}
                >
                  <td style={{ paddingLeft: 16, color: "var(--text-secondary)" }}>
                    #{t.id}
                  </td>
                  <td
                    style={{
                      maxWidth: 200,
                      overflow: "hidden",
                      textOverflow: "ellipsis",
                      whiteSpace: "nowrap",
                    }}
                  >
                    {t.asunto}
                  </td>
                  <td>{t.piso || "—"}</td>
                  <td style={{ textTransform: "capitalize" }}>{t.categoria}</td>
                  <td>
                    <Badge val={t.prioridad} />
                  </td>
                  <td>
                    <Badge val={t.estado} />
                  </td>
                  <td>{t.foto_path ? "📸" : "—"}</td>
                  <td style={{ color: "var(--text-secondary)", fontSize: 12 }}>
                    {fmtDate(t.creado_en)}
                  </td>
                  <td style={{ color: "var(--text-tertiary)" }}>›</td>
                </tr>
              );
            })}
          </tbody>
        </table>
        {items.length === 0 && (
          <div
            style={{
              padding: 24,
              textAlign: "center",
              color: "var(--text-secondary)",
            }}
          >
            No hay tickets con este filtro.
          </div>
        )}
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
              <span style={{ fontSize: 15, fontWeight: 500 }}>Nueva avería</span>
              <button className="btn btn-sm" onClick={() => setModal(false)}>
                ✕
              </button>
            </div>
            <div className="form-row">
              <div className="form-group">
                <label>Piso / Zona</label>
                <input
                  value={form.piso}
                  onChange={(e) =>
                    setForm((f) => ({ ...f, piso: e.target.value }))
                  }
                  placeholder="Ej: 3B, Comunal..."
                />
              </div>
              <div className="form-group">
                <label>Categoría</label>
                <select
                  value={form.categoria}
                  onChange={(e) =>
                    setForm((f) => ({ ...f, categoria: e.target.value }))
                  }
                >
                  {["fontaneria", "electricidad", "cerrajeria", "ascensor", "otros"].map(
                    (c) => (
                      <option key={c} value={c}>
                        {c}
                      </option>
                    )
                  )}
                </select>
              </div>
            </div>
            <div className="form-group">
              <label>Asunto *</label>
              <input
                value={form.asunto}
                onChange={(e) =>
                  setForm((f) => ({ ...f, asunto: e.target.value }))
                }
                placeholder="Descripción breve..."
              />
            </div>
            <div className="form-group">
              <label>Descripción</label>
              <textarea
                value={form.descripcion}
                onChange={(e) =>
                  setForm((f) => ({ ...f, descripcion: e.target.value }))
                }
                rows={3}
              />
            </div>
            <div className="form-row">
              <div className="form-group">
                <label>Prioridad</label>
                <select
                  value={form.prioridad}
                  onChange={(e) =>
                    setForm((f) => ({ ...f, prioridad: e.target.value }))
                  }
                >
                  {["urgente", "media", "normal", "baja"].map((p) => (
                    <option key={p} value={p}>
                      {p}
                    </option>
                  ))}
                </select>
              </div>
              <div className="form-group">
                <label>Asignar a</label>
                <input
                  value={form.asignado_a}
                  onChange={(e) =>
                    setForm((f) => ({ ...f, asignado_a: e.target.value }))
                  }
                  placeholder="Nombre o empresa..."
                />
              </div>
            </div>
            <div className="form-group">
              <label>Vecino afectado</label>
              <select
                value={form.vecino_id}
                onChange={(e) =>
                  setForm((f) => ({ ...f, vecino_id: e.target.value }))
                }
              >
                <option value="">Sin vecino asignado</option>
                {vecinos.map((v) => (
                  <option key={v.id} value={v.id}>
                    {v.nombre} — {v.piso}
                  </option>
                ))}
              </select>
            </div>
            <div className="form-group">
              <label>Foto (opcional)</label>
              <div
                className="photo-upload-area"
                onClick={() => document.getElementById("ticket-photo").click()}
              >
                {photoPreview ? (
                  <img
                    src={photoPreview}
                    alt="Preview"
                    style={{ maxWidth: 200, maxHeight: 120, borderRadius: 6 }}
                  />
                ) : (
                  <span>📷 Haz clic para subir una foto</span>
                )}
              </div>
              <input
                id="ticket-photo"
                type="file"
                accept=".jpg,.jpeg,.png,.webp"
                style={{ display: "none" }}
                onChange={handlePhotoChange}
              />
              {photo && (
                <p
                  style={{
                    fontSize: 11,
                    color: "var(--text-secondary)",
                    marginTop: 4,
                  }}
                >
                  {photo.name}{" "}
                  <span
                    style={{ cursor: "pointer", color: "#ef4444" }}
                    onClick={() => {
                      setPhoto(null);
                      setPhotoPreview(null);
                    }}
                  >
                    ✕
                  </span>
                </p>
              )}
            </div>
            {err && <p style={{ color: "#ef4444", fontSize: 12, marginBottom: 8 }}>{err}</p>}
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
                disabled={!form.asunto}
              >
                Crear ticket
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

