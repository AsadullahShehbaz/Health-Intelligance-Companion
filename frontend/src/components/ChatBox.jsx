import { useState, useRef, useEffect } from "react";
import { useAuth } from "../context/AuthContext";

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
        <span className="text-xs text-gray-500 font-mono">{language || "code"}</span>
        <button
          onClick={copy}
          className="text-xs text-gray-500 hover:text-gray-300 transition-colors flex items-center gap-1.5 px-2 py-1 rounded-md hover:bg-white/5"
        >
          {copied ? (
            <><svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" /></svg>Copied!</>
          ) : (
            <><svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" /></svg>Copy</>
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

  // Split by inline code
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
        // Process **bold** and *italic*, auto-link URLs
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
          // Italic inside text
          const italicParts = seg.v.split(/(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)/g);
          if (italicParts.length === 1) {
            // Auto-link URLs
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

  // Split into code blocks and non-code sections
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

// ─── Main Component ─────────────────────────────────────────────

export default function ChatBox({ onOpenLogin }) {
  const { isAuthenticated, loading: authLoading } = useAuth();
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const bottomRef = useRef(null);
  const textareaRef = useRef(null);

  // Auto-resize textarea
  useEffect(() => {
    const el = textareaRef.current;
    if (el) {
      el.style.height = "auto";
      el.style.height = Math.min(el.scrollHeight, 200) + "px";
    }
  }, [input]);

  // Auto-scroll on new content
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  const sendMessage = async (overrideText) => {
    const text = overrideText !== undefined ? overrideText : input;
    if (!text.trim() || loading) return;

    const userMsg = { role: "user", content: text };
    const newMessages = [...messages, userMsg];
    setMessages(newMessages);
    setInput("");
    setLoading(true);

    try {
      const res = await fetch("http://localhost:8000/chat/stream", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ messages: newMessages }),
      });

      if (!res.ok) throw new Error(`Server returned ${res.status}`);

      const reader = res.body.getReader();
      const decoder = new TextDecoder();
      let assistantMsg = { role: "assistant", content: "" };
      setMessages([...newMessages, assistantMsg]);

      while (true) {
        const { value, done } = await reader.read();
        if (done) break;
        assistantMsg = {
          ...assistantMsg,
          content: assistantMsg.content + decoder.decode(value, { stream: true }),
        };
        setMessages([...newMessages, { ...assistantMsg }]);
      }
    } catch (err) {
      console.error("Chat error:", err);
      setMessages([
        ...messages,
        userMsg,
        {
          role: "assistant",
          content: `**Connection error:** ${err.message}\n\nMake sure your local API server is running at \`http://localhost:8000\`.`,
        },
      ]);
    } finally {
      setLoading(false);
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

  // ── Render ──

  // Auth gate: show skeleton while checking token
  if (authLoading) {
    return (
      <div className="flex flex-col h-[calc(100vh-65px)] bg-[#212121] items-center justify-center">
        <div className="w-14 h-14 rounded-2xl bg-white/5 animate-pulse mb-6" />
        <div className="h-5 w-64 bg-white/5 rounded animate-pulse mb-3" />
        <div className="h-4 w-48 bg-white/5 rounded animate-pulse" />
      </div>
    );
  }

  // Auth gate: prompt to sign in when not authenticated
  if (!isAuthenticated) {
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

  return (
    <div className="flex flex-col h-[calc(100vh-65px)] bg-[#212121]">
      {/* ── Messages Area ── */}
      <div className="flex-1 overflow-y-auto scrollbar-thin">
        {messages.length === 0 && !loading ? (
          /* ── Empty State ── */
          <div className="flex flex-col items-center justify-center h-full px-4 animate-fade-in">
            {/* Logo */}
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

            {/* Suggestion Chips */}
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
          /* ── Message Thread ── */
          <div className="max-w-3xl mx-auto px-4 pt-4 pb-2">
            {messages.map((msg, i) => (
              <div key={i} className="animate-fade-in">
                {msg.role === "user" ? (
                  <div className="flex justify-end px-4 py-2 group">
                    <div className="max-w-[75%] bg-[#2f2f2f] text-gray-100 rounded-2xl rounded-tr-sm px-4 py-2.5 relative">
                      <p className="whitespace-pre-wrap text-sm leading-relaxed">{msg.content}</p>
                      <div className="flex justify-end mt-1 -mb-1">
                        <CopyButton content={msg.content} />
                      </div>
                    </div>
                  </div>
                ) : (
                  <div className="flex items-start gap-3 px-4 py-2 group">
                    {/* Avatar */}
                    <div className="flex-shrink-0 w-8 h-8 rounded-full bg-gradient-to-br from-emerald-400 to-teal-600 flex items-center justify-center shadow-sm mt-0.5">
                      <svg className="w-4 h-4 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9.75 3.104v5.714a2.25 2.25 0 01-.659 1.591L5 14.5M9.75 3.104c-.251.023-.501.05-.75.082m.75-.082a24.301 24.301 0 014.5 0m0 0v5.714c0 .597.237 1.17.659 1.591L19.8 15.3M14.25 3.104c.251.023.501.05.75.082M19.8 15.3l-1.57.393A9.065 9.065 0 0112 15a9.065 9.065 0 00-6.23.693L5 14.5m14.8.8l1.402 1.402c1.232 1.232.65 3.318-1.067 3.611A48.309 48.309 0 0112 21c-2.773 0-5.491-.235-8.135-.687-1.718-.293-2.3-2.379-1.067-3.61L5 14.5" />
                      </svg>
                    </div>
                    {/* Message */}
                    <div className="flex-1 min-w-0 pt-1">
                      <div className="flex items-center gap-1 mb-1.5">
                        <span className="text-xs font-medium text-gray-400">Assistant</span>
                        <span className="text-[10px] text-gray-600">just now</span>
                        <div className="ml-auto">
                          <CopyButton content={msg.content} />
                        </div>
                      </div>
                      <MarkdownContent content={msg.content} />
                    </div>
                  </div>
                )}
              </div>
            ))}
            {loading && <TypingIndicator />}
            <div ref={bottomRef} />
          </div>
        )}
      </div>

      {/* ── Input Area ── */}
      <div className="border-t border-white/10 bg-[#212121]">
        <div className="max-w-3xl mx-auto px-4 py-3">
          <div className="relative flex items-end bg-[#2f2f2f] rounded-2xl border border-white/10 focus-within:border-white/20 transition-colors">
            <textarea
              ref={textareaRef}
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Message Health Intelligence..."
              disabled={loading}
              rows={1}
              className="flex-1 bg-transparent text-gray-100 placeholder-gray-600 resize-none outline-none px-4 py-3.5 text-sm leading-relaxed max-h-[200px] scrollbar-thin"
            />
            <div className="flex items-center px-3 pb-3.5">
              <button
                onClick={() => sendMessage()}
                disabled={!input.trim() || loading}
                className="w-8 h-8 rounded-xl bg-white text-gray-900 flex items-center justify-center disabled:opacity-20 disabled:cursor-not-allowed hover:bg-gray-200 transition-all duration-200 active:scale-95"
              >
                <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 24 24">
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
    </div>
  );
}
