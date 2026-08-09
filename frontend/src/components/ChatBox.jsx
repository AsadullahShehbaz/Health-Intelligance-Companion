import { useState } from "react";
import { useAuth } from "../context/AuthContext";
import Sidebar from "./Sidebar";
import ChatWindow from "./ChatWindow";

/**
 * Layout wrapper: the auth gate, then the conversation sidebar + chat
 * window. Owns the sidebar's desktop collapse and mobile-drawer state;
 * everything else lives in ConversationsContext / ChatWindow.
 */

function AuthSkeleton() {
  return (
    <div className="flex flex-col h-[calc(100vh-65px)] bg-[#212121] items-center justify-center">
      <div className="w-14 h-14 rounded-2xl bg-white/5 animate-pulse mb-6" />
      <div className="h-5 w-64 bg-white/5 rounded animate-pulse mb-3" />
      <div className="h-4 w-48 bg-white/5 rounded animate-pulse" />
    </div>
  );
}

function SignInPrompt({ onOpenLogin }) {
  return (
    <div className="flex flex-col h-[calc(100vh-65px)] bg-[#212121] items-center justify-center px-4 animate-fade-in">
      <div className="w-14 h-14 rounded-2xl bg-gradient-to-br from-emerald-400 to-teal-600 flex items-center justify-center shadow-lg shadow-emerald-500/20 mb-6 ring-1 ring-white/10">
        <svg className="w-8 h-8 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9.75 3.104v5.714a2.25 2.25 0 01-.659 1.591L5 14.5M9.75 3.104c-.251.023-.501.05-.75.082m.75-.082a24.301 24.301 0 014.5 0m0 0v5.714c0 .597.237 1.17.659 1.591L19.8 15.3M14.25 3.104c.251.023.501.05.75.082M19.8 15.3l-1.57.393A9.065 9.065 0 0112 15a9.065 9.065 0 00-6.23.693L5 14.5m14.8.8l1.402 1.402c1.232 1.232.65 3.318-1.067 3.611A48.309 48.309 0 0112 21c-2.773 0-5.491-.235-8.135-.687-1.718-.293-2.3-2.379-1.067-3.61L5 14.5" />
        </svg>
      </div>

      <h1 className="text-2xl font-semibold text-gray-200 mb-2">
        Health Intelligence Companion
      </h1>
      <p className="text-gray-500 mb-8 text-center max-w-md text-sm">
        Sign in to start chatting with your AI health assistant.
      </p>

      <button
        onClick={onOpenLogin}
        className="px-6 py-2.5 rounded-xl bg-gradient-to-r from-emerald-500 to-teal-600 text-white font-medium text-sm hover:from-emerald-400 hover:to-teal-500 transition-all duration-200 shadow-sm active:scale-[0.98]"
      >
        Sign in
      </button>
    </div>
  );
}

export default function ChatBox({ onOpenLogin }) {
  const { isAuthenticated, loading: authLoading } = useAuth();
  const [collapsed, setCollapsed] = useState(false); // desktop rail hidden
  const [mobileOpen, setMobileOpen] = useState(false); // mobile drawer open

  // The chat header's hamburger opens the sidebar in the way that fits the
  // current viewport: re-open the rail on desktop, slide in the drawer on
  // mobile.
  const openSidebar = () => {
    if (window.matchMedia("(min-width: 768px)").matches) setCollapsed(false);
    else setMobileOpen(true);
  };

  if (authLoading) return <AuthSkeleton />;
  if (!isAuthenticated) return <SignInPrompt onOpenLogin={onOpenLogin} />;

  return (
    <div className="flex h-[calc(100vh-65px)] overflow-hidden bg-[#212121]">
      <Sidebar
        collapsed={collapsed}
        onToggleCollapsed={() => setCollapsed(true)}
        mobileOpen={mobileOpen}
        onCloseMobile={() => setMobileOpen(false)}
      />
      <main className="flex min-w-0 flex-1 flex-col">
        <ChatWindow onOpenSidebar={openSidebar} />
      </main>
    </div>
  );
}
