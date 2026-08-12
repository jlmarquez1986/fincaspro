import { useState, useEffect } from "react";
import { useAuth } from "./hooks/useAuth";
import { api } from "./api/client";

// Componentes de autenticación
import LoginStaff from "./components/auth/LoginStaff";
import LoginPortal from "./components/auth/LoginPortal";
import Landing from "./components/auth/Landing";

// Layout
import Sidebar from "./components/layout/Sidebar";
import Topbar from "./components/layout/Topbar";

// Páginas existentes
import Dashboard from "./components/pages/Dashboard";
import Tickets from "./components/pages/Tickets";
import Paqueteria from "./components/pages/Paqueteria";
import Llaves from "./components/pages/Llaves";
import Avisos from "./components/pages/Avisos";
import Vecinos from "./components/pages/Vecinos";

// Portal vecino
import PortalVecino from "./components/portal/PortalVecino";

// NUEVAS PÁGINAS
import TelefonosInteres from "./components/pages/TelefonosInteres";
import Administradores from "./components/pages/Administradores";
import EstadosCuenta from "./components/pages/EstadosCuenta";
import DelegacionesVoto from "./components/pages/DelegacionesVoto";
import QuejasMejoras from "./components/pages/QuejasMejoras";
import Piscina from "./components/pages/Piscina";

// Títulos para cada página
const PAGE_TITLES = {
  dashboard: "Dashboard",
  tickets: "Averías y tickets",
  paqueteria: "Gestión de paquetería",
  llaves: "Control de llaves",
  avisos: "Avisos y tablón",
  vecinos: "Vecinos",
  telefonos: "Teléfonos de interés",
  administradores: "Administradores",
  estados: "Estados de cuenta",
  delegaciones: "Delegaciones de voto",
  quejas: "Quejas y mejoras",
  piscina: "Piscina",
};

export default function App() {
  const { user, config, loginStaff, loginVecino, logout, isStaff, isVecino } = useAuth();
  const [landing, setLanding] = useState(true);
  const [authMode, setAuthMode] = useState("staff");
  const [page, setPage] = useState("dashboard");
  const [badges, setBadges] = useState({ tickets: 0, paquetes: 0 });

  // Recargar badges cada 30 segundos
  useEffect(() => {
    if (!user) return;
    const refresh = () => {
      api.dashboard()
        .then(s => setBadges({ tickets: s.tickets_abiertos, paquetes: s.pkgs_pendientes }))
        .catch(() => {});
    };
    refresh();
    const interval = setInterval(refresh, 30000);
    return () => clearInterval(interval);
  }, [user]);

  // Landing
  if (landing && !isStaff && !isVecino) {
    return <Landing onSelect={(type) => { setAuthMode(type); setLanding(false); }} communityName={config?.community_name} />;
  }

  // Login Staff
  if (!isStaff && !isVecino && authMode === "staff") {
    return (
      <div>
        <button className="btn btn-sm" onClick={() => setLanding(true)} style={{ position: "fixed", top: 16, left: 16, zIndex: 100 }}>← Volver</button>
        <LoginStaff onLogin={loginStaff} communityName={config?.community_name} />
      </div>
    );
  }

  // Login Portal
  if (!isStaff && !isVecino && authMode === "portal") {
    return (
      <div>
        <button className="btn btn-sm" onClick={() => setLanding(true)} style={{ position: "fixed", top: 16, left: 16, zIndex: 100 }}>← Volver</button>
        <LoginPortal onLogin={loginVecino} communityName={config?.community_name} />
      </div>
    );
  }

  // Portal Vecino
  if (isVecino) {
    return <PortalVecino onLogout={logout} />;
  }

  // Staff logged in
  const handleLogout = () => {
    logout();
    setLanding(true);
  };

  const pages = {
    dashboard: <Dashboard setPage={setPage} />,
    tickets: <Tickets />,
    paqueteria: <Paqueteria />,
    llaves: <Llaves />,
    avisos: <Avisos />,
    vecinos: <Vecinos />,
    telefonos: <TelefonosInteres />,
    administradores: <Administradores />,
    estados: <EstadosCuenta />,
    delegaciones: <DelegacionesVoto />,
    quejas: <QuejasMejoras />,
    piscina: <Piscina />,
  };

  return (
    <div className="layout">
      <Sidebar
        page={page}
        setPage={setPage}
        badges={badges}
        user={user}
        onLogout={handleLogout}
        communityName={config?.community_name}
      />
      <div className="main">
        <Topbar title={PAGE_TITLES[page] || page} />
        <div className="content">{pages[page]}</div>
      </div>
    </div>
  );
}