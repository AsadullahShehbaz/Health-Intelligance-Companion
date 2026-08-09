/**
 * Tiny timestamp helpers for the sidebar.
 */

/**
 * "just now" / "5m ago" / "3h ago" / "2d ago" / "Aug 4" for an ISO string.
 * Returns "" for missing or unparseable input.
 */
export function formatRelativeTime(iso) {
  if (!iso) return "";
  const then = new Date(iso);
  if (Number.isNaN(then.getTime())) return "";

  const seconds = Math.round((Date.now() - then.getTime()) / 1000);
  if (seconds < 60) return "just now";
  if (seconds < 3600) return `${Math.round(seconds / 60)}m ago`;
  if (seconds < 86400) return `${Math.round(seconds / 3600)}h ago`;
  const days = Math.round(seconds / 86400);
  if (days < 7) return `${days}d ago`;

  return then.toLocaleDateString(undefined, { month: "short", day: "numeric" });
}
