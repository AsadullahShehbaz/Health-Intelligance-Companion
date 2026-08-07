import { clearSession, getStoredSession, refreshSession } from "./session";

const API_BASE = "http://localhost:8000";

/**
 * Thin fetch wrapper that automatically attaches the stored JWT and
 * handles global auth failures (401 → refresh once → retry → logout).
 *
 * Usage:
 *   import api from "../utils/api";
 *   const data = await api.get("/auth/me");
 *   const result = await api.post("/auth/login", { username, password });
 */

async function request(method, path, body = null, isRetry = false) {
  const { accessToken } = getStoredSession();

  const headers = { "Content-Type": "application/json" };
  if (accessToken) headers["Authorization"] = `Bearer ${accessToken}`;

  const res = await fetch(`${API_BASE}${path}`, {
    method,
    headers,
    body: body ? JSON.stringify(body) : undefined,
  });

  // Unauthorised — access token expired. Silently refresh it once and retry;
  // only sign the user out if the refresh token is gone or invalid too.
  if (res.status === 401 && accessToken && !isRetry) {
    const session = await refreshSession();
    if (session?.accessToken) {
      return request(method, path, body, true);
    }
    clearSession();
    window.dispatchEvent(new CustomEvent("auth:unauthorized"));
    throw new Error("Session expired. Please sign in again.");
  }

  // Parse JSON body; fall back to text for empty responses
  let data;
  const contentType = res.headers.get("content-type");
  if (contentType && contentType.includes("application/json")) {
    data = await res.json();
  } else {
    const text = await res.text();
    data = text || null;
  }

  if (!res.ok) {
    const message = (data && data.detail) || `Request failed (${res.status})`;
    throw new Error(message);
  }

  return data;
}

const api = {
  get: (path) => request("GET", path),
  post: (path, body) => request("POST", path, body),
  patch: (path, body) => request("PATCH", path, body),
  put: (path, body) => request("PUT", path, body),
  delete: (path) => request("DELETE", path),
};

export default api;
