import { formatRelativeTime } from "../utils/time";

/**
 * One row in the sidebar: conversation title, last-updated time, and a
 * one-line snippet. Highlights when it's the active conversation.
 */
export default function ConversationItem({ conversation, active, onClick, disabled }) {
  const { title, updated_at, snippet } = conversation;

  return (
    <button
      type="button"
      onClick={onClick}
      disabled={disabled}
      title={title}
      className={`group w-full flex flex-col items-start gap-0.5 rounded-lg px-3 py-2.5 text-left transition-colors duration-150 disabled:cursor-not-allowed disabled:opacity-60 ${
        active
          ? "bg-white/10 text-gray-100"
          : "text-gray-400 hover:bg-white/5 hover:text-gray-200"
      }`}
    >
      <span className="w-full truncate text-sm font-medium leading-snug">{title}</span>
      <span className="flex w-full items-center gap-2 text-[11px] text-gray-500">
        <span className="shrink-0">{formatRelativeTime(updated_at)}</span>
        {snippet && <span className="truncate opacity-70">{snippet}</span>}
      </span>
    </button>
  );
}
