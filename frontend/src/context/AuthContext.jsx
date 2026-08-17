import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { api } from '../utils/api';
import { getSession, setSession, clearSession, getRefreshToken } from '../utils/session';
import { API_BASE } from '../utils/config';

const AuthContext = createContext(null);

export const useAuth = () => {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used inside AuthProvider');
  return ctx;
};

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  const logout = useCallback(() => {
    // Revoke the refresh token server-side (best-effort, fire-and-forget)
    // so the stored session can't be replayed after sign-out.
    const refreshToken = getRefreshToken();
    clearSession();
    setUser(null);
    if (refreshToken) {
      fetch(`${API_BASE}/auth/logout`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ refresh_token: refreshToken }),
      }).catch(() => {});
    }
  }, []);

  const verifySession = useCallback(async () => {
    const session = getSession();
    if (!session?.access_token) {
      setLoading(false);
      return;
    }

    // The session itself lives in localStorage; /auth/me only confirms it's
    // still valid server-side. A network failure (backend restarting, flaky
    // connection) must NEVER clear it — a user who signed in once stays
    // signed in until the refresh token truly expires or is revoked.
    try {
      const me = await api.get('/auth/me');
      setUser(me);
      setLoading(false);
      return;
    } catch (err) {
      if (err.status === 401) {
        // Real auth failure — refresh already failed inside api.js.
        logout();
        setLoading(false);
        return;
      }
    }

    // Network error — backend may just be starting up. Retry once before
    // giving up; the cached session stays signed in either way.
    console.warn('AuthProvider: backend unreachable during session check — retrying once');
    setTimeout(() => {
      api
        .get('/auth/me')
        .then((me) => setUser(me))
        .catch((err) => {
          if (err.status === 401) logout();
          // Still unreachable — remain signed in on the cached session.
        })
        .finally(() => setLoading(false));
    }, 2000);
  }, [logout]);

  useEffect(() => {
    verifySession();

    const onUnauthorized = () => logout();
    window.addEventListener('auth:unauthorized', onUnauthorized);
    return () => window.removeEventListener('auth:unauthorized', onUnauthorized);
  }, [verifySession, logout]);

  const login = useCallback(async (...args) => {
    // Support both call styles: login(username, password) and login({ username, password })
    let uname;
    let pwd;
    if (args.length === 1 && typeof args[0] === 'object') {
      const obj = args[0] || {};
      uname = obj.username;
      pwd = obj.password;
    } else {
      uname = args[0];
      pwd = args[1];
    }

    const res = await api.post('/auth/login', { username: uname, password: pwd });
    console.info('AuthProvider: login response', res);
    setSession({
      access_token: res.access_token,
      refresh_token: res.refresh_token, // rotated opaque refresh token
    });
    const me = await api.get('/auth/me');
    console.info('AuthProvider: fetched /auth/me after login', me);
    setUser(me);
    return me;
  }, []);

  const register = useCallback(async (a, b, c, d) => {
    // Support register(username, email, password, full_name)
    // and register({ username, email, password, full_name })
    let payload;
    if (typeof a === 'object') {
      payload = a || {};
    } else {
      payload = { username: a, email: b, password: c, full_name: d };
    }

    const res = await api.post('/auth/register', payload);
    setSession({
      access_token: res.access_token,
      refresh_token: res.refresh_token,
    });
    const me = await api.get('/auth/me');
    setUser(me);
    return me;
  }, []);

  return (
    <AuthContext.Provider
      value={{
        user,
        loading,
        isAuthenticated: !!user,
        login,
        logout,
        register,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}