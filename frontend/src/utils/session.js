/**
 * Session persistence for the JWT auth flow.
 *
 * The backend issues two tokens on login:
 *   - access_token  — short-lived JWT (15 min)
 *   - refresh_token — long-lived opaque token (7 days)
 *
 * We cache BOTH plus a copy of the user profile in localStorage so a page
 * reload or a backend restart doesn't force a fresh sign-in. When the access
 * token expires, `refreshSession` silently exchanges the refresh token for a
 * new pair via POST /auth/refresh.
 *
 * All token reads in the app go through here (not raw localStorage) so the
 * storage keys stay in one place.
 */

const API_BASE = "http://localhost:8000";

const ACCESS_KEY = "access_token";
const REFRESH_KEY = "refresh_token";
const USER_KEY = "auth_user";

/**
 * Custom event dispatched whenever a background refresh updates the tokens,
 * so the AuthContext can keep its React state in sync.
 */
export const SESSION_REFRESHED_EVENT = "auth:session-refreshed";

export function getStoredSession() {
  let user;
  try {
    user = JSON.parse(localStorage.getItem(USER_KEY) || "null");
  } catch {
    user = null; // malformed cached profile
  }
  return {
    accessToken: localStorage.getItem(ACCESS_KEY),
    refreshToken: localStorage.getItem(REFRESH_KEY),
    user,
  };
}

/**
 * Persist a session. Omitted fields (`undefined`) are left untouched, so a
 * partial update like `storeSession({ user })` keeps the existing tokens.
 * Pass `null`/falsy to explicitly remove a field.
 */
export function storeSession({ accessToken, refreshToken, user }) {
  if (accessToken !== undefined) {
    if (accessToken) localStorage.setItem(ACCESS_KEY, accessToken);
    else localStorage.removeItem(ACCESS_KEY);
  }
  if (refreshToken !== undefined) {
    if (refreshToken) localStorage.setItem(REFRESH_KEY, refreshToken);
    else localStorage.removeItem(REFRESH_KEY);
  }
  if (user !== undefined) {
    if (user) localStorage.setItem(USER_KEY, JSON.stringify(user));
    else localStorage.removeItem(USER_KEY);
  }
}

export function clearSession() {
  localStorage.removeItem(ACCESS_KEY);
  localStorage.removeItem(REFRESH_KEY);
  localStorage.removeItem(USER_KEY);
}

/**
 * True for fetch network failures (backend unreachable / mid-restart).
 * These are NOT auth failures — callers must NOT log the user out for them.
 */
export function isNetworkError(err) {
  return err instanceof TypeError || err?.name === "TypeError";
}

/**
 * Exchange the cached refresh token for a fresh access + refresh pair.
 *
 * Resolves with the new session object, or `null` when the refresh token is
 * missing or the server rejects it. On success the new pair is persisted and
 * SESSION_REFRESHED_EVENT is dispatched so consumers can update state.
 * On a network error the stored session is left intact and `null` is returned.
 */
export async function refreshSession() {
  const { refreshToken, user: existingUser } = getStoredSession();
  if (!refreshToken) return null;

  let res;
  try {
    res = await fetch(`${API_BASE}/auth/refresh`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ refresh_token: refreshToken }),
    });
  } catch {
    return null; // backend unreachable — keep the stored session as-is
  }
  if (!res.ok) return null;

  const data = await res.json();
  const session = {
    accessToken: data.access_token,
    refreshToken: data.refresh_token || refreshToken, // rotate; keep old if none returned
    user: existingUser, // start from the cached profile; replaced below when possible
  };

  // Fetch a fresh profile so the UI shows up-to-date user data.
  try {
    const meRes = await fetch(`${API_BASE}/auth/me`, {
      headers: { Authorization: `Bearer ${session.accessToken}` },
    });
    session.user = meRes.ok ? await meRes.json() : existingUser;
  } catch {
    session.user = existingUser; // keep the cached profile rather than dropping it
  }

  storeSession(session);
  window.dispatchEvent(new CustomEvent(SESSION_REFRESHED_EVENT, { detail: session }));
  return session;
}
