const BASE = "/api";

function getToken() {
  return localStorage.getItem("token");
}

function getVecinoToken() {
  return localStorage.getItem("vecino_token");
}

async function request(method, path, body = null, isFormData = false) {
  const headers = {};
  const token = getToken();
  const vecinoToken = getVecinoToken();

  if (path.startsWith("/portal") && vecinoToken) {
    headers["Authorization"] = `Bearer ${vecinoToken}`;
  } else if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }

  if (!isFormData) {
    headers["Content-Type"] = "application/json";
  }

  const res = await fetch(`${BASE}${path}`, {
    method,
    headers,
    body: body ? (isFormData ? body : JSON.stringify(body)) : undefined,
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: "Error desconocido" }));
    throw new Error(err.detail || "Error en la petición");
  }
  if (res.status === 204) return null;
  return res.json();
}

export const api = {
  get: (path) => request("GET", path),
  post: (path, body) => request("POST", path, body),
  patch: (path, body) => request("PATCH", path, body),
  delete: (path) => request("DELETE", path),

  // Auth (staff)
  login: (username, password) => {
    const form = new URLSearchParams({ username, password });
    return fetch(`${BASE}/auth/login`, {
      method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
      body: form,
    }).then(r => r.json());
  },

  // Vecino portal auth
  vecinoLogin: (email, password) => {
    return fetch(`${BASE}/portal/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password }),
    }).then(r => r.json());
  },

  // Dashboard
  dashboard: () => request("GET", "/dashboard"),
  config: () => request("GET", "/config"),

  // Tickets
  tickets: {
    list: (params = "") => request("GET", `/tickets/${params}`),
    get: (id) => request("GET", `/tickets/${id}`),
    create: (data) => request("POST", "/tickets/", data),
    createWithPhoto: (formData) => request("POST", "/tickets/", formData, true),
    update: (id, data) => request("PATCH", `/tickets/${id}`, data),
    delete: (id) => request("DELETE", `/tickets/${id}`),
    comments: (id) => request("GET", `/tickets/${id}/comentarios`),
    addComment: (id, data) => request("POST", `/tickets/${id}/comentarios`, data),
  },

  // Paquetería
  paquetes: {
    list: (params = "") => request("GET", `/paqueteria/${params}`),
    create: (data) => request("POST", "/paqueteria/", data),
    deliver: (id) => request("PATCH", `/paqueteria/${id}/entregar`),
  },

  // Llaves
  llaves: {
    list: () => request("GET", "/llaves/"),
    create: (data) => request("POST", "/llaves/", data),
    prestar: (id, data) => request("PATCH", `/llaves/${id}/prestar`, data),
    devolver: (id) => request("PATCH", `/llaves/${id}/devolver`),
  },

  // Avisos
  avisos: {
    list: () => request("GET", "/avisos/"),
    create: (data) => request("POST", "/avisos/", data),
    archive: (id) => request("PATCH", `/avisos/${id}/archivar`),
  },

  // Vecinos
  vecinos: {
    list: () => request("GET", "/vecinos/"),
    create: (data) => request("POST", "/vecinos/", data),
    delete: (id) => request("DELETE", `/vecinos/${id}`),
    portalRegistro: (data) => request("POST", "/vecinos/portal/registro", data),
    // Nuevo: obtener presidente
    presidente: () => request("GET", "/vecinos/presidente"),
    // Actualizar vecino (PATCH)
    update: (id, data) => request("PATCH", `/vecinos/${id}`, data),
  },

  // Portal Vecino
  portal: {
    me: () => request("GET", "/portal/me"),
    misTickets: () => request("GET", "/portal/mis-tickets"),
    misPaquetes: () => request("GET", "/portal/mis-paquetes"),
    avisos: () => request("GET", "/portal/avisos"),
    reportarAveria: (formData) => request("POST", "/portal/tickets", formData, true),
  },

  // ── Nuevos módulos ──────────────────────────────────

  // Quejas y Mejoras
  quejasMejoras: {
    list: (params = "") => request("GET", `/quejas-mejoras/${params}`),
    create: (data) => request("POST", "/quejas-mejoras/", data),
    update: (id, data) => request("PATCH", `/quejas-mejoras/${id}`, data),
    delete: (id) => request("DELETE", `/quejas-mejoras/${id}`),
  },

  // Piscina
  piscina: {
    carnets: {
      list: () => request("GET", "/piscina/carnets"),
      create: (data) => request("POST", "/piscina/carnets", data),
      verificar: (numero) => request("GET", `/piscina/carnets/verificar/${numero}`),
    },
    invitaciones: {
      saldo: (vecinoId) => request("GET", `/piscina/invitaciones/vecino/${vecinoId}`),
      config: (nuevoTotal) => request("PATCH", `/piscina/invitaciones/config?nuevo_total=${nuevoTotal}`),
    },
    registros: {
      list: (params = "") => request("GET", `/piscina/registros/${params}`),
      create: (data) => request("POST", "/piscina/registros", data),
    },
  },

  // Administradores
  administradores: {
    list: (params = "") => request("GET", `/administradores/${params}`),
    create: (data) => request("POST", "/administradores/", data),
    update: (id, data) => request("PATCH", `/administradores/${id}`, data),
    delete: (id) => request("DELETE", `/administradores/${id}`),
  },

  // Estados de Cuenta
  estadosCuenta: {
    list: (params = "") => request("GET", `/estados-cuenta/${params}`),
    create: (data) => request("POST", "/estados-cuenta/", data),
    update: (id, data) => request("PATCH", `/estados-cuenta/${id}`, data),
    delete: (id) => request("DELETE", `/estados-cuenta/${id}`),
  },

  // Delegaciones de Voto
  delegacionesVoto: {
    list: (params = "") => request("GET", `/delegaciones-voto/${params}`),
    create: (data) => request("POST", "/delegaciones-voto/", data),
    desactivar: (id) => request("PATCH", `/delegaciones-voto/${id}/desactivar`),
  },

  // Teléfonos de Interés
  telefonosInteres: {
    list: (params = "") => request("GET", `/telefonos-interes/${params}`),
    create: (data) => request("POST", "/telefonos-interes/", data),
    update: (id, data) => request("PATCH", `/telefonos-interes/${id}`, data),
    delete: (id) => request("DELETE", `/telefonos-interes/${id}`),
  },
};