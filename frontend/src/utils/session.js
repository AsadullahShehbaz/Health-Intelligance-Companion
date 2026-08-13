// src/utils/session.js

const SESSION_KEY = 'health_companion_session';

export const getSession = () => {
  try {
    const raw = localStorage.getItem(SESSION_KEY);
    return raw ? JSON.parse(raw) : null;
  } catch {
    return null;
  }
};

export const setSession = (session) => {
  localStorage.setItem(SESSION_KEY, JSON.stringify(session));
};

export const clearSession = () => {
  localStorage.removeItem(SESSION_KEY);
};

export const getAccessToken = () => getSession()?.access_token ?? null;
export const getRefreshToken = () => getSession()?.refresh_token ?? null;