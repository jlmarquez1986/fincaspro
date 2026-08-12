import { useState, useEffect } from "react";
import { api } from "../../api/client";
import { Badge, fmtDate } from "../../utils/helpers";

const BORDER = { info: "#2563eb", aviso: "#f59e0b", urgente: "#ef4444" };

export default function PortalVecino({ onLogout }) {
  const [me, setMe] = useState(null);
  const [tickets, setTickets] = useState([]);
  const [paquetes, setPaquetes] = useState([]);
  const [avisos, setAvisos] = useState([]);
  const [tab, setTab] = useState("tickets");
  const [modal, setModal] = useState(false);
  const [form, setForm] = useState({ asunto: "", descripcion: "", categoria: "fontaneria" });
  const [photo, setPhoto] = useState(null);
  const [photoPreview, setPhotoPreview] = useState(null);
  const [enviando, setEnviando] = useState(false);
  const [err, setErr] = useState("");

  const loadTickets = () => api.portal.misTickets().then(setTickets).catch(() => {});

  useEffect(() => {
    api.portal.me().then(setMe).catch(() => {});
    loadTickets();
    api.portal.misPaquetes().then(setPaquetes).catch(() => {});
    api.portal.avisos().then(setAvisos).catch(() => {});
  }, []);

  const handlePhotoChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      setPhoto(file);
      setPhotoPreview(URL.createObjectURL(file));
    }
  };

  const cerrarModal = () => {
    setModal(false);
    setForm({ asunto: "", descripcion: "", categoria: "fontaneria" });
    setPhoto(null);
    setPhotoPreview(null);
    setErr("");
  };

  const reportarAveria = async () => {
    setErr("");
    setEnviando(true);
    try {
      const fd = new FormData();
      fd.append("asunto", form.asunto);
      fd.append("descripcion", form.descripcion);
      fd.append("categoria", form.categoria);
      if (photo) fd.append("foto", photo);
      await api.portal.reportarAveria(fd);
      cerrarModal();
      setTab("tickets");
      loadTickets();
    } catch (e) {
      setErr(e.message || "No se pudo enviar el reporte");
    } finally {
      setEnviando(false);
    }
  };

  if (!me) return <div style={{ padding: 40, textAlign: "center", color: "var(--text-secondary)" }}>Cargando portal...</div>;

  return (
    <div style={{ maxWidth: 800, margin: "0 auto", padding: 24 }}>
      <div className="portal-card">
        <div className="portal-header">
          <div className="portal-avatar">{me.nombre?.slice(0, 2).toUpperCase()}</div>
          <div>
            <h2 style={{ fontSize: 18, fontWeight: 600 }}>Hola, {me.nombre}</h2>
            <p style={{ color: "var(--text-secondary)", fontSize: 13 }}>
              {me.piso} · {me.email}
            </p>
          </div>
          <button className="btn btn-sm" style={{ marginLeft: "auto" }} onClick={onLogout}>
            ⎋ Salir
          </button>
        </div>

        <div style={{ display: "flex", gap: 8, marginBottom: 16, flexWrap: "wrap" }}>
          {[
            { key: "tickets", label: `🔧 Mis Tickets (${tickets.length})` },
            { key: "paquetes", label: `📦 Mis Paquetes (${paquetes.length})` },
            { key: "avisos", label: "📢 Avisos" },
          ].map((t) => (
            <button
              key={t.key}
              className={`btn ${tab === t.key ? "btn-primary" : ""}`}
              onClick={() => setTab(t.key)}
            >
              {t.label}
            </button>
          ))}
          <button
            className="btn btn-primary"
            style={{ marginLeft: "auto", background: "#16a34a", borderColor: "#16a34a" }}
            onClick={() => setModal(true)}
          >
            + Reportar avería
          </button>
        </div>

        {tab === "tickets" && (
          <div>
            {tickets.length === 0 ? (
              <p style={{ color: "var(--text-secondary)", textAlign: "center", padding: 20 }}>
                No tienes tickets registrados.
              </p>
            ) : (
              tickets.map((t) => (
                <div
                  key={t.id}
                  style={{
                    borderLeft: `3px solid ${
                      t.estado === "resuelto"
                        ? "#16a34a"
                        : t.estado === "en_proceso"
                        ? "#d97706"
                        : "#2563eb"
                    }`,
                    padding: "10px 12px",
                    background: "var(--bg-primary)",
                    borderRadius: "0 6px 6px 0",
                    marginBottom: 8,
                  }}
                >
                  <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                    <span style={{ fontWeight: 500 }}>{t.asunto}</span>
                    <Badge val={t.estado} />
                  </div>
                  <p style={{ fontSize: 12, color: "var(--text-secondary)", marginTop: 4 }}>
                    {t.categoria} · {t.piso} · {fmtDate(t.creado_en)}
                  </p>
                  {t.foto_path && <p style={{ fontSize: 12, marginTop: 4 }}>📸 Tiene foto adjunta</p>}
                </div>
              ))
            )}
          </div>
        )}

        {tab === "paquetes" && (
          <div>
            {paquetes.length === 0 ? (
              <p style={{ color: "var(--text-secondary)", textAlign: "center", padding: 20 }}>
                No tienes paquetes registrados.
              </p>
            ) : (
              paquetes.map((p) => (
                <div
                  key={p.id}
                  style={{
                    padding: "10px 12px",
                    background: "var(--bg-primary)",
                    borderRadius: 6,
                    marginBottom: 8,
                  }}
                >
                  <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                    <span style={{ fontWeight: 500 }}>📦 {p.remitente || "Remitente desconocido"}</span>
                    <Badge val={p.estado} />
                  </div>
                  <p style={{ fontSize: 12, color: "var(--text-secondary)", marginTop: 4 }}>
                    Tamaño: {p.tamanio} · Recibido: {fmtDate(p.recibido_en)}
                  </p>
                </div>
              ))
            )}
          </div>
        )}

        {tab === "avisos" && (
          <div>
            {avisos.length === 0 ? (
              <p style={{ color: "var(--text-secondary)", textAlign: "center", padding: 20 }}>
                No hay avisos activos.
              </p>
            ) : (
              avisos.map((a) => (
                <div
                  key={a.id}
                  style={{
                    borderLeft: `3px solid ${BORDER[a.tipo] || "#2563eb"}`,
                    padding: "10px 12px",
                    background: "var(--bg-primary)",
                    borderRadius: "0 6px 6px 0",
                    marginBottom: 8,
                  }}
                >
                  <div style={{ fontWeight: 500, marginBottom: 4 }}>{a.titulo}</div>
                  <div style={{ fontSize: 13, color: "var(--text-secondary)" }}>{a.contenido}</div>
                  <div style={{ fontSize: 11, color: "var(--text-tertiary)", marginTop: 4 }}>
                    {fmtDate(a.creado_en)}
                  </div>
                </div>
              ))
            )}
          </div>
        )}
      </div>

      {modal && (
        <div className="modal-bg open" onClick={(e) => e.target.className.includes("modal-bg") && cerrarModal()}>
          <div className="modal">
            <div className="modal-head">
              <span style={{ fontSize: 15, fontWeight: 500 }}>Reportar avería</span>
              <button className="btn btn-sm" onClick={cerrarModal}>
                ✕
              </button>
            </div>
            <div className="form-group">
              <label>Asunto *</label>
              <input
                value={form.asunto}
                onChange={(e) => setForm((f) => ({ ...f, asunto: e.target.value }))}
                placeholder="Ej: Fuga de agua en el baño"
              />
            </div>
            <div className="form-group">
              <label>Categoría</label>
              <select
                value={form.categoria}
                onChange={(e) => setForm((f) => ({ ...f, categoria: e.target.value }))}
              >
                {["fontaneria", "electricidad", "cerrajeria", "ascensor", "otros"].map((c) => (
                  <option key={c} value={c}>
                    {c}
                  </option>
                ))}
              </select>
            </div>
            <div className="form-group">
              <label>Descripción</label>
              <textarea
                value={form.descripcion}
                onChange={(e) => setForm((f) => ({ ...f, descripcion: e.target.value }))}
                rows={3}
                placeholder="Cuéntanos qué ha pasado..."
              />
            </div>
            <div className="form-group">
              <label>Foto (opcional)</label>
              <div
                className="photo-upload-area"
                onClick={() => document.getElementById("portal-ticket-photo").click()}
              >
                {photoPreview ? (
                  <img src={photoPreview} alt="Preview" style={{ maxWidth: 200, maxHeight: 120, borderRadius: 6 }} />
                ) : (
                  <span>📷 Haz clic para subir una foto</span>
                )}
              </div>
              <input
                id="portal-ticket-photo"
                type="file"
                accept=".jpg,.jpeg,.png,.webp"
                style={{ display: "none" }}
                onChange={handlePhotoChange}
              />
              {photo && (
                <p style={{ fontSize: 11, color: "var(--text-secondary)", marginTop: 4 }}>
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
            <p style={{ fontSize: 11, color: "var(--text-tertiary)", marginTop: -4, marginBottom: 8 }}>
              Se registrará automáticamente a tu nombre y en tu piso ({me.piso}).
            </p>
            {err && (
              <p style={{ color: "#ef4444", fontSize: 12, marginBottom: 8 }}>{err}</p>
            )}
            <div style={{ display: "flex", gap: 8, justifyContent: "flex-end", marginTop: 8 }}>
              <button className="btn" onClick={cerrarModal}>
                Cancelar
              </button>
              <button
                className="btn btn-primary"
                style={{ background: "#16a34a", borderColor: "#16a34a" }}
                onClick={reportarAveria}
                disabled={!form.asunto || enviando}
              >
                {enviando ? "Enviando..." : "Enviar reporte"}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}