import { useState, useRef, useEffect } from "react";
import { useAuth } from "../context/AuthContext";

export default function Navbar({ onOpenLogin }) {
  const { user, isAuthenticated, logout, loading } = useAuth();
  const [menuOpen, setMenuOpen] = useState(false);
  const menuRef = useRef(null);

  // Close dropdown on click outside
  useEffect(() => {
    if (!menuOpen) return;
    const handleClick = (e) => {
      if (menuRef.current && !menuRef.current.contains(e.target)) {
        setMenuOpen(false);
      }
    };
    document.addEventListener("mousedown", handleClick);
    return () => document.removeEventListener("mousedown", handleClick);
  }, [menuOpen]);

  const initials = user?.full_name
    ? user.full_name.split(" ").map((n) => n[0]).join("").toUpperCase().slice(0, 2)
    : user?.username?.slice(0, 2).toUpperCase() || "?";

  return (
    <nav className="bg-[#212121] border-b border-white/10 sticky top-0 z-40">
      <div className="flex items-center justify-between max-w-5xl mx-auto px-4 h-14">
        {/* Left: Brand */}
        <div className="flex items-center gap-2.5">
          <span className="flex items-center justify-center h-8 w-8 rounded-lg bg-gradient-to-br from-emerald-400 to-teal-600 text-white font-bold text-sm shadow-sm">
            <svg className="w-4.5 h-4.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M9.75 3.104v5.714a2.25 2.25 0 01-.659 1.591L5 14.5M9.75 3.104c-.251.023-.501.05-.75.082m.75-.082a24.301 24.301 0 014.5 0m0 0v5.714c0 .597.237 1.17.659 1.591L19.8 15.3M14.25 3.104c.251.023.501.05.75.082M19.8 15.3l-1.57.393A9.065 9.065 0 0112 15a9.065 9.065 0 00-6.23.693L5 14.5m14.8.8l1.402 1.402c1.232 1.232.65 3.318-1.067 3.611A48.309 48.309 0 0112 21c-2.773 0-5.491-.235-8.135-.687-1.718-.293-2.3-2.379-1.067-3.61L5 14.5" />
            </svg>
          </span>
          <span className="text-gray-200 font-semibold text-base tracking-tight">
            Health Intelligence
          </span>
        </div>

        {/* Right: Navigation */}
        <div className="flex items-center gap-1">
          <a
            href="#"
            className="px-3 py-1.5 text-sm text-gray-400 hover:text-gray-200 transition-colors rounded-lg hover:bg-white/5"
          >
            Home
          </a>
          <a
            href="#"
            className="px-3 py-1.5 text-sm text-gray-400 hover:text-gray-200 transition-colors rounded-lg hover:bg-white/5"
          >
            About
          </a>
          <div className="w-px h-5 bg-white/10 mx-2" />

          {loading ? (
            <div className="w-8 h-8 rounded-full bg-white/5 animate-pulse" />
          ) : isAuthenticated ? (
            /* ── User Menu ── */
            <div className="relative" ref={menuRef}>
              <button
                onClick={() => setMenuOpen(!menuOpen)}
                className="flex items-center gap-2 px-2 py-1.5 rounded-lg hover:bg-white/5 transition-colors"
              >
                <span className="w-7 h-7 rounded-full bg-gradient-to-br from-emerald-400 to-teal-600 flex items-center justify-center text-white text-xs font-semibold shadow-sm">
                  {initials}
                </span>
                <span className="text-sm text-gray-300 hidden sm:inline max-w-[120px] truncate">
                  {user?.full_name || user?.username}
                </span>
                <svg
                  className={`w-4 h-4 text-gray-500 transition-transform ${menuOpen ? "rotate-180" : ""}`}
                  fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}
                >
                  <path strokeLinecap="round" strokeLinejoin="round" d="M19 9l-7 7-7-7" />
                </svg>
              </button>

              {menuOpen && (
                <div className="absolute right-0 mt-2 w-56 bg-[#2f2f2f] border border-white/10 rounded-xl shadow-2xl py-1.5 animate-fade-in">
                  {/* User info header */}
                  <div className="px-4 py-2.5 border-b border-white/5">
                    <p className="text-sm font-medium text-gray-200 truncate">
                      {user?.full_name || user?.username}
                    </p>
                    <p className="text-xs text-gray-500 truncate mt-0.5">{user?.email}</p>
                  </div>

                  <button
                    onClick={() => { logout(); setMenuOpen(false); }}
                    className="w-full flex items-center gap-2.5 px-4 py-2.5 text-sm text-red-400 hover:bg-white/5 transition-colors"
                  >
                    <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                      <path strokeLinecap="round" strokeLinejoin="round" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
                    </svg>
                    Sign out
                  </button>
                </div>
              )}
            </div>
          ) : (
            /* ── Login Button ── */
            <button
              onClick={onOpenLogin}
              className="px-4 py-1.5 text-sm font-medium text-white bg-gradient-to-r from-emerald-500 to-teal-600 hover:from-emerald-400 hover:to-teal-500 rounded-lg transition-all duration-200 shadow-sm"
            >
              Sign in
            </button>
          )}
        </div>
      </div>
    </nav>
  );
}
