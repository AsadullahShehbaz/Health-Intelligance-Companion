# Spec: Make Voice UI interruptible (barge-in + playback speed)

## Problem
`VoiceAssistantModal.jsx` currently plays TTS audio to completion with no way to
stop it mid-sentence. The only control that touches playback is "Mute TTS", which
kills the audio entirely and can't be un-done mid-response, and there's no way to
just cut the assistant off and immediately talk again — a real voice assistant
(Siri/Alexa/ChatGPT voice) lets you tap or speak over it and it stops instantly.

Two things are being asked for:
1. **Interrupt / stop-talking** — tap the orb (or a button) while `status === "speaking"`
   and playback stops immediately, mic re-opens for the next question.
2. **Playback speed control** — a way to slow down or speed up how fast the
   assistant talks.

---

## Step 1 — Orb tap-to-interrupt (primary fix)
- Make the `<canvas>` orb clickable whenever `status === "speaking"` or
  `status === "processing"`.
- Add an `interruptPlayback()` function:
  ```js
  const interruptPlayback = useCallback(() => {
    if (audioRef.current) {
      audioRef.current.pause();
      audioRef.current.src = "";
      audioRef.current = null;
    }
    setStatus("idle");
  }, []);
  ```
- Wire it to the canvas `onClick` (and give the orb a `cursor-pointer` + subtle
  hover ring only while speaking, so it's visually obvious it's tappable).
- After interrupting, don't auto-restart listening — let the user tap the orb
  again like normal (`status: "idle"` already shows "Tap to speak"). This matches
  existing `idle` behavior and needs zero new state.

## Step 2 — Keyboard/space-bar interrupt (accessibility + desktop parity)
- While the modal is open and `status === "speaking"`, listen for `Escape` or
  `Space` keydown and call `interruptPlayback()`. Skip this if focus is inside
  the fallback `<textarea>` (check `document.activeElement`).

## Step 3 — True barge-in: speak-over-it (stretch, do after 1–2 work)
- While `status === "speaking"`, keep `streamRef.current`'s mic stream alive
  (currently only opened during `recording`) and run a lightweight volume check
  via the existing `analyserRef` pattern already used in `drawVisualizer`.
- If mic input volume crosses a threshold for ~300ms while TTS is playing,
  treat it as the user interrupting: call `interruptPlayback()` then
  immediately call `startListening()`.
- Guard against false positives from the TTS audio itself leaking into the mic
  (feedback) — only enable this on devices with headphones, or gate behind a
  toggle in the UI ("Auto-interrupt" switch) so users can opt in rather than
  fighting false triggers on laptop speakers.

## Step 4 — Playback speed control
- Add a `speechRate` state, default `1`, with options `[0.75, 1, 1.25, 1.5]`.
- In `playTTS`, after creating `audio`, set `audio.playbackRate = speechRate`.
- Add a small speed control in the UI — a pill/dropdown near "Mute TTS"
  (e.g. "1x" button that cycles through the options on click, or a short menu).
- If `speechRate` changes *while* audio is currently playing, apply it live:
  ```js
  useEffect(() => {
    if (audioRef.current) audioRef.current.playbackRate = speechRate;
  }, [speechRate]);
  ```
- Persist the last-used rate in `localStorage` (e.g. `voice_speech_rate`) so it
  sticks across sessions — small nice-to-have, skip if out of scope.

## Step 5 — Visual affordance
- While `status === "speaking"`, show a small "Tap to stop" label under the
  status text (reuse the existing `getStatusLabel()` area) instead of just
  "Speaking..." — make the interrupt option discoverable, not hidden.
- Update `drawVisualizer`'s `speaking` branch with a subtle pointer-hover state
  (e.g. slightly brighter ripple color on `:hover`) if feasible with canvas;
  otherwise skip — the text label is enough.

## Step 6 — Test
- Manual: ask a question, tap orb mid-response → audio stops immediately,
  status returns to idle, orb pulses idle animation.
- Manual: change speed to 1.5x mid-playback → rate changes without restarting
  the clip from the beginning.
- Manual: press Escape/Space during speaking → same as orb-tap interrupt.
- Manual (if Step 3 implemented): speak over the assistant with "Auto-interrupt"
  on → playback stops and mic starts listening within ~300ms.
- Regression: Mute TTS button still works exactly as before; existing
  fallback-textarea flow untouched.

## Non-goals
- No changes to STT/backend — this is purely playback-control UX.
- No streaming/partial TTS (assistant still speaks a full pre-generated clip;
  interrupting just stops that clip early, it doesn't make the response
  generate faster).