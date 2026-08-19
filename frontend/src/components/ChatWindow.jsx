import { useRef, useState, useEffect } from "react";
import { useConversations } from "../context/ConversationsContext";
import { api, getStreamUrl, getAuthHeaders } from "../utils/api";
import { ensureFreshToken } from "../utils/session";
import { API_BASE } from "../utils/config";
import { fileToImageData } from "../utils/image";
import { formatRelativeTime } from "../utils/time";
import VoiceAssistantModal from "./VoiceAssistantModal";
import ChatVoiceInput from "./ChatVoiceInput";

// ─── Markdown Renderer ─────────────────────────────────────────

function CodeBlock({ code, language }) {
  const [copied, setCopied] = useState(false);

  const copy = async () => {
    try {
      await navigator.clipboard.writeText(code);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch { /* clipboard not available */ }
  };

  return (
    <div className="my-3 rounded-xl overflow-hidden border border-white/10 bg-black/40">
      <div className="flex items-center justify-between px-4 py-2 bg-white/5 border-b border-white/10">
        <span className="text-xs text-gray-500 font-mono">
          {language || "code"}
        </span>
        <button
          onClick={copy}
          className="text-xs text-gray-500 hover:text-gray-300 transition-colors flex items-center gap-1.5 px-2 py-1 rounded-md hover:bg-white/5"
        >
          {copied ? (
            <>
              <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" /></svg>
              Copied!
            </>
          ) : (
            <>
              <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" /></svg>
              Copy
            </>
          )}
        </button>
      </div>
      <pre className="p-4 overflow-x-auto text-sm leading-relaxed scrollbar-thin">
        <code className="text-gray-300 font-mono">{code}</code>
      </pre>
    </div>
  );
}

function InlineContent({ text }) {
  if (!text) return null;

  const parts = text.split(/(`[^`]+`)/g);

  return (
    <div className="space-y-2">
      {parts.map((part, i) => {
        if (part.startsWith("`") && part.endsWith("`")) {
          return (
            <code key={i} className="px-1.5 py-0.5 bg-white/10 rounded-md text-sm font-mono text-emerald-300">
              {part.slice(1, -1)}
            </code>
          );
        }
        const segments = [];
        let lastIdx = 0;
        const boldRe = /\*\*(.+?)\*\*/g;
        let match;
        while ((match = boldRe.exec(part)) !== null) {
          if (match.index > lastIdx) segments.push({ t: "text", v: part.slice(lastIdx, match.index) });
          segments.push({ t: "bold", v: match[1] });
          lastIdx = match.index + match[0].length;
        }
        if (lastIdx < part.length) segments.push({ t: "text", v: part.slice(lastIdx) });

        const processed = segments.map((seg, j) => {
          if (seg.t === "bold") return <strong key={j} className="font-semibold text-gray-100">{seg.v}</strong>;
          const italicParts = seg.v.split(/(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)/g);
          if (italicParts.length === 1) {
            const urlRe = /(https?:\/\/[^\s]+)/g;
            const urlParts = seg.v.split(urlRe);
            if (urlParts.length === 1) return seg.v;
            return urlParts.map((u, k) =>
              urlRe.test(u)
                ? <a key={k} href={u} target="_blank" rel="noopener noreferrer" className="text-blue-400 hover:underline">{u}</a>
                : u
            );
          }
          return italicParts.map((ip, k) =>
            k % 2 === 1
              ? <em key={k} className="text-gray-300">{ip}</em>
              : ip
          );
        });

        return <p key={i} className="text-gray-200 leading-relaxed whitespace-pre-wrap text-sm">{processed}</p>;
      })}
    </div>
  );
}

function MarkdownContent({ content }) {
  if (!content) return null;

  const parts = content.split(/(```[\s\S]*?```)/g);

  return (
    <div className="prose prose-invert max-w-none">
      {parts.map((part, i) => {
        if (/^```[\s\S]*```$/.test(part)) {
          const firstNewline = part.indexOf("\n");
          const lang = firstNewline > 3 ? part.slice(3, firstNewline).trim() : "";
          const codeStart = firstNewline > 0 ? firstNewline + 1 : 3;
          const code = part.slice(codeStart, -3);
          return <CodeBlock key={i} code={code} language={lang} />;
        }
        return <InlineContent key={i} text={part} />;
      })}
    </div>
  );
}

// ─── Copy Button ──────────────────────────────────────────────

function CopyButton({ content }) {
  const [copied, setCopied] = useState(false);

  const copy = async () => {
    try {
      await navigator.clipboard.writeText(content);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch { /* clipboard not available */ }
  };

  return (
    <button
      onClick={(e) => { e.stopPropagation(); copy(); }}
      className="opacity-0 group-hover:opacity-100 transition-opacity duration-200 p-1.5 rounded-lg hover:bg-white/10 text-gray-500 hover:text-gray-300"
      title="Copy message"
    >
      {copied ? (
        <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
        </svg>
      ) : (
        <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
        </svg>
      )}
    </button>
  );
}

// ─── Typing Indicator ───────────────────────────────────────────

function TypingIndicator() {
  return (
    <div className="flex items-start gap-3 px-4 py-4 animate-fade-in">
      <div className="flex-shrink-0 w-8 h-8 rounded-full bg-gradient-to-br from-emerald-400 to-teal-600 flex items-center justify-center shadow-sm">
        <svg className="w-4 h-4 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.75 3.104v5.714a2.25 2.25 0 01-.659 1.591L5 14.5M9.75 3.104c-.251.023-.501.05-.75.082m.75-.082a24.301 24.301 0 014.5 0m0 0v5.714c0 .597.237 1.17.659 1.591L19.8 15.3M14.25 3.104c.251.023.501.05.75.082M19.8 15.3l-1.57.393A9.065 9.065 0 0112 15a9.065 9.065 0 00-6.23.693L5 14.5m14.8.8l1.402 1.402c1.232 1.232.65 3.318-1.067 3.611A48.309 48.309 0 0112 21c-2.773 0-5.491-.235-8.135-.687-1.718-.293-2.3-2.379-1.067-3.61L5 14.5" />
        </svg>
      </div>
      <div className="flex items-center gap-1 pt-2">
        <span className="w-2 h-2 rounded-full bg-gray-500 animate-bounce" style={{ animationDelay: "0ms" }} />
        <span className="w-2 h-2 rounded-full bg-gray-500 animate-bounce" style={{ animationDelay: "150ms" }} />
        <span className="w-2 h-2 rounded-full bg-gray-500 animate-bounce" style={{ animationDelay: "300ms" }} />
      </div>
    </div>
  );
}

// ─── Mode Selector ─────────────────────────────────────────────

const MODES = [
  { key: "agent", label: "Agent", hint: "Multi-step agent: translation, RAG, memory, image OCR" },
  { key: "rag", label: "RAG", hint: "Retrieve context, then stream an answer" },
  { key: "chat", label: "Chat", hint: "Plain streaming chat (no retrieval)" },
];

function ModeSelector({ mode, onChange, disabled }) {
  return (
    <div className="flex items-center gap-1 p-1 bg-[#2f2f2f] rounded-xl border border-white/10 w-fit" title={MODES.find((m) => m.key === mode)?.hint}>
      {MODES.map((m) => (
        <button
          key={m.key}
          onClick={() => onChange(m.key)}
          disabled={disabled}
          title={m.hint}
          className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-all duration-200 disabled:opacity-50 ${
            mode === m.key
              ? "bg-emerald-500/20 text-emerald-300 border border-emerald-500/30"
              : "text-gray-400 border border-transparent hover:text-gray-200 hover:bg-white/5"
          }`}
        >
          {m.label}
        </button>
      ))}
    </div>
  );
}

// ─── Message Metadata Chips ─────────────────────────────────────

function MessageMeta({ meta }) {
  if (!meta) return null;

  const langChip = meta.detected_lang && meta.detected_lang !== "en"
    ? { label: `🌐 ${meta.detected_lang}` }
    : null;
  const ragChip = meta.needs_rag
    ? { label: `🧠 RAG: ${meta.retrieval_decision || "retrieved"}` }
    : { label: "💬 Direct" };

  return (
    <div className="flex flex-wrap items-center gap-1.5 mt-2">
      <span className="text-[10px] uppercase tracking-wider text-gray-600 mr-0.5">agent:</span>
      {langChip && (
        <span className="text-[11px] px-2 py-0.5 rounded-md bg-white/5 border border-white/10 text-gray-400">
          {langChip.label}
        </span>
      )}
      <span className="text-[11px] px-2 py-0.5 rounded-md bg-white/5 border border-white/10 text-gray-400">
        {ragChip.label}
      </span>
      {meta.sources?.length > 0 && (
        <span className="flex items-center gap-1 flex-wrap">
          {meta.sources.map((src, i) => (
            <span
              key={i}
              className="text-[11px] px-2 py-0.5 rounded-md bg-blue-500/10 border border-blue-500/20 text-blue-300 font-mono"
              title="Source"
            >
              {src}
            </span>
          ))}
        </span>
      )}
    </div>
  );
}

// ─── History Skeleton ───────────────────────────────────────────

function HistorySkeleton() {
  return (
    <div className="max-w-3xl mx-auto px-4 pt-6 space-y-6">
      {[...Array(3)].map((_, i) => (
        <div key={i} className="flex items-start gap-3 px-4 animate-pulse">
          <div className="w-8 h-8 rounded-full bg-white/5" />
          <div className="flex-1 space-y-2 pt-1">
            <div className="h-4 w-1/3 bg-white/5 rounded" />
            <div className="h-3 w-full bg-white/5 rounded" />
            <div className="h-3 w-5/6 bg-white/5 rounded" />
          </div>
        </div>
      ))}
    </div>
  );
}

// ─── Header ─────────────────────────────────────────────────────

function HamburgerIcon() {
  return (
    <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.8}>
      <path strokeLinecap="round" strokeLinejoin="round" d="M3.75 6.75h16.5M3.75 12h16.5m-16.5 5.25h16.5" />
    </svg>
  );
}

// ─── Main Component ─────────────────────────────────────────────

export default function ChatWindow({ onOpenSidebar }) {
  const {
    patientId,
    conversations,
    messages,
    setMessages,
    activeThreadId,
    historyLoading,
    sending,
    setSending,
    refreshList,
  } = useConversations();

  const [input, setInput] = useState("");
  const [mode, setMode] = useState("agent");
  const [image, setImage] = useState(null);
  const [showVoice, setShowVoice] = useState(false);
  const bottomRef = useRef(null);
  const textareaRef = useRef(null);
  const fileInputRef = useRef(null);

  const busy = historyLoading || sending;
  const current = conversations.find((c) => c.thread_id === activeThreadId);
  const headerTitle = current?.title || "New chat";

  useEffect(() => {
    const el = textareaRef.current;
    if (el) {
      el.style.height = "auto";
      el.style.height = Math.min(el.scrollHeight, 200) + "px";
    }
  }, [input]);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, sending]);

  const streamChat = async (endpoint, history) => {
    await ensureFreshToken();
    const res = await fetch(getStreamUrl(endpoint), {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...getAuthHeaders(),
      },
      body: JSON.stringify({ messages: history }),
    });

    if (res.status === 401) {
      throw new Error('Session expired. Please sign in again.');
    }

    if (!res.ok) throw new Error(`Server returned ${res.status}`);

    const reader = res.body.getReader();
    const decoder = new TextDecoder();
    let assistantMsg = { role: 'assistant', content: '' };
    setMessages([...history, assistantMsg]);

    while (true) {
      const { value, done } = await reader.read();
      if (done) break;
      assistantMsg = {
        ...assistantMsg,
        content: assistantMsg.content + decoder.decode(value, { stream: true }),
      };
      setMessages([...history, { ...assistantMsg }]);
    }
  };

  const runAgent = async (text, attachedImage) => {
    const payload = {
      patient_id: patientId,
      query: text,
      thread_id: activeThreadId,
    };
    if (attachedImage) payload.image_base64 = attachedImage.base64;

    const data = await api.post("/agent/invoke", payload);

    return {
      role: "assistant",
      content: data.answer,
      meta: {
        detected_lang: data.detected_lang,
        needs_rag: data.needs_rag,
        retrieval_decision: data.retrieval_decision,
        sources: data.sources || [],
      },
    };
  };

  const sendMessage = async (overrideText) => {
    const text = overrideText !== undefined ? overrideText : input;
    if (!text.trim() || busy) return null;

    const userMsg = { role: "user", content: text };
    if (image) userMsg.imageDataUrl = image.dataUrl;
    const history = [...messages, userMsg];
    const attachedImage = image;

    setMessages(history);
    setInput("");
    setImage(null);
    setSending(true);

    try {
      if (mode === "agent") {
        const assistantMsg = await runAgent(text, attachedImage);
        setMessages([...history, assistantMsg]);
        refreshList();
        return assistantMsg;
      } else {
        const endpoint = mode === "rag" ? "/rag/stream" : "/chat/stream";
        await streamChat(endpoint, history);
        return null;
      }
    } catch (err) {
      console.error("Chat error:", err);
      const extra = mode === "agent" && attachedImage
        ? " The agent endpoint needs a running server with the LangGraph stack (checkpointer + Qdrant)."
        : "";
      setMessages([
        ...history,
        {
          role: 'assistant',
          content: `**Connection error:** ${err.message}\n\nMake sure your local API server is running at \`${API_BASE}\`.${extra}`,
        },
      ]);
    } finally {
      setSending(false);
    }
  };

  const handleVoiceMessageSent = (userMsg, assistantMsg) => {
    setMessages((prev) => [...prev, userMsg, assistantMsg]);
    refreshList();
  };

  const handleFileChange = async (e) => {
    const file = e.target.files?.[0];
    e.target.value = "";
    if (!file) return;
    try {
      const img = await fileToImageData(file);
      setImage(img);
    } catch (err) {
      console.error("Image read failed:", err);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const handleSuggestion = (text) => {
    sendMessage(text);
  };

  return (
    <div className="flex h-full flex-col">
      <div className="flex h-12 shrink-0 items-center gap-2 border-b border-white/10 px-3">
        <button
          type="button"
          onClick={onOpenSidebar}
          aria-label="Toggle sidebar"
          title="Toggle sidebar"
          className="rounded-lg p-1.5 text-gray-400 transition-colors duration-150 hover:bg-white/5 hover:text-gray-200"
        >
          <HamburgerIcon />
        </button>
        <span className="truncate text-sm text-gray-300">{headerTitle}</span>
      </div>

      <div className="flex-1 overflow-y-auto scrollbar-thin">
        {historyLoading ? (
          <HistorySkeleton />
        ) : messages.length === 0 && !sending ? (
          <div className="flex flex-col items-center justify-center h-full px-4 animate-fade-in">
            <div className="w-14 h-14 rounded-2xl bg-gradient-to-br from-emerald-400 to-teal-600 flex items-center justify-center shadow-lg shadow-emerald-500/20 mb-6 ring-1 ring-white/10">
              <svg className="w-8 h-8 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9.75 3.104v5.714a2.25 2.25 0 01-.659 1.591L5 14.5M9.75 3.104c-.251.023-.501.05-.75.082m.75-.082a24.301 24.301 0 014.5 0m0 0v5.714c0 .597.237 1.17.659 1.591L19.8 15.3M14.25 3.104c.251.023.501.05.75.082M19.8 15.3l-1.57.393A9.065 9.065 0 0112 15a9.065 9.065 0 00-6.23.693L5 14.5m14.8.8l1.402 1.402c1.232 1.232.65 3.318-1.067 3.611A48.309 48.309 0 0112 21c-2.773 0-5.491-.235-8.135-.687-1.718-.293-2.3-2.379-1.067-3.61L5 14.5" />
              </svg>
            </div>

            <h1 className="text-2xl font-semibold text-gray-200 mb-2">
              Health Intelligence Companion
            </h1>
            <p className="text-gray-500 mb-8 text-center max-w-md text-sm">
              Ask me anything about health, wellness, and medical information
            </p>

            <div className="grid grid-cols-2 gap-3 max-w-lg w-full px-4">
              {[
                "What are the symptoms of vitamin D deficiency?",
                "Explain how the immune system works",
                "Give me a heart-healthy meal plan",
                "Best exercises for lower back pain?",
              ].map((suggestion) => (
                <button
                  key={suggestion}
                  onClick={() => handleSuggestion(suggestion)}
                  className="text-left text-sm text-gray-400 bg-white/5 hover:bg-white/[0.08] border border-white/10 hover:border-white/20 rounded-xl px-4 py-3 transition-all duration-200 leading-relaxed"
                >
                  {suggestion}
                </button>
              ))}
            </div>
          </div>
        ) : (
          <div className="max-w-3xl mx-auto px-4 pt-4 pb-2">
            {messages.map((msg, i) => (
              <div key={i} className="animate-fade-in">
                {msg.role === "user" ? (
                  <div className="flex justify-end px-4 py-2 group">
                    <div className="max-w-[75%] bg-[#2f2f2f] text-gray-100 rounded-2xl rounded-tr-sm px-4 py-2.5 relative">
                      {msg.imageDataUrl && (
                        <div className="mb-2">
                          <img
                            src={msg.imageDataUrl}
                            alt="Attached"
                            className="max-h-40 rounded-lg border border-white/10 object-contain"
                          />
                        </div>
                      )}
                      <p className="whitespace-pre-wrap text-sm leading-relaxed">{msg.content}</p>
                      <div className="flex justify-end mt-1 -mb-1">
                        <CopyButton content={msg.content} />
                      </div>
                    </div>
                  </div>
                ) : (
                  <div className="flex items-start gap-3 px-4 py-2 group">
                    <div className="flex-shrink-0 w-8 h-8 rounded-full bg-gradient-to-br from-emerald-400 to-teal-600 flex items-center justify-center shadow-sm mt-0.5">
                      <svg className="w-4 h-4 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9.75 3.104v5.714a2.25 2.25 0 01-.659 1.591L5 14.5M9.75 3.104c-.251.023-.501.05-.75.082m.75-.082a24.301 24.301 0 014.5 0m0 0v5.714c0 .597.237 1.17.659 1.591L19.8 15.3M14.25 3.104c.251.023.501.05.75.082M19.8 15.3l-1.57.393A9.065 9.065 0 0112 15a9.065 9.065 0 00-6.23.693L5 14.5m14.8.8l1.402 1.402c1.232 1.232.65 3.318-1.067 3.611A48.309 48.309 0 0112 21c-2.773 0-5.491-.235-8.135-.687-1.718-.293-2.3-2.379-1.067-3.61L5 14.5" />
                      </svg>
                    </div>
                    <div className="flex-1 min-w-0 pt-1">
                      <div className="flex items-center gap-1 mb-1.5">
                        <span className="text-xs font-medium text-gray-400">Assistant</span>
                        <span className="text-[10px] text-gray-600">
                          {msg.timestamp ? formatRelativeTime(msg.timestamp) : "just now"}
                        </span>
                        <div className="ml-auto">
                          <CopyButton content={msg.content} />
                        </div>
                      </div>
                      <MarkdownContent content={msg.content} />
                      <MessageMeta meta={msg.meta} />
                    </div>
                  </div>
                )}
              </div>
            ))}
            {sending && <TypingIndicator />}
            <div ref={bottomRef} />
          </div>
        )}
      </div>

      <div className="border-t border-white/10 bg-[#212121]">
        <div className="max-w-3xl mx-auto px-4 py-3">
          <div className="flex items-center justify-between mb-2">
            <ModeSelector mode={mode} onChange={setMode} disabled={busy} />
            <span className="text-[11px] text-gray-600">
              {mode === "agent"
                ? "Agent: memory · RAG · images · multilingual"
                : mode === "rag"
                  ? "Retrieve context then answer"
                  : "Plain chat, no retrieval"}
            </span>
          </div>

          {image && (
            <div className="flex items-center gap-2 mb-2 bg-[#2f2f2f] rounded-xl border border-white/10 px-3 py-2 w-fit">
              <img src={image.dataUrl} alt="Attached preview" className="h-10 w-10 object-cover rounded-lg border border-white/10" />
              <div className="text-xs text-gray-400 max-w-[180px] truncate">
                <span className="text-gray-200 font-medium">{image.name}</span>
                <span className="block text-[10px] text-gray-600">
                  {mode === "agent" ? "OCR will read the text" : "Only used in Agent mode"}
                </span>
              </div>
              <button
                onClick={() => setImage(null)}
                className="p-1 rounded-md text-gray-500 hover:text-gray-200 hover:bg-white/5 transition-colors"
                title="Remove image"
              >
                <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
          )}

          <div className="relative flex items-end bg-[#2f2f2f] rounded-2xl border border-white/10 focus-within:border-white/20 transition-colors">
            <button
              onClick={() => fileInputRef.current?.click()}
              disabled={busy}
              className="ml-2 mb-3.5 p-2 rounded-lg text-gray-500 hover:text-gray-200 hover:bg-white/5 transition-colors disabled:opacity-40"
              title="Attach an image (OCR in Agent mode)"
            >
              <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.8} d="M2.25 15.75l5.159-5.159a2.25 2.25 0 013.182 0l5.159 5.159m-1.5-1.5l1.409-1.409a2.25 2.25 0 013.182 0l2.909 2.909M3.75 21h16.5A2.25 2.25 0 0022.5 18.75V5.25A2.25 2.25 0 0020.25 3H3.75A2.25 2.25 0 001.5 5.25v13.5A2.25 2.25 0 003.75 21zm9.75-12h.008v.008h-.008V9z" />
              </svg>
            </button>
            <input
              ref={fileInputRef}
              type="file"
              accept="image/*"
              onChange={handleFileChange}
              className="hidden"
            />
            <textarea
              ref={textareaRef}
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder={
                mode === "agent"
                  ? "Describe symptoms, attach a photo, or ask in your language…"
                  : "Message Health Intelligence…"
              }
              disabled={busy}
              rows={1}
              className="flex-1 bg-transparent text-gray-100 placeholder-gray-600 resize-none outline-none px-3 py-3.5 text-sm leading-relaxed max-h-[200px] scrollbar-thin"
            />
            <div className="flex items-center px-3 pb-3.5 gap-2">
              <ChatVoiceInput onSendMessage={sendMessage} disabled={busy} />
              <button
                onClick={() => setShowVoice(true)}
                disabled={busy}
                className="p-2 rounded-xl bg-white/5 hover:bg-white/10 text-gray-400 hover:text-emerald-300 border border-white/10 transition-all duration-200 disabled:opacity-40"
                title="Full voice chat (visualizer + barge-in)"
              >
                <svg
                  className="w-5 h-5"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                  strokeWidth={1.8}
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    d="M5.586 15H4a1 1 0 01-1-1v-4a1 1 0 011-1h1.586l4.707-4.707C10.923 3.663 12 4.109 12 5v14c0 .891-1.077 1.337-1.707.707L5.586 15z"
                  />
                </svg>
              </button>
              <button
                onClick={() => sendMessage()}
                disabled={!input.trim() || busy}
                className="w-8 h-8 rounded-xl bg-white text-gray-900 flex items-center justify-center disabled:opacity-20 disabled:cursor-not-allowed hover:bg-gray-200 transition-all duration-200 active:scale-95"
                title="Send"
              >
                <svg
                  className="w-4 h-4"
                  fill="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path d="M3.478 2.404a.75.75 0 00-.926.941l2.432 7.905H13.5a.75.75 0 010 1.5H4.984l-2.432 7.905a.75.75 0 00.926.94 60.519 60.519 0 0018.445-8.986.75.75 0 000-1.218A60.517 60.517 0 003.478 2.404z" />
                </svg>
              </button>
            </div>
          </div>
          <p className="text-center text-xs text-gray-700 mt-2">
            AI may produce inaccurate information about health topics. Always consult a healthcare professional.
          </p>
        </div>
      </div>

      {showVoice && (
        <VoiceAssistantModal
          patientId={patientId}
          activeThreadId={activeThreadId}
          onClose={() => setShowVoice(false)}
          onMessageSent={handleVoiceMessageSent}
        />
      )}
    </div>
  );
}
