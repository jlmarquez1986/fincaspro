import { useState, useEffect } from "react";
import { AuthContext } from "./AuthContext";
import { api } from "../api/client";

export function AuthProvider({ children }) {
  const [user, setUser] = useState(() => {
    try {
      return JSON.parse(localStorage.getItem("user"));
    } catch {
      return null;
    }
  });

  const [vecino, setVecino] = useState(() => {
    try {
      return JSON.parse(localStorage.getItem("vecino"));
    } catch {
      return null;
    }
  });

  const [config, setConfig] = useState({
    community_name: "Comunidad",
  });

  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.config()
      .then(setConfig)
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  const loginStaff = (usuario) => {
    setUser(usuario);
    localStorage.setItem("user", JSON.stringify(usuario));
  };

  const loginVecino = (v) => {
    setVecino(v);
    localStorage.setItem("vecino", JSON.stringify(v));
  };

  const logout = () => {
    localStorage.clear();
    setUser(null);
    setVecino(null);
  };

  const value = {
    user,
    vecino,
    config,
    loading,
    loginStaff,
    loginVecino,
    logout,
    isStaff: !!user,
    isVecino: !!vecino,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}