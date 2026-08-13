import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { api } from '../utils/api';
import { getSession, setSession, clearSession } from '../utils/session';

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
    clearSession();
    setUser(null);
  }, []);

  const verifySession = useCallback(async () => {
    const session = getSession();
    if (!session?.access_token) {
      setLoading(false);
      return;
    }

    try {
      const me = await api.get('/auth/me');
      console.info('AuthProvider: verifySession got /auth/me', me);
      setUser(me);
    } catch (err) {
      if (err.status === 401) {
        // Already handled inside api.js (clears storage + fires event),
        // but keep UI state in sync just in case.
        logout();
      } else {
        // Network error / server restarting — keep cached session alive
        // so the user isn't kicked out on a flaky connection.
        console.warn('Auth check failed (network), keeping session');
      }
    } finally {
      setLoading(false);
    }
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
      refresh_token: res.refresh_token, // backend sends copy of access_token
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