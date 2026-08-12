import { useState, useEffect } from "react";
import { api } from "../../api/client";

export default function EstadosCuenta() {
  const [items, setItems] = useState([]);
  const [modal, setModal] = useState(false);
  const [form, setForm] = useState({ entidad: "comunidad", mes: new Date().getMonth() + 1, anio: new Date().getFullYear(), saldo_inicial: 0, ingresos: 0, gastos: 0, saldo_final: 0, observaciones: "" });
  const [editId, setEditId] = useState(null);
  const [err, setErr] = useState("");
  const [enviando, setEnviando] = useState(false);

  const load = () => api.estadosCuenta.list().then(setItems).catch(() => {});
  useEffect(() => { load(); }, []);

  const openModal = (item = null) => {
    if (item) {
      setForm(item);
      setEditId(item.id);
    } else {
      setForm({ entidad: "comunidad", mes: new Date().getMonth() + 1, anio: new Date().getFullYear(), saldo_inicial: 0, ingresos: 0, gastos: 0, saldo_final: 0, observaciones: "" });
      setEditId(null);
    }
    setErr("");
    setModal(true);
  };

  const save = async () => {
    setErr("");
    setEnviando(true);
    try {
      const data = { ...form, saldo_final: form.saldo_inicial + form.ingresos - form.gastos };
      if (editId) {
        await api.estadosCuenta.update(editId, data);
      } else {
        await api.estadosCuenta.create(data);
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
    if (window.confirm("¿Eliminar este registro?")) {
      await api.estadosCuenta.delete(id);
      load();
    }
  };

  const meses = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"];

  return (
    <div>
      <div style={{ display: "flex", justifyContent: "flex-end", marginBottom: 14 }}>
        <button className="btn btn-primary btn-sm" onClick={() => openModal()}>+ Nuevo registro</button>
      </div>

      <div className="card" style={{ padding: 0, overflow: "hidden" }}>
        <table className="table">
          <thead>
            <tr>
              <th style={{ paddingLeft: 16 }}>Entidad</th>
              <th>Mes / Año</th>
              <th>Saldo inicial</th>
              <th>Ingresos</th>
              <th>Gastos</th>
              <th>Saldo final</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            {items.map(item => (
              <tr key={item.id}>
                <td style={{ paddingLeft: 16, textTransform: "capitalize" }}>{item.entidad}</td>
                <td>{meses[item.mes - 1]} {item.anio}</td>
                <td>€{item.saldo_inicial.toFixed(2)}</td>
                <td style={{ color: "#16a34a" }}>+€{item.ingresos.toFixed(2)}</td>
                <td style={{ color: "#ef4444" }}>-€{item.gastos.toFixed(2)}</td>
                <td><strong>€{item.saldo_final.toFixed(2)}</strong></td>
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
            No hay registros de estados de cuenta.
          </div>
        )}
      </div>

      {modal && (
        <div className="modal-bg open" onClick={e => e.target.className.includes("modal-bg") && setModal(false)}>
          <div className="modal">
            <div className="modal-head">
              <span style={{ fontSize: 15, fontWeight: 500 }}>{editId ? "Editar" : "Nuevo"} estado de cuenta</span>
              <button className="btn btn-sm" onClick={() => setModal(false)}>✕</button>
            </div>
            <div className="form-group">
              <label>Entidad</label>
              <select value={form.entidad} onChange={e => setForm(f => ({ ...f, entidad: e.target.value }))}>
                <option value="comunidad">Comunidad</option>
                <option value="mancomunidad">Mancomunidad</option>
              </select>
            </div>
            <div className="form-row">
              <div className="form-group">
                <label>Mes</label>
                <select value={form.mes} onChange={e => setForm(f => ({ ...f, mes: parseInt(e.target.value) }))}>
                  {meses.map((m, i) => <option key={i} value={i + 1}>{m}</option>)}
                </select>
              </div>
              <div className="form-group">
                <label>Año</label>
                <input type="number" value={form.anio} onChange={e => setForm(f => ({ ...f, anio: parseInt(e.target.value) }))} />
              </div>
            </div>
            <div className="form-row">
              <div className="form-group">
                <label>Saldo inicial</label>
                <input type="number" step="0.01" value={form.saldo_inicial} onChange={e => setForm(f => ({ ...f, saldo_inicial: parseFloat(e.target.value) || 0 }))} />
              </div>
              <div className="form-group">
                <label>Ingresos</label>
                <input type="number" step="0.01" value={form.ingresos} onChange={e => setForm(f => ({ ...f, ingresos: parseFloat(e.target.value) || 0 }))} />
              </div>
            </div>
            <div className="form-row">
              <div className="form-group">
                <label>Gastos</label>
                <input type="number" step="0.01" value={form.gastos} onChange={e => setForm(f => ({ ...f, gastos: parseFloat(e.target.value) || 0 }))} />
              </div>
              <div className="form-group">
                <label>Saldo final (automático)</label>
                <input type="number" step="0.01" value={(form.saldo_inicial + form.ingresos - form.gastos).toFixed(2)} disabled style={{ opacity: 0.6 }} />
              </div>
            </div>
            <div className="form-group">
              <label>Observaciones</label>
              <input value={form.observaciones} onChange={e => setForm(f => ({ ...f, observaciones: e.target.value }))} />
            </div>
            {err && <p style={{ color: "#ef4444", fontSize: 12, marginBottom: 8 }}>{err}</p>}
            <div style={{ display: "flex", gap: 8, justifyContent: "flex-end", marginTop: 8 }}>
              <button className="btn" onClick={() => setModal(false)}>Cancelar</button>
              <button className="btn btn-primary" onClick={save} disabled={!form.entidad || !form.mes || !form.anio || enviando}>
                {enviando ? "Guardando..." : "Guardar"}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}