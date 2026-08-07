import { createContext, useContext, useState, useEffect, useCallback } from "react";
import {
  clearSession,
  getStoredSession,
  isNetworkError,
  refreshSession,
  storeSession,
  SESSION_REFRESHED_EVENT,
} from "../utils/session";

const API_BASE = "http://localhost:8000";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  // Whole session (access token + refresh token + cached profile) lives in
  // localStorage via utils/session.js, so a reload or backend restart keeps
  // the user signed in.
  const [session, setSession] = useState(() => getStoredSession());
  // Only show the loading skeleton when we have a token but no cached profile
  // to render immediately (e.g. a session stored before user caching was added).
  const [loading, setLoading] = useState(
    () => Boolean(getStoredSession().accessToken && !getStoredSession().user)
  );

  const { accessToken: token, user } = session;

  // Keep React state in sync when api.js refreshes the tokens in the background.
  useEffect(() => {
    const handleRefreshed = (e) => {
      const s = e.detail;
      if (!s) return;
      setSession((prev) => ({
        ...prev,
        accessToken: s.accessToken || prev.accessToken,
        refreshToken: s.refreshToken || prev.refreshToken,
        user: s.user || prev.user,
      }));
    };
    window.addEventListener(SESSION_REFRESHED_EVENT, handleRefreshed);
    return () => window.removeEventListener(SESSION_REFRESHED_EVENT, handleRefreshed);
  }, []);

  // Listen for 401 events from the api wrapper — forces logout when a token
  // genuinely can't be refreshed.
  useEffect(() => {
    const handleUnauthorized = () => {
      clearSession();
      setSession({ accessToken: null, refreshToken: null, user: null });
    };
    window.addEventListener("auth:unauthorized", handleUnauthorized);
    return () => window.removeEventListener("auth:unauthorized", handleUnauthorized);
  }, []);

  // On mount, validate the cached session. The key rule: a network error
  // (backend restarting) must NOT log the user out — we keep the cached
  // session and re-check a few times. Only a real 401 triggers a refresh
  // (or a logout when the refresh token is invalid too).
  useEffect(() => {
    // No cached session — initial `loading` is already false for this case.
    if (!getStoredSession().accessToken) return;

    let retryTimer = null;
    let attempts = 0;
    const MAX_RETRIES = 3;

    const validate = async () => {
      const { accessToken } = getStoredSession();
      if (!accessToken) {
        setLoading(false);
        return;
      }
      try {
        const res = await fetch(`${API_BASE}/auth/me`, {
          headers: { Authorization: `Bearer ${accessToken}` },
        });

        if (res.ok) {
          const freshUser = await res.json();
          setSession((prev) => ({ ...prev, user: freshUser }));
          storeSession({ user: freshUser }); // refresh the cached profile
        } else if (res.status === 401) {
          // Access token expired — silently refresh with the cached refresh token.
          const refreshed = await refreshSession();
          if (refreshed) {
            setSession({
              accessToken: refreshed.accessToken,
              refreshToken: refreshed.refreshToken,
              user: refreshed.user,
            });
          } else {
            clearSession();
            setSession({ accessToken: null, refreshToken: null, user: null });
          }
        } else {
          // 403 / 5xx — treat as an untrustworthy session.
          clearSession();
          setSession({ accessToken: null, refreshToken: null, user: null });
        }
      } catch (err) {
        if (isNetworkError(err) && attempts < MAX_RETRIES) {
          // Backend down / restarting — keep the cached session, retry shortly.
          attempts += 1;
          retryTimer = setTimeout(validate, 2000 * attempts);
        } else {
          clearSession();
          setSession({ accessToken: null, refreshToken: null, user: null });
        }
      } finally {
        setLoading(false);
      }
    };

    validate();
    return () => clearTimeout(retryTimer);
  }, []);

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

    // Fetch the user profile immediately so state is consistent.
    const userRes = await fetch(`${API_BASE}/auth/me`, {
      headers: { Authorization: `Bearer ${data.access_token}` },
    });

    if (!userRes.ok) throw new Error("Failed to fetch user profile");

    const userData = await userRes.json();
    const newSession = {
      accessToken: data.access_token,
      refreshToken: data.refresh_token || null,
      user: userData,
    };
    storeSession(newSession);
    setSession(newSession);
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
    clearSession();
    setSession({ accessToken: null, refreshToken: null, user: null });
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
