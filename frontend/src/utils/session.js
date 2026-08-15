// src/utils/session.js

import { API_BASE } from './config';

const SESSION_KEY = 'health_companion_session';
const TOKEN_EXPIRY_KEY = 'health_companion_token_expiry';

// Default token expiry time (in minutes) — should match backend ACCESS_TOKEN_EXPIRE_MINUTES
const ACCESS_TOKEN_EXPIRE_MINUTES = 60;

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
  // When tokens are issued, record the current time so we can calculate expiry
  recordTokenIssuedTime();
};

export const clearSession = () => {
  localStorage.removeItem(SESSION_KEY);
  localStorage.removeItem(TOKEN_EXPIRY_KEY);
};

export const getAccessToken = () => getSession()?.access_token ?? null;
export const getRefreshToken = () => getSession()?.refresh_token ?? null;

/**
 * Record the time tokens were issued (now).
 * Used for proactive refresh — we calculate expiry as issuedTime + ACCESS_TOKEN_EXPIRE_MINUTES.
 */
export const recordTokenIssuedTime = () => {
  localStorage.setItem(TOKEN_EXPIRY_KEY, JSON.stringify({
    issued_at: Date.now(),
    expires_in_ms: ACCESS_TOKEN_EXPIRE_MINUTES * 60 * 1000,
  }));
};

/**
 * Get the expiry time for the current access token (milliseconds since epoch).
 * Returns null if tokens haven't been issued yet.
 */
export const getTokenExpiryTime = () => {
  try {
    const data = localStorage.getItem(TOKEN_EXPIRY_KEY);
    if (!data) return null;
    const parsed = JSON.parse(data);
    return parsed.issued_at + parsed.expires_in_ms;
  } catch {
    return null;
  }
};

/**
 * Check if the access token is expiring soon (within threshold minutes).
 * Returns true if token is within `thresholdMinutes` of expiry.
 * @param thresholdMinutes - How many minutes before expiry to consider it "soon" (default 2)
 */
export const isTokenExpiringSoon = (thresholdMinutes = 2) => {
  const expiryTime = getTokenExpiryTime();
  if (!expiryTime) return false;
  
  const now = Date.now();
  const expiryThreshold = thresholdMinutes * 60 * 1000;
  
  return expiryTime - now < expiryThreshold;
};

// ---------------------------------------------------------------------------
// Refresh interceptor
// ---------------------------------------------------------------------------

const onUnauthorized = () => {
  clearSession();
  window.dispatchEvent(new CustomEvent('auth:unauthorized'));
};

/**
 * Exchange the refresh token for a new access + refresh pair.
 * Implements token rotation: the old refresh token is revoked server-side.
 * Throws on failure (session is cleared and auth:unauthorized is dispatched).
 */
async function refreshAccessToken() {
  const refreshToken = getRefreshToken();
  if (!refreshToken) {
    onUnauthorized();
    throw new Error('No refresh token available');
  }

  const res = await fetch(`${API_BASE}/auth/refresh`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ refresh_token: refreshToken }),
  });

  if (!res.ok) {
    onUnauthorized();
    throw new Error(`Token refresh failed (HTTP ${res.status})`);
  }

  const data = await res.json();
  setSession({
    access_token: data.access_token,
    refresh_token: data.refresh_token,
  });
  return data.access_token;
}

// Single-flight: concurrent callers share one in-flight refresh promise
let refreshInFlight = null;

/**
 * Refresh the access token. If a refresh is already in progress, wait for it
 * instead of issuing a parallel request (prevents refresh-token rotation races).
 */
export function refreshSession() {
  if (!refreshInFlight) {
    refreshInFlight = refreshAccessToken().finally(() => {
      refreshInFlight = null;
    });
  }
  return refreshInFlight;
}

/**
 * Proactively refresh the token if it's expiring soon.
 * Call before making important requests. Fire-and-forget safe:
 * returns false instead of throwing when no refresh is needed/possible.
 */
export async function ensureFreshToken() {
  if (!getAccessToken() || !isTokenExpiringSoon()) return false;
  try {
    await refreshSession();
    return true;
  } catch (err) {
    console.warn('Proactive refresh failed, will retry on 401:', err);
    return false;
  }
}

/**
 * Authenticated fetch with refresh interception.
 * - Proactively refreshes before the request if the token is near expiry
 * - On a 401 response, refreshes once and retries the original request
 */
export async function authFetch(path, options = {}) {
  await ensureFreshToken();

  const doFetch = async () => {
    const token = getAccessToken();
    return fetch(`${API_BASE}${path}`, {
      ...options,
      headers: {
        ...(options.body ? { 'Content-Type': 'application/json' } : {}),
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
        ...options.headers,
      },
    });
  };

  let res = await doFetch();

  if (res.status === 401) {
    try {
      await refreshSession();
    } catch {
      throw new Error('Unauthorized');
    }
    res = await doFetch(); // retry exactly once with the new token
  }

  return res;
}