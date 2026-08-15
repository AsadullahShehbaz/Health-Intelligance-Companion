import { API_BASE } from './config';
import { authFetch, getAccessToken } from './session';

export class ApiError extends Error {
  constructor(message, status) {
    super(message);
    this.status = status;
  }
}

async function request(path, options = {}) {
  // authFetch handles proactive refresh, 401 refresh-and-retry, and
  // session cleanup + auth:unauthorized dispatch when refresh fails
  let res;
  try {
    res = await authFetch(path, options);
  } catch {
    throw new ApiError('Unauthorized', 401);
  }

  if (res.status === 401) {
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
