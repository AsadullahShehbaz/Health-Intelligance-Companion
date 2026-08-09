import { createContext, useCallback, useContext, useEffect, useState } from "react";
import { useAuth } from "./AuthContext";
import api from "../utils/api";

/**
 * Owns everything the conversation-history UI needs: the sidebar list, the
 * currently active LangGraph thread, and the restored message transcript.
 *
 * The backend is the single source of truth — the list is fetched from
 * /agent/threads and a thread's messages from /agent/threads/{id}; we keep
 * no separate local store. State is shared here (via the context) so
 * Sidebar and ChatWindow stay in sync without prop drilling.
 */
const ConversationsContext = createContext(null);

export function ConversationsProvider({ children }) {
  const { user, isAuthenticated } = useAuth();
  const patientId = user?.id || user?.username || "guest";

  const [conversations, setConversations] = useState([]);
  // Starts true: the provider remounts on every sign-in (keyed by user id in
  // App.jsx), so the sidebar shows its skeleton until the first fetch lands.
  const [listLoading, setListLoading] = useState(true);
  const [historyLoading, setHistoryLoading] = useState(false);
  const [sending, setSending] = useState(false);
  const [messages, setMessages] = useState([]);
  // A brand-new chat gets a fresh UUID thread id; selecting an existing
  // conversation replaces it with that conversation's thread id.
  const [activeThreadId, setActiveThreadId] = useState(() => crypto.randomUUID());
  // Which sidebar row is highlighted. null for a brand-new chat that has not
  // been persisted yet (there is no row for it).
  const [selectedThreadId, setSelectedThreadId] = useState(null);

  const busy = historyLoading || sending;

  // Load the sidebar list when a patient signs in. The whole provider is
  // keyed by user id in App.jsx, so a sign-out / sign-in as another patient
  // remounts it and all state here starts fresh — no reset needed in this
  // effect (which would cause a synchronous render loop).
  useEffect(() => {
    if (!isAuthenticated) return;

    let cancelled = false;
    api
      .get("/agent/threads")
      .then((list) => {
        if (!cancelled) setConversations(list);
      })
      .catch((err) => console.error("Failed to load conversations:", err))
      .finally(() => {
        if (!cancelled) setListLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, [patientId, isAuthenticated]);

  /** Refresh the sidebar list (after a send, so timestamps/new threads show). */
  const refreshList = useCallback(async () => {
    if (!isAuthenticated) return;
    try {
      const list = await api.get("/agent/threads");
      setConversations(list);
      setSelectedThreadId((prev) => {
        // Highlight the thread we're actively chatting in once it persists.
        if (list.some((c) => c.thread_id === activeThreadId)) return activeThreadId;
        return list.some((c) => c.thread_id === prev) ? prev : null;
      });
    } catch (err) {
      console.error("Failed to refresh conversations:", err);
    }
  }, [isAuthenticated, activeThreadId]);

  /** Start a fresh conversation: new thread id, empty window. */
  const newChat = useCallback(() => {
    const threadId = crypto.randomUUID();
    setActiveThreadId(threadId);
    setSelectedThreadId(null);
    setMessages([]);
  }, []);

  /** Resume an existing conversation from its checkpoints. */
  const selectConversation = useCallback(async (threadId) => {
    setSelectedThreadId(threadId);
    setHistoryLoading(true);
    try {
      const detail = await api.get(`/agent/threads/${threadId}`);
      setActiveThreadId(detail.thread_id);
      setMessages(detail.messages || []);
    } catch (err) {
      console.error("Failed to load conversation:", err);
    } finally {
      setHistoryLoading(false);
    }
  }, []);

  return (
    <ConversationsContext.Provider
      value={{
        patientId,
        conversations,
        listLoading,
        historyLoading,
        sending,
        setSending,
        busy,
        messages,
        activeThreadId,
        selectedThreadId,
        setMessages,
        setSelectedThreadId,
        newChat,
        selectConversation,
        refreshList,
      }}
    >
      {children}
    </ConversationsContext.Provider>
  );
}

export function useConversations() {
  const ctx = useContext(ConversationsContext);
  if (!ctx) throw new Error("useConversations must be used within a ConversationsProvider");
  return ctx;
}
