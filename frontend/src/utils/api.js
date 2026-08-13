import { API_BASE } from './config';
import { getAccessToken, clearSession } from './session';

export class ApiError extends Error {
  constructor(message, status) {
    super(message);
    this.status = status;
  }
}

async function request(path, options = {}) {
  const token = getAccessToken();
  const url = `${API_BASE}${path}`;

  const headers = {
    'Content-Type': 'application/json',
    ...(token && { Authorization: `Bearer ${token}` }),
    ...options.headers,
  };

  const res = await fetch(url, { ...options, headers });

  // Backend has NO /auth/refresh in Phase 5 — just logout on 401
  if (res.status === 401) {
    clearSession();
    window.dispatchEvent(new CustomEvent('auth:unauthorized'));
    throw new ApiError('Unauthorized', 401);
  }

  if (!res.ok) {
    const text = await res.text();
    throw new ApiError(text || `HTTP ${res.status}`, res.status);
  }

  if (res.status === 204) return null;
  return res.json();
}

export const api = {
  get: (path) => request(path, { method: 'GET' }),
  post: (path, body) => request(path, { method: 'POST', body: JSON.stringify(body) }),
  put: (path, body) => request(path, { method: 'PUT', body: JSON.stringify(body) }),
  del: (path) => request(path, { method: 'DELETE' }),
};

// Helpers for streaming endpoints (ChatWindow, etc.)
export const getStreamUrl = (path) => `${API_BASE}${path}`;

export const getAuthHeaders = () => {
  const token = getAccessToken();
  return token ? { Authorization: `Bearer ${token}` } : {};
};

// Backwards-compat default export for existing imports
export default api;
