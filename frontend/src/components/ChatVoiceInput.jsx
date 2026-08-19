// srs/components/ChatVoiceInput.jsx
import { useState, useRef, useEffect } from "react";
import { API_BASE } from "../utils/config";

/* ── Icons ────────────────────────────────────────── */

const MicIcon = () => (
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
      d="M12 18.75a6 6 0 006-6v-1.5m-6 7.5a6 6 0 01-6-6v-1.5m6 7.5v3.75m-3.75 0h7.5M12 15.75a3 3 0 01-3-3V4.5a3 3 0 016 0v8.25a3 3 0 01-3 3z"
    />
  </svg>
);

const CheckIcon = () => (
  <svg
    className="w-5 h-5"
    fill="none"
    viewBox="0 0 24 24"
    stroke="currentColor"
    strokeWidth={2}
  >
    <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
  </svg>
);

const CancelIcon = () => (
  <svg
    className="w-4 h-4"
    fill="none"
    viewBox="0 0 24 24"
    stroke="currentColor"
    strokeWidth={2}
  >
    <path
      strokeLinecap="round"
      strokeLinejoin="round"
      d="M6 18L18 6M6 6l12 12"
    />
  </svg>
);

const SpinnerIcon = () => (
  <svg
    className="w-5 h-5 animate-spin"
    fill="none"
    viewBox="0 0 24 24"
    stroke="currentColor"
  >
    <circle
      className="opacity-25"
      cx="12"
      cy="12"
      r="10"
      stroke="currentColor"
      strokeWidth="4"
    />
    <path
      className="opacity-75"
      fill="currentColor"
      d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"
    />
  </svg>
);

/**
 * ChatVoiceInput — inline Push-to-Talk / Confirm voice input.
 *
 * Flow:
 *   1. User clicks Record → microphone audio is captured locally.
 *   2. User clicks OK      → recording stops, audio is POSTed to /voice/stt.
 *   3. Transcribed text is passed to onSendMessage (parent → agent pipeline).
 *   4. The assistant reply is rendered in the conversation window.
 *   5. Optional TTS playback of the reply (toggle via speaker icon).
 */
export default function ChatVoiceInput({ onSendMessage, disabled }) {
  const [phase, setPhase] = useState("idle");
  const [error, setError] = useState("");
  const [ttsEnabled, setTtsEnabled] = useState(true);
  const [isSpeaking, setIsSpeaking] = useState(false);
  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);
  const streamRef = useRef(null);
  const audioRef = useRef(null);

  useEffect(() => {
  const stopOnUnload = () => {
    navigator.sendBeacon(`${API_BASE}/voice/stop`);
  };
  window.addEventListener("pagehide", stopOnUnload);
  return () => {
    window.removeEventListener("pagehide", stopOnUnload);
    if (audioRef.current) audioRef.current.pause();
  };
}, []);
  const stopStream = () => {
    if (streamRef.current) {
      streamRef.current.getTracks().forEach((t) => t.stop());
      streamRef.current = null;
    }
  };

  const startRecording = async () => {
    audioChunksRef.current = [];
    setError("");
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      streamRef.current = stream;
      mediaRecorderRef.current = new MediaRecorder(stream, {
        mimeType: "audio/webm",
      });
      mediaRecorderRef.current.ondataavailable = (e) => {
        if (e.data.size > 0) audioChunksRef.current.push(e.data);
      };
      mediaRecorderRef.current.start();
      setPhase("recording");
    } catch (err) {
      setError(
        err.name === "NotAllowedError"
          ? "Microphone access denied"
          : "Microphone unavailable"
      );
    }
  };

  const cancelRecording = () => {
    if (
      mediaRecorderRef.current &&
      mediaRecorderRef.current.state !== "inactive"
    ) {
      mediaRecorderRef.current.stop();
    }
    stopStream();
    setPhase("idle");
    setError("");
  };

  const stopAndConfirm = () => {
    if (!mediaRecorderRef.current || phase !== "recording") return;

    mediaRecorderRef.current.stop();
    setPhase("processing");

    mediaRecorderRef.current.onstop = async () => {
      const blob = new Blob(audioChunksRef.current, { type: "audio/webm" });
      audioChunksRef.current = [];
      stopStream();

      if (blob.size === 0) {
        setPhase("idle");
        setError("No audio captured");
        return;
      }

      try {
        const formData = new FormData();
        formData.append("audio", blob, "voice_input.webm");

        const res = await fetch(`${API_BASE}/voice/stt`, {
          method: "POST",
          body: formData,
        });

        if (!res.ok) throw new Error(`STT request failed: ${res.status}`);

        const data = await res.json();
        const text = (data.text || "").trim();

        if (!text) {
          setPhase("idle");
          setError("Could not understand audio");
          return;
        }

        const assistantMsg = await onSendMessage(text);

        if (ttsEnabled && assistantMsg?.content) {
          await playTTS(assistantMsg.content);
        }

        setPhase("idle");
      } catch (err) {
        setError(err.message || "Speech recognition failed");
        setPhase("idle");
      }
    };
  };

  const playTTS = async (text) => {
    if (audioRef.current) {
      audioRef.current.pause();
      audioRef.current = null;
    }
    try {
      const res = await fetch(
        `${API_BASE}/voice/tts?text=${encodeURIComponent(text)}`,
        { method: "POST" }
      );
      if (!res.ok) return;
      const blob = await res.blob();
      const url = URL.createObjectURL(blob);
      const audio = new Audio(url);
      audioRef.current = audio;
      setIsSpeaking(true);

      audio.onended = () => {
        URL.revokeObjectURL(url);
        audioRef.current = null;
        setIsSpeaking(false);
      };
      audio.onerror = () => {
        URL.revokeObjectURL(url);
        audioRef.current = null;
        setIsSpeaking(false);
      };

      audio.play();
    } catch (err) {
      console.error("TTS error:", err);
      setIsSpeaking(false);
    }
  };

  const toggleTTS = () => setTtsEnabled(!ttsEnabled);

  const stopSpeaking = async () => {
    try {
      await fetch(`${API_BASE}/voice/stop`, { method: "POST" });
    } catch (err) {
      console.error("Stop playback error:", err);
    }
    if (audioRef.current) {
      audioRef.current.pause();
      audioRef.current = null;
    }
    setIsSpeaking(false);
  };

  

  useEffect(() => {
    return () => {
      if (audioRef.current) {
        audioRef.current.pause();
        audioRef.current = null;
      }
      fetch(`${API_BASE}/voice/stop`, { method: "POST" }).catch(() => {});
    };
  }, []);

  if (phase === "recording") {
    return (
      <div className="flex items-center gap-1.5">
        <button
          onClick={cancelRecording}
          className="p-1.5 rounded-lg text-gray-500 hover:text-gray-300 hover:bg-white/5 transition-colors"
          title="Cancel recording"
        >
          <CancelIcon />
        </button>
        <button
          onClick={stopAndConfirm}
          className="px-3 py-2 rounded-xl bg-emerald-500/20 text-emerald-300 border border-emerald-500/30 font-medium text-sm animate-pulse"
          title="Stop & send to agent"
        >
          <span className="flex items-center gap-1.5">
            <CheckIcon />
            OK
          </span>
        </button>
        <button
          onClick={toggleTTS}
          className={`p-1.5 rounded-lg border transition-colors ${
            ttsEnabled
              ? "bg-emerald-500/20 text-emerald-300 border-emerald-500/30"
              : "text-gray-500 border-white/10 hover:text-gray-300 hover:bg-white/5"
          }`}
          title={ttsEnabled ? "TTS on (play reply)" : "TTS off"}
        >
          <svg
            className="w-4 h-4"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
            strokeWidth={2}
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              d="M5.586 15H4a1 1 0 01-1-1v-4a1 1 0 011-1h1.586l4.707-4.707C10.923 3.663 12 4.109 12 5v14c0 .891-1.077 1.337-1.707.707L5.586 15z"
            />
          </svg>
        </button>
      </div>
    );
  }

  if (phase === "processing") {
    return (
      <div className="flex items-center gap-1.5">
        <button
          disabled
          className="p-2 rounded-xl bg-white/5 text-gray-400 border border-white/10"
        >
          <SpinnerIcon />
        </button>
        <span className="text-xs text-gray-500">Transcribing…</span>
      </div>
    );
  }

  return (
    <div className="flex items-center gap-1.5">
      {isSpeaking ? (
        <button
          onClick={stopSpeaking}
          className="p-2 rounded-xl bg-red-500/20 text-red-300 border border-red-500/30 hover:bg-red-500/30 transition-all duration-200"
          title="Stop speaking"
        >
          <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M5.25 7.5A2.25 2.25 0 017.5 5.25h9a2.25 2.25 0 012.25 2.25v9a2.25 2.25 0 01-2.25 2.25h-9a2.25 2.25 0 01-2.25-2.25v-9z" />
          </svg>
        </button>
      ) : (
        <button
          onClick={startRecording}
          disabled={disabled}
          className="p-2 rounded-xl bg-white/5 hover:bg-white/10 text-gray-400 hover:text-emerald-300 border border-white/10 transition-all duration-200 disabled:opacity-40"
          title="Voice input (push to talk)"
        >
          <MicIcon />
        </button>
      )}

      {isSpeaking && (
    <button
      onClick={stopTTS}
      className="p-1.5 rounded-lg text-red-300 bg-red-500/20 border border-red-500/30 hover:bg-red-500/30 transition-colors"
      title="Stop speaking"
    >
      <CancelIcon />
    </button>
  )}
      <button
        onClick={toggleTTS}
        className={`p-1.5 rounded-lg border text-xs transition-colors ${
          ttsEnabled
            ? "bg-emerald-500/20 text-emerald-300 border-emerald-500/30"
            : "text-gray-500 border-white/10 hover:text-gray-300 hover:bg-white/5"
        }`}
        title={ttsEnabled ? "TTS on" : "TTS off"}
      >
        {ttsEnabled ? "TTS" : "TTS"}
      </button>
      {error && (
        <span className="text-xs text-gray-500 max-w-[140px] truncate" title={error}>
          {error}
        </span>
      )}
    </div>
  );
}
