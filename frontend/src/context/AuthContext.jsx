import { createContext, useContext, useEffect, useState } from "react";
import api from "../services/api";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  // Check whether an existing JWT is still valid.
  useEffect(() => {
    const token = localStorage.getItem("access_token");

    if (!token) {
      setLoading(false);
      return;
    }

    api
      .get("/auth/me")
      .then((response) => {
        setUser(response.data);
      })
      .catch(() => {
        localStorage.removeItem("access_token");
        setUser(null);
      })
      .finally(() => {
        setLoading(false);
      });
  }, []);

  async function login(email, password) {
    const response = await api.post("/auth/login", {
      email,
      password,
    });

    const token = response.data.access_token;

    localStorage.setItem("access_token", token);

    const userResponse = await api.get("/auth/me");

    setUser(userResponse.data);

    return userResponse.data;
  }

  async function signup(fullName, email, password) {
    const response = await api.post("/auth/signup", {
      full_name: fullName,
      email,
      password,
    });

    return response.data;
  }

  function logout() {
    localStorage.removeItem("access_token");
    setUser(null);
  }

  const value = {
    user,
    loading,
    login,
    signup,
    logout,
    isAuthenticated: Boolean(user),
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);

  if (!context) {
    throw new Error("useAuth must be used inside AuthProvider");
  }

  return context;
}