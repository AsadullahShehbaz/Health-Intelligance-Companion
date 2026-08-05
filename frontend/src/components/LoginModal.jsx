import { useState, useRef, useEffect } from "react";
import { useAuth } from "../context/AuthContext";

export default function LoginModal({ onClose, onSwitchToRegister }) {
  const { login } = useAuth();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const usernameRef = useRef(null);

  useEffect(() => {
    usernameRef.current?.focus();
  }, []);

  // Close on Escape
  useEffect(() => {
    const handleKey = (e) => {
      if (e.key === "Escape") onClose();
    };
    window.addEventListener("keydown", handleKey);
    return () => window.removeEventListener("keydown", handleKey);
  }, [onClose]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");

    if (!username.trim() || !password.trim()) {
      setError("Please enter both username and password.");
      return;
    }

    setSubmitting(true);
    try {
      await login(username.trim(), password);
      onClose();
    } catch (err) {
      setError(err.message);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm animate-fade-in"
      onClick={(e) => { if (e.target === e.currentTarget) onClose(); }}
    >
      <div className="w-full max-w-sm mx-4 bg-[#212121] border border-white/10 rounded-2xl shadow-2xl p-6 animate-fade-in">
        {/* Header */}
        <div className="flex items-center justify-between mb-5">
          <h2 className="text-lg font-semibold text-gray-200">Welcome back</h2>
          <button
            onClick={onClose}
            className="p-1.5 rounded-lg text-gray-500 hover:text-gray-300 hover:bg-white/5 transition-colors"
          >
            <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label htmlFor="login-username" className="block text-sm text-gray-400 mb-1.5">
              Username
            </label>
            <input
              ref={usernameRef}
              id="login-username"
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              disabled={submitting}
              autoComplete="username"
              className="w-full bg-[#2f2f2f] border border-white/10 rounded-xl px-4 py-2.5 text-sm text-gray-200 placeholder-gray-600 outline-none focus:border-emerald-500/50 focus:ring-1 focus:ring-emerald-500/20 transition-all disabled:opacity-50"
              placeholder="Enter your username"
            />
          </div>

          <div>
            <label htmlFor="login-password" className="block text-sm text-gray-400 mb-1.5">
              Password
            </label>
            <input
              id="login-password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              disabled={submitting}
              autoComplete="current-password"
              className="w-full bg-[#2f2f2f] border border-white/10 rounded-xl px-4 py-2.5 text-sm text-gray-200 placeholder-gray-600 outline-none focus:border-emerald-500/50 focus:ring-1 focus:ring-emerald-500/20 transition-all disabled:opacity-50"
              placeholder="Enter your password"
            />
          </div>

          {error && (
            <div className="bg-red-500/10 border border-red-500/20 rounded-xl px-4 py-2.5 text-sm text-red-400">
              {error}
            </div>
          )}

          <button
            type="submit"
            disabled={submitting}
            className="w-full py-2.5 rounded-xl bg-gradient-to-r from-emerald-500 to-teal-600 text-white font-medium text-sm hover:from-emerald-400 hover:to-teal-500 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 active:scale-[0.98] flex items-center justify-center gap-2"
          >
            {submitting ? (
              <>
                <svg className="w-4 h-4 animate-spin" viewBox="0 0 24 24" fill="none">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                </svg>
                Signing in…
              </>
            ) : (
              "Sign in"
            )}
          </button>
        </form>

        {/* Footer */}
        <p className="mt-5 text-center text-sm text-gray-500">
          Don&apos;t have an account?{" "}
          <button
            onClick={onSwitchToRegister}
            className="text-emerald-400 hover:text-emerald-300 font-medium transition-colors"
          >
            Create one
          </button>
        </p>
      </div>
    </div>
  );
}
