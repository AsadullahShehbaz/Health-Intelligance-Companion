import { useState, useEffect, useCallback } from "react";
import { useAuth } from "../context/AuthContext";
import { fetchPatientMemories, updatePatientMemory } from "../utils/api";

const CATEGORY_LABELS = {
  identity: "Identity",
  symptom: "Symptoms",
  medication: "Medications",
  lab_result: "Lab Results",
  lifestyle: "Lifestyle",
  emotional: "Emotional",
};

const STATUS_COLORS = {
  active: "bg-emerald-500/15 text-emerald-400 border-emerald-500/20",
  resolved: "bg-blue-500/15 text-blue-400 border-blue-500/20",
  historical: "bg-gray-500/15 text-gray-400 border-gray-500/20",
};

const SEVERITY_COLORS = {
  mild: "bg-yellow-500/15 text-yellow-400 border-yellow-500/20",
  moderate: "bg-orange-500/15 text-orange-400 border-orange-500/20",
  severe: "bg-red-500/15 text-red-400 border-red-500/20",
};

function PencilIcon() {
  return (
    <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
      <path strokeLinecap="round" strokeLinejoin="round" d="M16.862 4.487l1.687-1.688a1.875 1.875 0 112.652 2.652L10.582 16.07a4.5 4.5 0 01-1.897 1.13L6 18l.8-2.685a4.5 4.5 0 011.13-1.897l8.932-8.931zm0 0L19.5 7.125M18 14v4.75A2.25 2.25 0 0115.75 21H5.25A2.25 2.25 0 013 18.75V8.25A2.25 2.25 0 015.25 6H10" />
    </svg>
  );
}

function XIcon() {
  return (
    <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
      <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
    </svg>
  );
}

export default function MemoryDashboard({ onClose }) {
  const { user } = useAuth();
  const [memories, setMemories] = useState(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");
  const [editingId, setEditingId] = useState(null);
  const [editForm, setEditForm] = useState({});

  const loadMemories = useCallback(async () => {
    if (!user) return;
    setLoading(true);
    setError("");
    try {
      const data = await fetchPatientMemories(user.id);
      setMemories(data);
    } catch (err) {
      setError(err.message || "Failed to load memories");
    } finally {
      setLoading(false);
    }
  }, [user]);

  useEffect(() => {
    loadMemories();
  }, [loadMemories]);

  useEffect(() => {
    const handleKey = (e) => {
      if (e.key === "Escape") onClose();
    };
    window.addEventListener("keydown", handleKey);
    return () => window.removeEventListener("keydown", handleKey);
  }, [onClose]);

  const startEdit = (item) => {
    setEditingId(item.id);
    setEditForm({
      text: item.text,
      category: item.category,
      status: item.status,
      severity: item.severity || "",
      onset: item.onset || "",
    });
  };

  const cancelEdit = () => {
    setEditingId(null);
    setEditForm({});
  };

  const saveEdit = async (memoryId) => {
    setSaving(true);
    try {
      const updates = {};
      if (editForm.text !== undefined) updates.text = editForm.text;
      if (editForm.category !== undefined) updates.category = editForm.category;
      if (editForm.status !== undefined) updates.status = editForm.status;
      if (editForm.severity !== undefined) updates.severity = editForm.severity || null;
      if (editForm.onset !== undefined) updates.onset = editForm.onset || null;

      const updated = await updatePatientMemory(user.id, memoryId, updates);
      setMemories((prev) => {
        const next = { ...prev };
        next.categories = prev.categories.map((cat) => ({
          ...cat,
          items: cat.items.map((item) =>
            item.id === memoryId ? { ...item, ...updated } : item
          ),
        }));
        return next;
      });
      cancelEdit();
    } catch (err) {
      setError(err.message || "Failed to update memory");
    } finally {
      setSaving(false);
    }
  };

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm animate-fade-in"
      onClick={(e) => { if (e.target === e.currentTarget) onClose(); }}
    >
      <div className="w-full max-w-2xl mx-4 bg-[#212121] border border-white/10 rounded-2xl shadow-2xl max-h-[85vh] flex flex-col">
        <div className="flex items-center justify-between p-5 border-b border-white/10">
          <h2 className="text-lg font-semibold text-gray-200">Memory Dashboard</h2>
          <button
            onClick={onClose}
            className="p-1.5 rounded-lg text-gray-500 hover:text-gray-300 hover:bg-white/5 transition-colors"
          >
            <XIcon />
          </button>
        </div>

        <div className="flex-1 overflow-y-auto p-5 scrollbar-thin">
          {error && (
            <div className="mb-4 bg-red-500/10 border border-red-500/20 rounded-xl px-4 py-2.5 text-sm text-red-400">
              {error}
            </div>
          )}

          {loading ? (
            <div className="space-y-3">
              {[...Array(3)].map((_, i) => (
                <div key={i} className="h-20 animate-pulse rounded-xl bg-white/5" />
              ))}
            </div>
          ) : !memories || memories.categories.every((c) => c.items.length === 0) ? (
            <div className="text-center py-10">
              <p className="text-sm text-gray-500">No memories recorded yet.</p>
              <p className="mt-1 text-xs text-gray-600">Memories will appear here as the conversation progresses.</p>
            </div>
          ) : (
            <div className="space-y-5">
              {memories.categories.map((group) =>
                group.items.length === 0 ? null : (
                  <div key={group.category}>
                    <h3 className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-2">
                      {group.display_name}
                    </h3>
                    <div className="space-y-2">
                      {group.items.map((item) => (
                        <MemoryItemCard
                          key={item.id}
                          item={item}
                          isEditing={editingId === item.id}
                          editForm={editForm}
                          onStartEdit={() => startEdit(item)}
                          onCancelEdit={cancelEdit}
                          onSave={() => saveEdit(item.id)}
                          onFormChange={(field, value) =>
                            setEditForm((prev) => ({ ...prev, [field]: value }))
                          }
                          saving={saving}
                        />
                      ))}
                    </div>
                  </div>
                ),
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

function MemoryItemCard({
  item,
  isEditing,
  editForm,
  onStartEdit,
  onCancelEdit,
  onSave,
  onFormChange,
  saving,
}) {
  if (isEditing) {
    return (
      <div className="bg-[#2f2f2f] border border-white/10 rounded-xl p-3 space-y-2">
        <input
          type="text"
          value={editForm.text}
          onChange={(e) => onFormChange("text", e.target.value)}
          className="w-full bg-[#1b1b1b] border border-white/10 rounded-lg px-3 py-1.5 text-sm text-gray-200 outline-none focus:border-emerald-500/50"
        />
        <div className="flex gap-2">
          <select
            value={editForm.category}
            onChange={(e) => onFormChange("category", e.target.value)}
            className="bg-[#1b1b1b] border border-white/10 rounded-lg px-2 py-1.5 text-xs text-gray-300 outline-none focus:border-emerald-500/50"
          >
            {Object.entries(CATEGORY_LABELS).map(([key, label]) => (
              <option key={key} value={key}>{label}</option>
            ))}
          </select>
          <select
            value={editForm.status}
            onChange={(e) => onFormChange("status", e.target.value)}
            className="bg-[#1b1b1b] border border-white/10 rounded-lg px-2 py-1.5 text-xs text-gray-300 outline-none focus:border-emerald-500/50"
          >
            <option value="active">Active</option>
            <option value="resolved">Resolved</option>
            <option value="historical">Historical</option>
          </select>
          <input
            type="text"
            placeholder="Severity"
            value={editForm.severity}
            onChange={(e) => onFormChange("severity", e.target.value)}
            className="bg-[#1b1b1b] border border-white/10 rounded-lg px-2 py-1.5 text-xs text-gray-300 outline-none focus:border-emerald-500/50 w-24"
          />
          <input
            type="text"
            placeholder="Onset"
            value={editForm.onset}
            onChange={(e) => onFormChange("onset", e.target.value)}
            className="bg-[#1b1b1b] border border-white/10 rounded-lg px-2 py-1.5 text-xs text-gray-300 outline-none focus:border-emerald-500/50 w-24"
          />
        </div>
        <div className="flex justify-end gap-2">
          <button
            onClick={onCancelEdit}
            className="px-3 py-1.5 rounded-lg text-xs text-gray-400 hover:bg-white/5 transition-colors"
          >
            Cancel
          </button>
          <button
            onClick={onSave}
            disabled={saving}
            className="px-3 py-1.5 rounded-lg text-xs text-white bg-gradient-to-r from-emerald-500 to-teal-600 hover:from-emerald-400 hover:to-teal-500 disabled:opacity-50 transition-all"
          >
            {saving ? "Saving..." : "Save"}
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="group flex items-start gap-3 bg-white/[0.03] border border-white/5 rounded-xl p-3 hover:border-white/10 transition-colors">
      <div className="flex-1 min-w-0">
        <p className="text-sm text-gray-300 leading-snug">{item.text}</p>
        <div className="flex flex-wrap gap-1.5 mt-2">
          <span className={`inline-flex items-center px-2 py-0.5 rounded-md text-[10px] font-medium border ${STATUS_COLORS[item.status] || "bg-gray-500/15 text-gray-400 border-gray-500/20"}`}>
            {item.status}
          </span>
          {item.severity && (
            <span className={`inline-flex items-center px-2 py-0.5 rounded-md text-[10px] font-medium border ${SEVERITY_COLORS[item.severity] || "bg-gray-500/15 text-gray-400 border-gray-500/20"}`}>
              {item.severity}
            </span>
          )}
          {item.onset && (
            <span className="inline-flex items-center px-2 py-0.5 rounded-md text-[10px] font-medium border bg-purple-500/15 text-purple-400 border-purple-500/20">
              {item.onset}
            </span>
          )}
        </div>
      </div>
      <button
        onClick={onStartEdit}
        className="mt-1 p-1.5 rounded-lg text-gray-600 opacity-0 group-hover:opacity-100 hover:text-emerald-400 hover:bg-white/5 transition-all"
        title="Edit memory"
      >
        <PencilIcon />
      </button>
    </div>
  );
}
