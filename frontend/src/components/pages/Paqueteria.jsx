import { useState, useEffect } from "react";
import { api } from "../../api/client";
import { Badge } from "../../utils/helpers";
import { fmtDate } from "../../utils/date";

export default function Paqueteria() {
  const [items, setItems] = useState([]);
  const [vecinos, setVecinos] = useState([]);
  const [modal, setModal] = useState(false);
  const [form, setForm] = useState({
    remitente: "Amazon",
    vecino_id: "",
    tamanio: "mediano",
    tracking: "",
    notificado: "si",
  });
  const [err, setErr] = useState("");
  const [enviando, setEnviando] = useState(false);

  const load = () =>
    Promise.all([
      api.paquetes.list("?estado=pendiente"),
      api.vecinos.list(),
    ]).then(([p, v]) => {
      setItems(p);
      setVecinos(v);
    });

  useEffect(() => {
    load();
  }, []);

  const create = async () => {
    setErr("");
    setEnviando(true);
    try {
      await api.paquetes.create({
        ...form,
        vecino_id: parseInt(form.vecino_id),
      });
      setModal(false);
      setForm({
        remitente: "Amazon",
        vecino_id: "",
        tamanio: "mediano",
        tracking: "",
        notificado: "si",
      });
      load();
    } catch (e) {
      setErr(e.message || "No se pudo registrar el paquete");
    } finally {
      setEnviando(false);
    }
  };

  const deliver = async (id) => {
    await api.paquetes.deliver(id);
    load();
  };

  return (
    <div>
      <div style={{ display: "flex", justifyContent: "flex-end", marginBottom: 14 }}>
        <button className="btn btn-primary btn-sm" onClick={() => setModal(true)}>
          📦 Registrar paquete
        </button>
      </div>
      <div className="card" style={{ padding: 0, overflow: "hidden" }}>
        <table className="table">
          <thead>
            <tr>
              <th style={{ paddingLeft: 16 }}>Remitente</th>
              <th>Destinatario</th>
              <th>Piso</th>
              <th>Llegada</th>
              <th>Tamaño</th>
              <th>Notificado</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            {items.map((p) => {
              const v = vecinos.find((x) => x.id === p.vecino_id);
              return (
                <tr key={p.id}>
                  <td style={{ paddingLeft: 16 }}>
                    <strong>{p.remitente || "—"}</strong>
                  </td>
                  <td>{v?.nombre || "—"}</td>
                  <td>
                    <span className="badge badge-blue">{v?.piso || "—"}</span>
                  </td>
                  <td style={{ fontSize: 12, color: "var(--text-secondary)" }}>
                    {fmtDate(p.recibido_en)}
                  </td>
                  <td style={{ textTransform: "capitalize" }}>{p.tamanio}</td>
                  <td>
                    <Badge val={p.notificado === "si" ? "resuelto" : "pendiente"} />
                  </td>
                  <td>
                    <button className="btn btn-sm" onClick={() => deliver(p.id)}>
                      ✓ Entregar
                    </button>
                  </td>
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
            No hay paquetes pendientes. 🎉
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
              <span style={{ fontSize: 15, fontWeight: 500 }}>Registrar paquete</span>
              <button className="btn btn-sm" onClick={() => setModal(false)}>
                ✕
              </button>
            </div>
            <div className="form-row">
              <div className="form-group">
                <label>Destinatario *</label>
                <select
                  value={form.vecino_id}
                  onChange={(e) =>
                    setForm((f) => ({ ...f, vecino_id: e.target.value }))
                  }
                >
                  <option value="">Seleccionar...</option>
                  {vecinos.map((v) => (
                    <option key={v.id} value={v.id}>
                      {v.nombre} — {v.piso}
                    </option>
                  ))}
                </select>
              </div>
              <div className="form-group">
                <label>Remitente</label>
                <select
                  value={form.remitente}
                  onChange={(e) =>
                    setForm((f) => ({ ...f, remitente: e.target.value }))
                  }
                >
                  {["Amazon", "Correos", "Seur", "MRW", "DHL", "GLS", "Otro"].map(
                    (r) => (
                      <option key={r}>{r}</option>
                    )
                  )}
                </select>
              </div>
            </div>
            <div className="form-row">
              <div className="form-group">
                <label>Nº seguimiento</label>
                <input
                  value={form.tracking}
                  onChange={(e) =>
                    setForm((f) => ({ ...f, tracking: e.target.value }))
                  }
                  placeholder="Opcional"
                />
              </div>
              <div className="form-group">
                <label>Tamaño</label>
                <select
                  value={form.tamanio}
                  onChange={(e) =>
                    setForm((f) => ({ ...f, tamanio: e.target.value }))
                  }
                >
                  {["sobre", "pequeno", "mediano", "grande"].map((t) => (
                    <option key={t}>{t}</option>
                  ))}
                </select>
              </div>
            </div>
            {err && (
              <p style={{ color: "#ef4444", fontSize: 12, marginBottom: 8 }}>
                {err}
              </p>
            )}
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
                disabled={!form.vecino_id || enviando}
              >
                {enviando ? "Registrando..." : "Registrar"}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

