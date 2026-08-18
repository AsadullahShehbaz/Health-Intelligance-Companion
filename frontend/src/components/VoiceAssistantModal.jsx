import { useState, useEffect, useRef, useCallback } from "react";
import { API_BASE } from "../utils/config";

/**
 * VoiceAssistantModal Component
 * 
 * An interactive, modal-based voice assistant interface featuring real-time HTML5 Canvas 
 * audio visualizers, Speech-to-Text (STT), AI agent query execution, Text-to-Speech (TTS),
 * adjustable playback controls, and automated voice-activity detection (barge-in/auto-interrupt).
 */
export default function VoiceAssistantModal({
  patientId,
  activeThreadId,
  onClose,
  onMessageSent,
}) {
  // ---------------------------------------------------------------------------
  // STATE MANAGEMENT
  // ---------------------------------------------------------------------------
  
  // Current modal operational state: 'idle' | 'recording' | 'processing' | 'speaking'
  const [status, setStatus] = useState("idle");
  
  // User's transcribed speech or fallback text input
  const [transcript, setTranscript] = useState("");
  
  // Response text returned from the AI agent endpoint
  const [agentResponse, setAgentResponse] = useState("");
  
  // Controls whether TTS audio output is muted
  const [muted, setMuted] = useState(false);
  
  // Captures microphone access or Speech-to-Text service error messages
  const [speechError, setSpeechError] = useState(null);
  
  // Speech playback speed rate (persisted in localStorage)
  const [speechRate, setSpeechRate] = useState(() => {
    const saved = localStorage.getItem("voice_speech_rate");
    return saved ? parseFloat(saved) : 1;
  });
  
  // Enables automatic interruption of TTS playback when user speaks over it (persisted in localStorage)
  const [autoInterrupt, setAutoInterrupt] = useState(() => {
    const saved = localStorage.getItem("voice_auto_interrupt");
    return saved === "true";
  });

  // ---------------------------------------------------------------------------
  // REFS & MUTABLE INSTANCES
  // ---------------------------------------------------------------------------
  
  // DOM & Audio API Refs
  const canvasRef = useRef(null);
  const audioContextRef = useRef(null);
  const analyserRef = useRef(null);
  const streamRef = useRef(null);
  const animationRef = useRef(null);
  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);
  const audioRef = useRef(null);

  // Operational & Sync Refs (avoid re-render closures in async loops / callbacks)
  const currentTranscriptRef = useRef("");
  const isSubmittingRef = useRef(false);
  const statusRef = useRef("idle");
  const startTimeRef = useRef(null);
  const silenceStartRef = useRef(null);
  const recordingStartRef = useRef(null);
  const maxDurationTimeoutRef = useRef(null);
  
  // Barge-in (Auto-interrupt) VAD Refs
  const bargeInRafRef = useRef(null);
  const aboveThresholdStartRef = useRef(null);
  const interruptedRef = useRef(false);

  // Synchronized refs for fresh state access in requestAnimationFrame & event listeners
  const autoInterruptRef = useRef(() => {
    const saved = localStorage.getItem("voice_auto_interrupt");
    return saved === "true";
  });
  const speechRateRef = useRef(() => {
    const saved = localStorage.getItem("voice_speech_rate");
    return saved ? parseFloat(saved) : 1;
  });

  // ---------------------------------------------------------------------------
  // CLEANUP & UTILITIES
  // ---------------------------------------------------------------------------

  /**
   * Cleans up hardware resources, active audio contexts, animation loops, 
   * timeouts, and active media recording streams.
   */
  const cleanup = useCallback(() => {
    if (mediaRecorderRef.current && mediaRecorderRef.current.state !== "inactive") {
      mediaRecorderRef.current.stop();
      mediaRecorderRef.current = null;
    }
    if (audioContextRef.current && audioContextRef.current.state !== "closed") {
      audioContextRef.current.close();
      audioContextRef.current = null;
    }
    if (streamRef.current) {
      streamRef.current.getTracks().forEach((t) => t.stop());
      streamRef.current = null;
    }
    if (animationRef.current) {
      cancelAnimationFrame(animationRef.current);
      animationRef.current = null;
    }
    if (audioRef.current) {
      audioRef.current.pause();
      audioRef.current.src = "";
      audioRef.current = null;
    }
    if (maxDurationTimeoutRef.current) {
      clearTimeout(maxDurationTimeoutRef.current);
      maxDurationTimeoutRef.current = null;
    }
    if (bargeInRafRef.current) {
      cancelAnimationFrame(bargeInRafRef.current);
      bargeInRafRef.current = null;
    }
    aboveThresholdStartRef.current = null;
  }, []);

  /**
   * Helper function to render a radial glowing orb on the canvas context.
   */
  const drawOrb = (ctx, x, y, radius, fill, glow) => {
    const innerRadius = Math.max(1, radius * 0.3);
    const outerRadius = Math.max(2, radius * 1.8);
    const gradient = ctx.createRadialGradient(x, y, innerRadius, x, y, outerRadius);
    gradient.addColorStop(0, fill);
    gradient.addColorStop(1, glow);
    ctx.fillStyle = gradient;
    ctx.beginPath();
    ctx.arc(x, y, radius * 1.8, 0, Math.PI * 2);
    ctx.fill();

    ctx.beginPath();
    ctx.arc(x, y, radius, 0, Math.PI * 2);
    ctx.fillStyle = fill;
    ctx.fill();
  };

  // ---------------------------------------------------------------------------
  // CANVAS VISUALIZER LOOP
  // ---------------------------------------------------------------------------

  /**
   * Main render loop for the audio visualization sphere. Dynamically switches mode 
   * based on `statusRef.current`:
   * - Idle: Gentle breathing pulse.
   * - Recording: Dynamic frequency-driven visual orb surrounded by reactive audio frequency bars.
   * - Processing: Orbital spinning dots indicator.
   * - Speaking: Pulsing concentric ripple waves.
   */
  const drawVisualizer = useCallback(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext("2d");
    const analyser = analyserRef.current;
    const bufferLength = analyser ? analyser.frequencyBinCount : 0;
    const dataArray = analyser ? new Uint8Array(bufferLength) : null;

    const draw = () => {
      animationRef.current = requestAnimationFrame(draw);

      const w = canvas.width;
      const h = canvas.height;
      ctx.clearRect(0, 0, w, h);

      const elapsed = (Date.now() - (startTimeRef.current || Date.now())) / 1000;
      const cx = w / 2;
      const cy = h / 2;

      // 1. Idle Visualization Mode
      if (statusRef.current === "idle") {
        const pulse = Math.sin(elapsed * 1.5) * 0.3 + 0.7;
        const radius = 30 * pulse;
        drawOrb(ctx, cx, cy, radius, "rgba(107, 114, 128, 0.35)", "rgba(107, 114, 128, 0.08)");
      
      // 2. Recording Visualization Mode (Audio Frequency Spectrum Analysis)
      } else if (statusRef.current === "recording" && analyser && dataArray) {
        analyser.getByteFrequencyData(dataArray);
        let sum = 0;
        for (let i = 0; i < bufferLength; i++) sum += dataArray[i];
        const avg = sum / bufferLength;
        const radius = 30 + (avg / 255) * 55;

        // Dynamic center orb based on average volume level
        drawOrb(
          ctx,
          cx,
          cy,
          radius,
          "rgba(52, 211, 153, 0.55)",
          "rgba(52, 211, 153, 0.12)"
        );

        // Circular frequency spectrum equalizer bars
        const barCount = 48;
        const step = (Math.PI * 2) / barCount;
        for (let i = 0; i < barCount; i++) {
          const val = dataArray[i] / 255;
          const barHeight = val * 24 + 2;
          const angle = i * step - Math.PI / 2;
          const x1 = cx + Math.cos(angle) * (radius + 10);
          const y1 = cy + Math.sin(angle) * (radius + 10);
          const x2 = cx + Math.cos(angle) * (radius + 10 + barHeight);
          const y2 = cy + Math.sin(angle) * (radius + 10 + barHeight);

          ctx.beginPath();
          ctx.moveTo(x1, y1);
          ctx.lineTo(x2, y2);
          ctx.strokeStyle = `rgba(52, 211, 153, ${0.25 + val * 0.55})`;
          ctx.lineWidth = 2.5;
          ctx.lineCap = "round";
          ctx.stroke();
        }
      
      // 3. Processing Visualization Mode (Rotating Orbit loader)
      } else if (statusRef.current === "processing") {
        const angle = elapsed * 3;
        const orbitRadius = 44;
        ctx.save();
        ctx.translate(cx, cy);
        ctx.rotate(angle);
        for (let i = 0; i < 8; i++) {
          const a = (i / 8) * Math.PI * 2;
          const x = Math.cos(a) * orbitRadius;
          const y = Math.sin(a) * orbitRadius;
          const opacity =
            0.25 + (Math.sin(elapsed * 4 + i * 0.8) * 0.5 + 0.5) * 0.55;
          ctx.beginPath();
          ctx.arc(x, y, 4.5, 0, Math.PI * 2);
          ctx.fillStyle = `rgba(52, 211, 153, ${opacity})`;
          ctx.fill();
        }
        ctx.restore();
      
      // 4. Speaking Visualization Mode (Expanding Ripple Animation)
      } else if (statusRef.current === "speaking") {
        const rippleCount = 3;
        for (let i = 0; i < rippleCount; i++) {
          const phase = (elapsed * 1.8 + i / rippleCount) % 1;
          const radius = 18 + phase * 70;
          const opacity = (1 - phase) * 0.35;
          ctx.beginPath();
          ctx.arc(cx, cy, radius, 0, Math.PI * 2);
          ctx.strokeStyle = `rgba(52, 211, 153, ${opacity})`;
          ctx.lineWidth = 2;
          ctx.stroke();
        }
        drawOrb(
          ctx,
          cx,
          cy,
          34,
          "rgba(52, 211, 153, 0.45)",
          "rgba(52, 211, 153, 0.1)"
        );
      }
    };

    draw();
  }, []);

  // ---------------------------------------------------------------------------
  // AUDIO & QUERY HANDLERS
  // ---------------------------------------------------------------------------

  /**
   * Fetches TTS audio stream from backend and handles playback through HTML5 Audio API.
   */
  const playTTS = useCallback(async (text) => {
    try {
      const response = await fetch(
        `${API_BASE}/voice/tts?text=${encodeURIComponent(text)}`,
        { method: "POST" }
      );
      if (!response.ok) throw new Error("TTS request failed");

      const blob = await response.blob();
      const audioUrl = URL.createObjectURL(blob);
      const audio = new Audio(audioUrl);
      audio.playbackRate = speechRateRef.current;
      audioRef.current = audio;

      audio.onended = () => {
        URL.revokeObjectURL(audioUrl);
        setStatus("idle");
      };

      audio.onerror = () => {
        URL.revokeObjectURL(audioUrl);
        setStatus("idle");
      };

      await audio.play();
    } catch (err) {
      console.error("TTS playback error:", err);
      setStatus("idle");
    }
  }, []);

  /**
   * Halts active TTS playback immediately (used for barge-in or manual stops).
   */
  const interruptPlayback = useCallback(() => {
    interruptedRef.current = true;
    if (audioRef.current) {
      audioRef.current.pause();
      audioRef.current.src = "";
      audioRef.current = null;
    }
    setStatus("idle");
  }, []);

  /**
   * Sends transcribed or manual text query to backend Agent API, handles answer presentation,
   * triggers message history callbacks, and invokes TTS playback if enabled.
   */
  const submitVoiceQuery = useCallback(
    async (queryText) => {
      interruptedRef.current = false;
      setStatus("processing");
      setTranscript(queryText);
      setSpeechError(null);

      try {
        const res = await fetch(`${API_BASE}/agent/invoke`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            patient_id: patientId,
            query: queryText,
            thread_id: activeThreadId,
          }),
        });

        if (!res.ok) throw new Error(`HTTP ${res.status}`);

        const data = await res.json();
        setAgentResponse(data.answer);
        setStatus("speaking");

        // Notify parent application of user and assistant turn-taking
        if (onMessageSent) {
          onMessageSent(
            { role: "user", content: queryText },
            { role: "assistant", content: data.answer }
          );
        }

        // Trigger TTS synthesized speech if not muted or interrupted
        if (!muted && !interruptedRef.current) {
          await playTTS(data.answer);
        } else {
          setTimeout(() => setStatus("idle"), 1000);
        }
      } catch (err) {
        console.error("Voice query error:", err);
        setStatus("idle");
      } finally {
        isSubmittingRef.current = false;
      }
    },
    [patientId, activeThreadId, muted, playTTS, onMessageSent]
  );

  /**
   * Stops active MediaRecorder recording stream.
   */
  const stopRecording = useCallback(() => {
    if (
      mediaRecorderRef.current &&
      mediaRecorderRef.current.state !== "inactive"
    ) {
      mediaRecorderRef.current.stop();
    }
    if (maxDurationTimeoutRef.current) {
      clearTimeout(maxDurationTimeoutRef.current);
      maxDurationTimeoutRef.current = null;
    }
  }, []);

  /**
   * Requests microphone access, configures Web Audio API analyzer node, starts media 
   * recording chunk collection, sets auto-stop timer, and activates canvas visualizer.
   */
  const startListening = useCallback(async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        audio: true,
      });
      streamRef.current = stream;

      // Initialize Web Audio API nodes for visualization and auto-interrupt detection
      const audioCtx = new (window.AudioContext ||
        window.webkitAudioContext)();
      audioContextRef.current = audioCtx;
      const analyser = audioCtx.createAnalyser();
      analyserRef.current = analyser;
      analyser.fftSize = 64;
      analyser.smoothingTimeConstant = 0.8;

      const source = audioCtx.createMediaStreamSource(stream);
      source.connect(analyser);

      // Setup MediaRecorder for capturing WebM audio blobs
      const mediaRecorder = new MediaRecorder(stream);
      mediaRecorderRef.current = mediaRecorder;
      audioChunksRef.current = [];
      currentTranscriptRef.current = "";
      isSubmittingRef.current = false;

      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data);
        }
      };

      // Process recorded audio blob once recording completes
      mediaRecorder.onstop = async () => {
        const blob = new Blob(audioChunksRef.current, { type: "audio/webm" });
        audioChunksRef.current = [];

        if (blob.size === 0) {
          setStatus("idle");
          return;
        }

        setStatus("processing");
        const formData = new FormData();
        formData.append("audio", blob, "recording.webm");

        try {
          // Send WebM audio blob to backend Speech-to-Text endpoint
          const res = await fetch(`${API_BASE}/voice/stt`, {
            method: "POST",
            body: formData,
          });

          if (!res.ok) {
            throw new Error(`STT request failed: ${res.status}`);
          }

          const data = await res.json();
          const text = (data.text || "").trim();

          if (text) {
            await submitVoiceQuery(text);
          } else {
            setStatus("idle");
          }
        } catch (err) {
          console.error("STT request error:", err);
          setSpeechError(err.message || "Speech recognition failed");
          setStatus("idle");
        } finally {
          isSubmittingRef.current = false;
        }
      };

      mediaRecorder.start();

      startTimeRef.current = Date.now();
      recordingStartRef.current = Date.now();
      silenceStartRef.current = null;
      setStatus("recording");
      statusRef.current = "recording";

      // Enforce a maximum continuous recording limit of 15 seconds
      maxDurationTimeoutRef.current = setTimeout(() => {
        stopRecording();
      }, 15000);

      drawVisualizer();
    } catch (err) {
      console.error("Microphone access error:", err);
      setSpeechError(err.message || "Microphone access denied");
      setStatus("idle");
    }
  }, [drawVisualizer, submitVoiceQuery, stopRecording]);

  // ---------------------------------------------------------------------------
  // REACT SIDE EFFECTS & LISTENERS
  // ---------------------------------------------------------------------------

  // Synchronize mutable status ref with React state
  useEffect(() => {
    statusRef.current = status;
  }, [status]);

  // Cleanup component resources on unmount
  useEffect(() => {
    return () => {
      cleanup();
    };
  }, [cleanup]);

  // Persist auto-interrupt preference changes to localStorage
  useEffect(() => {
    autoInterruptRef.current = autoInterrupt;
    localStorage.setItem("voice_auto_interrupt", String(autoInterrupt));
  }, [autoInterrupt]);

  // Dynamically update active TTS audio element playback rate and persist setting
  useEffect(() => {
    if (audioRef.current) {
      audioRef.current.playbackRate = speechRate;
    }
    speechRateRef.current = speechRate;
    localStorage.setItem("voice_speech_rate", String(speechRate));
  }, [speechRate]);

  // Keyboard accessibility: Interruption on Space or Escape key press while agent speaks
  useEffect(() => {
    const handleKeyDown = (e) => {
      if (status !== "speaking") return;
      const activeEl = document.activeElement;
      if (activeEl && (activeEl.tagName === "TEXTAREA" || activeEl.tagName === "INPUT")) return;
      if (e.key === "Escape" || e.key === " ") {
        e.preventDefault();
        interruptPlayback();
      }
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [status, interruptPlayback]);

  /**
   * Barge-in VAD Loop: Analyzes microphone audio level during TTS playback ('speaking' status).
   * If input volume stays above a defined threshold (> 30) for 300ms continuous duration, 
   * automatically interrupts TTS playback and starts listening for user input.
   */
  useEffect(() => {
    if (status !== "speaking" || !autoInterrupt) return;

    const analyser = analyserRef.current;
    if (!analyser) return;

    const bufferLength = analyser.frequencyBinCount;
    const dataArray = new Uint8Array(bufferLength);

    const checkVolume = () => {
      if (statusRef.current !== "speaking" || !autoInterruptRef.current) return;

      analyser.getByteFrequencyData(dataArray);
      let sum = 0;
      for (let i = 0; i < bufferLength; i++) sum += dataArray[i];
      const avg = sum / bufferLength;

      // Speech detection volume threshold check
      if (avg > 30) {
        if (!aboveThresholdStartRef.current) {
          aboveThresholdStartRef.current = Date.now();
        } else if (Date.now() - aboveThresholdStartRef.current >= 300) {
          // Continuous voice activity detected for 300ms -> Trigger barge-in interrupt
          aboveThresholdStartRef.current = null;
          interruptPlayback();
          startListening();
          return;
        }
      } else {
        aboveThresholdStartRef.current = null;
      }

      bargeInRafRef.current = requestAnimationFrame(checkVolume);
    };

    bargeInRafRef.current = requestAnimationFrame(checkVolume);

    return () => {
      if (bargeInRafRef.current) {
        cancelAnimationFrame(bargeInRafRef.current);
        bargeInRafRef.current = null;
      }
      aboveThresholdStartRef.current = null;
    };
  }, [status, autoInterrupt, interruptPlayback, startListening]);

  // ---------------------------------------------------------------------------
  // INTERACTION HANDLERS
  // ---------------------------------------------------------------------------

  const handleMuteToggle = () => {
    const nextMuted = !muted;
    setMuted(nextMuted);
    if (nextMuted && audioRef.current) {
      audioRef.current.pause();
      audioRef.current.src = "";
      audioRef.current = null;
      setStatus("idle");
    }
  };

  const handleClose = () => {
    setSpeechError(null);
    cleanup();
    onClose();
  };

  const handleRetry = () => {
    setTranscript("");
    setAgentResponse("");
    setSpeechError(null);
    currentTranscriptRef.current = "";
    isSubmittingRef.current = false;
    startListening();
  };

  const handleFallbackSubmit = async () => {
    const text = transcript.trim();
    if (!text) return;
    isSubmittingRef.current = true;
    await submitVoiceQuery(text);
  };

  /**
   * Helper to resolve user-facing status label UI text.
   */
  const getStatusLabel = () => {
    switch (status) {
      case "recording":
        return "Listening...";
      case "processing":
        return "Thinking...";
      case "speaking":
        return (
          <>
            <span>Speaking...</span>
            <span className="mt-1 block text-xs text-gray-500">Tap to stop</span>
          </>
        );
      default:
        return "Tap to speak";
    }
  };

  // ---------------------------------------------------------------------------
  // RENDER UI
  // ---------------------------------------------------------------------------
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm animate-fade-in">
      <div className="relative w-full max-w-lg mx-4 bg-[#1a1a1a] rounded-3xl border border-white/10 shadow-2xl overflow-hidden">
        
        {/* Close Modal Button */}
        <button
          onClick={handleClose}
          className="absolute top-4 right-4 z-10 p-2 rounded-full bg-white/5 hover:bg-white/10 text-gray-400 hover:text-gray-200 transition-colors"
          title="Close voice mode"
        >
          <svg
            className="w-5 h-5"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M6 18L18 6M6 6l12 12"
            />
          </svg>
        </button>

        {/* Audio Visualizer Canvas Container */}
        <div className="flex flex-col items-center justify-center pt-10 pb-4">
          <canvas
            ref={canvasRef}
            width={220}
            height={220}
            onClick={
              status === "speaking" || status === "processing"
                ? interruptPlayback
                : undefined
            }
            className={`rounded-full transition-all ${
              status === "speaking" || status === "processing"
                ? "cursor-pointer hover:ring-2 hover:ring-emerald-400/50 hover:ring-offset-2 hover:ring-offset-[#1a1a1a] active:scale-95"
                : ""
            }`}
          />
        </div>

        {/* Status Text Indicator */}
        <div className="text-center mb-3 px-6">
          <div className="text-sm font-medium text-gray-300 uppercase tracking-widest">
            {getStatusLabel()}
          </div>
        </div>

        {/* User Speech Transcript / Manual Fallback Input Area */}
        <div className="px-8 mb-5 min-h-[56px]">
          {speechError ? (
            <div className="text-center">
              <p className="text-xs text-gray-500 mb-2">
                {speechError.includes(" microphone") || speechError.includes("Microphone")
                  ? "Microphone input isn't available right now. Type your question instead:"
                  : "Speech service is unreachable. Type your question instead:"}
              </p>
              <textarea
                value={transcript}
                onChange={(e) => setTranscript(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === "Enter" && !e.shiftKey) {
                    e.preventDefault();
                    handleFallbackSubmit();
                  }
                }}
                placeholder="Type your question..."
                className="w-full bg-white/5 border border-white/10 rounded-xl px-3 py-2 text-sm text-gray-200 placeholder-gray-600 outline-none focus:border-white/20 resize-none"
                rows={2}
              />
            </div>
          ) : (
            <p className="text-center text-gray-400 text-sm leading-relaxed">
              {transcript ||
                (status === "idle" ? "Say something..." : "")}
            </p>
          )}
        </div>

        {/* Assistant Response Card */}
        {agentResponse && (
          <div className="px-8 mb-6">
            <div className="bg-white/5 rounded-2xl border border-white/10 p-4">
              <p className="text-[11px] text-gray-500 mb-1.5 uppercase tracking-wider font-medium">
                Response
              </p>
              <p className="text-sm text-gray-200 leading-relaxed">
                {agentResponse}
              </p>
            </div>
          </div>
        )}

        {/* Voice Assistant Controls Toolbar */}
        <div className="flex items-center justify-center gap-3 pb-8">
          
          {/* Mute/Unmute TTS Toggle */}
          <button
            onClick={handleMuteToggle}
            className={`flex items-center gap-2 px-4 py-2.5 rounded-xl text-sm transition-all ${
              muted
                ? "bg-red-500/20 text-red-300 border border-red-500/30"
                : "bg-white/5 text-gray-400 border border-white/10 hover:bg-white/10"
            }`}
          >
            {muted ? (
              <svg
                className="w-4 h-4"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M5.586 15H4a1 1 0 01-1-1v-4a1 1 0 011-1h1.586l4.707-4.707C10.923 3.663 12 4.109 12 5v14c0 .891-1.077 1.337-1.707.707L5.586 15z"
                />
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M17 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2"
                />
              </svg>
            ) : (
              <svg
                className="w-4 h-4"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M15.536 8.464a5 5 0 010 7.072m2.828-9.9a9 9 0 010 12.728M5.586 15H4a1 1 0 01-1-1v-4a1 1 0 011-1h1.586l4.707-4.707C10.923 3.663 12 4.109 12 5v14c0 .891-1.077 1.337-1.707.707L5.586 15z"
                />
              </svg>
            )}
            {muted ? "Unmute TTS" : "Mute TTS"}
          </button>

          {/* Speech Rate Modifier Button */}
          <button
            onClick={() => {
              const rates = [0.75, 1, 1.25, 1.5];
              const idx = rates.indexOf(speechRate);
              setSpeechRate(rates[(idx + 1) % rates.length]);
            }}
            className="px-3 py-1.5 rounded-xl bg-white/5 text-gray-300 border border-white/10 hover:bg-white/10 text-xs transition-all"
            title="Playback speed (click to cycle)"
          >
            {speechRate}x
          </button>

          {/* Auto-Interrupt / Barge-in Feature Toggle */}
          <button
            onClick={() => setAutoInterrupt(!autoInterrupt)}
            className={`px-3 py-1.5 rounded-xl text-xs transition-all flex items-center gap-1.5 ${
              autoInterrupt
                ? "bg-emerald-500/20 text-emerald-300 border border-emerald-500/30"
                : "bg-white/5 text-gray-400 border border-white/10 hover:bg-white/10"
            }`}
            title={
              autoInterrupt
                ? "Auto-interrupt: ON (speak over assistant)"
                : "Auto-interrupt: OFF"
            }
          >
            <span
              className={`w-1.5 h-1.5 rounded-full ${
                autoInterrupt ? "bg-emerald-400" : "bg-gray-600"
              }`}
            />
            Auto-interrupt
          </button>

          {/* Try Again (Restart Recording) Button */}
          {status === "idle" && (
            <button
              onClick={handleRetry}
              className="flex items-center gap-2 px-4 py-2.5 rounded-xl bg-emerald-500/20 text-emerald-300 border border-emerald-500/30 hover:bg-emerald-500/30 text-sm transition-all"
            >
              <svg
                className="w-4 h-4"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z"
                />
              </svg>
              Try Again
            </button>
          )}

          {/* Send Button for Fallback Manual Text Entry */}
          {speechError && transcript.trim() && (
            <button
              onClick={handleFallbackSubmit}
              className="flex items-center gap-2 px-4 py-2.5 rounded-xl bg-emerald-500/20 text-emerald-300 border border-emerald-500/30 hover:bg-emerald-500/30 text-sm transition-all"
            >
              <svg
                className="w-4 h-4"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M6 12L3.269 3.126A59.768 59.768 0 0121.485 12 59.77 59.77 0 013.27 20.876L5.999 12z"
                />
              </svg>
              Send
            </button>
          )}
        </div>
      </div>
    </div>
  );
}