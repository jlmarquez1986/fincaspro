import { useState, useEffect } from "react";
import { api } from "../../api/client";
import { Badge, fmtDate } from "../../utils/helpers";

export default function Llaves() {
  const [items, setItems] = useState([]);
  const [modalPrestar, setModalPrestar] = useState(null);
  const [prestadaA, setPrestadaA] = useState("");
  const [modalNueva, setModalNueva] = useState(false);
  const [nueva, setNueva] = useState({
    nombre: "",
    codigo: "",
    descripcion: "",
  });
  const [err, setErr] = useState("");
  const [enviando, setEnviando] = useState(false);

  const load = () =>
    api.llaves.list().then((l) => {
      setItems(l);
    });

  useEffect(() => {
    load();
  }, []);

  const prestar = async () => {
    await api.llaves.prestar(modalPrestar, { prestada_a: prestadaA });
    setModalPrestar(null);
    setPrestadaA("");
    load();
  };

  const devolver = async (id) => {
    await api.llaves.devolver(id);
    load();
  };

  const crearLlave = async () => {
    setErr("");
    setEnviando(true);
    try {
      await api.llaves.create(nueva);
      setModalNueva(false);
      setNueva({ nombre: "", codigo: "", descripcion: "" });
      load();
    } catch (e) {
      setErr(e.message || "No se pudo crear la llave. Comprueba que el código no esté ya en uso.");
    } finally {
      setEnviando(false);
    }
  };

  const disponibles = items.filter((l) => l.estado === "disponible").length;
  const prestadas = items.filter((l) => l.estado === "prestada").length;

  return (
    <div>
      <div className="grid-3" style={{ marginBottom: 16 }}>
        <div className="metric">
          <div className="metric-label">Total llaves</div>
          <div className="metric-value">{items.length}</div>
        </div>
        <div className="metric">
          <div className="metric-label">Prestadas</div>
          <div className="metric-value" style={{ color: "#d97706" }}>
            {prestadas}
          </div>
        </div>
        <div className="metric">
          <div className="metric-label">Disponibles</div>
          <div className="metric-value" style={{ color: "#16a34a" }}>
            {disponibles}
          </div>
        </div>
      </div>
      <div style={{ display: "flex", justifyContent: "flex-end", marginBottom: 14 }}>
        <button
          className="btn btn-primary btn-sm"
          onClick={() => {
            setModalNueva(true);
            setErr("");
          }}
        >
          + Añadir llave
        </button>
      </div>
      <div className="card" style={{ padding: 0, overflow: "hidden" }}>
        <table className="table">
          <thead>
            <tr>
              <th style={{ paddingLeft: 16 }}>Código</th>
              <th>Nombre</th>
              <th>Estado</th>
              <th>Prestada a</th>
              <th>Desde</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            {items.length === 0 && (
              <tr>
                <td
                  colSpan={6}
                  style={{
                    padding: 20,
                    textAlign: "center",
                    color: "var(--text-secondary)",
                  }}
                >
                  Aún no hay llaves registradas. Usa &ldquo;+ Añadir llave&rdquo; para dar de alta la
                  primera.
                </td>
              </tr>
            )}
            {items.map((l) => {
              return (
                <tr key={l.id}>
                  <td
                    style={{
                      paddingLeft: 16,
                      fontFamily: "monospace",
                      fontWeight: 600,
                      color: "var(--accent)",
                    }}
                  >
                    {l.codigo}
                  </td>
                  <td>{l.nombre}</td>
                  <td>
                    <Badge val={l.estado} />
                  </td>
                  <td style={{ color: "var(--text-secondary)" }}>
                    {l.prestada_a || "—"}
                  </td>
                  <td style={{ fontSize: 12, color: "var(--text-secondary)" }}>
                    {fmtDate(l.desde)}
                  </td>
                  <td>
                    {l.estado === "disponible" ? (
                      <button
                        className="btn btn-sm"
                        onClick={() => {
                          setModalPrestar(l.id);
                          setPrestadaA("");
                        }}
                      >
                        Prestar
                      </button>
                    ) : (
                      <button className="btn btn-sm" onClick={() => devolver(l.id)}>
                        Devolver
                      </button>
                    )}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
      {modalPrestar && (
        <div
          className="modal-bg open"
          onClick={(e) =>
            e.target.className.includes("modal-bg") && setModalPrestar(null)
          }
        >
          <div className="modal">
            <div className="modal-head">
              <span style={{ fontSize: 15, fontWeight: 500 }}>Prestar llave</span>
              <button className="btn btn-sm" onClick={() => setModalPrestar(null)}>
                ✕
              </button>
            </div>
            <div className="form-group">
              <label>Prestada a *</label>
              <input
                value={prestadaA}
                onChange={(e) => setPrestadaA(e.target.value)}
                placeholder="Nombre del vecino..."
              />
            </div>
            <div
              style={{
                display: "flex",
                gap: 8,
                justifyContent: "flex-end",
                marginTop: 8,
              }}
            >
              <button className="btn" onClick={() => setModalPrestar(null)}>
                Cancelar
              </button>
              <button
                className="btn btn-primary"
                onClick={prestar}
                disabled={!prestadaA}
              >
                Confirmar préstamo
              </button>
            </div>
          </div>
        </div>
      )}
      {modalNueva && (
        <div
          className="modal-bg open"
          onClick={(e) =>
            e.target.className.includes("modal-bg") && setModalNueva(false)
          }
        >
          <div className="modal">
            <div className="modal-head">
              <span style={{ fontSize: 15, fontWeight: 500 }}>Añadir llave</span>
              <button className="btn btn-sm" onClick={() => setModalNueva(false)}>
                ✕
              </button>
            </div>
            <div className="form-group">
              <label>Nombre *</label>
              <input
                value={nueva.nombre}
                onChange={(e) =>
                  setNueva((n) => ({ ...n, nombre: e.target.value }))
                }
                placeholder="Ej: Cuarto de contadores"
              />
            </div>
            <div className="form-group">
              <label>Código *</label>
              <input
                value={nueva.codigo}
                onChange={(e) =>
                  setNueva((n) => ({ ...n, codigo: e.target.value }))
                }
                placeholder="Ej: LL-004 (debe ser único)"
              />
            </div>
            <div className="form-group">
              <label>Descripción</label>
              <input
                value={nueva.descripcion}
                onChange={(e) =>
                  setNueva((n) => ({ ...n, descripcion: e.target.value }))
                }
                placeholder="Opcional"
              />
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
              <button className="btn" onClick={() => setModalNueva(false)}>
                Cancelar
              </button>
              <button
                className="btn btn-primary"
                onClick={crearLlave}
                disabled={!nueva.nombre || !nueva.codigo || enviando}
              >
                {enviando ? "Añadiendo..." : "Añadir"}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}