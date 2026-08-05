import { createContext, useContext, useState, useEffect, useCallback } from "react";

const API_BASE = "http://localhost:8000";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(() => localStorage.getItem("access_token"));
  const [loading, setLoading] = useState(true);

  // Listen for 401 events from the api wrapper — forces logout on expired tokens
  useEffect(() => {
    const handleUnauthorized = () => {
      setToken(null);
      setUser(null);
    };
    window.addEventListener("auth:unauthorized", handleUnauthorized);
    return () => window.removeEventListener("auth:unauthorized", handleUnauthorized);
  }, []);

  // On mount, validate stored token by fetching /auth/me
  useEffect(() => {
    if (!token) {
      setLoading(false);
      return;
    }

    fetch(`${API_BASE}/auth/me`, {
      headers: { Authorization: `Bearer ${token}` },
    })
      .then((res) => {
        if (!res.ok) throw new Error("Token invalid");
        return res.json();
      })
      .then((userData) => setUser(userData))
      .catch(() => {
        localStorage.removeItem("access_token");
        setToken(null);
      })
      .finally(() => setLoading(false));
  }, [token]);

  const login = useCallback(async (username, password) => {
    const res = await fetch(`${API_BASE}/auth/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username, password }),
    });

    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || "Invalid username or password");
    }

    const data = await res.json();
    localStorage.setItem("access_token", data.access_token);
    setToken(data.access_token);

    // Fetch the user profile immediately so state is consistent
    const userRes = await fetch(`${API_BASE}/auth/me`, {
      headers: { Authorization: `Bearer ${data.access_token}` },
    });

    if (!userRes.ok) throw new Error("Failed to fetch user profile");

    const userData = await userRes.json();
    setUser(userData);
    return userData;
  }, []);

  const register = useCallback(async (username, email, password, fullName) => {
    const body = { username, email, password };
    if (fullName) body.full_name = fullName;

    const res = await fetch(`${API_BASE}/auth/register`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });

    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || "Registration failed");
    }

    // Auto-login after successful registration
    return await login(username, password);
  }, [login]);

  const logout = useCallback(() => {
    localStorage.removeItem("access_token");
    setToken(null);
    setUser(null);
  }, []);

  return (
    <AuthContext.Provider
      value={{
        user,
        token,
        loading,
        login,
        register,
        logout,
        isAuthenticated: !!token && !!user,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within an AuthProvider");
  return ctx;
}
