import { useConversations } from "../context/ConversationsContext";
import ConversationItem from "./ConversationItem";

function PlusIcon() {
  return (
    <svg className="h-4 w-4 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
      <path strokeLinecap="round" strokeLinejoin="round" d="M12 4.5v15m7.5-7.5h-15" />
    </svg>
  );
}

function CollapseIcon() {
  return (
    <svg className="h-4 w-4 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
      <path strokeLinecap="round" strokeLinejoin="round" d="M3.75 6.75h16.5M3.75 12h16.5m-16.5 5.25h16.5" />
    </svg>
  );
}

function XIcon() {
  return (
    <svg className="h-4 w-4 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
      <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
    </svg>
  );
}

/**
 * The pieces shared by both the desktop rail and the mobile drawer:
 * New Chat button, the conversation list, and the footer action.
 */
function SidebarInner({ onToggleCollapsed, onCloseMobile, mobile }) {
  const { conversations, listLoading, busy, selectedThreadId, newChat, selectConversation } =
    useConversations();

  return (
    <>
      {/* New Chat */}
      <div className="p-3">
        <button
          type="button"
          onClick={newChat}
          disabled={busy}
          title="Start a new conversation"
          className="flex w-full items-center gap-2.5 rounded-xl border border-white/10 bg-white/5 px-3 py-2.5 text-sm font-medium text-gray-200 transition-colors duration-150 hover:border-white/20 hover:bg-white/10 disabled:cursor-not-allowed disabled:opacity-60"
        >
          <PlusIcon />
          <span className="truncate">New chat</span>
        </button>
      </div>

      {/* Conversation list */}
      <div className="flex-1 overflow-y-auto px-2.5 pb-2 scrollbar-thin">
        {listLoading ? (
          <div className="space-y-2 px-1 pt-1">
            {[...Array(5)].map((_, i) => (
              <div key={i} className="h-14 animate-pulse rounded-lg bg-white/5" />
            ))}
          </div>
        ) : conversations.length === 0 ? (
          <div className="px-3 pt-6 text-center">
            <p className="text-sm text-gray-500">No conversations yet</p>
            <p className="mt-1 text-xs text-gray-600">Start a new chat to begin.</p>
          </div>
        ) : (
          <div className="space-y-0.5">
            {conversations.map((c) => (
              <ConversationItem
                key={c.thread_id}
                conversation={c}
                active={c.thread_id === selectedThreadId}
                disabled={busy}
                onClick={() => selectConversation(c.thread_id)}
              />
            ))}
          </div>
        )}
      </div>

      {/* Footer */}
      <div className="border-t border-white/10 p-3">
        {mobile ? (
          <button
            type="button"
            onClick={onCloseMobile}
            className="flex w-full items-center gap-2.5 rounded-lg px-3 py-2.5 text-sm text-gray-400 transition-colors duration-150 hover:bg-white/5 hover:text-gray-200"
          >
            <XIcon />
            <span>Close sidebar</span>
          </button>
        ) : (
          <button
            type="button"
            onClick={onToggleCollapsed}
            className="flex w-full items-center gap-2.5 rounded-lg px-3 py-2.5 text-sm text-gray-400 transition-colors duration-150 hover:bg-white/5 hover:text-gray-200"
          >
            <CollapseIcon />
            <span>Collapse sidebar</span>
          </button>
        )}
      </div>
    </>
  );
}

/**
 * The sidebar. On desktop it's a fixed-width (280px) rail that can be
 * collapsed away; on mobile it slides in as an overlay drawer over a
 * dimmed backdrop. Both share SidebarInner so the list stays consistent.
 */
export default function Sidebar({ collapsed, onToggleCollapsed, mobileOpen, onCloseMobile }) {
  return (
    <>
      {/* Desktop rail */}
      <aside
        className={`hidden w-[280px] shrink-0 flex-col border-r border-white/10 bg-[#1b1b1b] ${
          collapsed ? "md:hidden" : "md:flex"
        }`}
      >
        <SidebarInner onToggleCollapsed={onToggleCollapsed} />
      </aside>

      {/* Mobile backdrop */}
      <div
        className={`fixed inset-0 z-40 bg-black/60 transition-opacity duration-300 md:hidden ${
          mobileOpen ? "opacity-100" : "pointer-events-none opacity-0"
        }`}
        onClick={onCloseMobile}
      />

      {/* Mobile drawer */}
      <aside
        className={`fixed inset-y-0 left-0 z-50 flex w-[280px] flex-col bg-[#1b1b1b] transition-transform duration-300 md:hidden ${
          mobileOpen ? "translate-x-0" : "-translate-x-full"
        }`}
      >
        <SidebarInner mobile onCloseMobile={onCloseMobile} />
      </aside>
    </>
  );
}
