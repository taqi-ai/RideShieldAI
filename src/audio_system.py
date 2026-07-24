import subprocess
import threading
import time

class VoiceSpeaker:
    """Thread-safe non-blocking Text-To-Speech engine using Windows PowerShell System.Speech synthesizer."""
    def __init__(self):
        self._lock = threading.Lock()
        self._last_speech_time = 0
        self._last_phrase = None
        self._cooldown = 4.0  # seconds between repeated alerts

    def speak(self, text, force=False):
        current_time = time.time()
        with self._lock:
            if not force and text == self._last_phrase and (current_time - self._last_speech_time) < self._cooldown:
                return
            self._last_speech_time = current_time
            self._last_phrase = text

        def _speak_thread():
            try:
                escaped_text = text.replace('"', '\\"')
                cmd = f'Add-Type -AssemblyName System.Speech; $synth = New-Object System.Speech.Synthesis.SpeechSynthesizer; $synth.Rate = 1; $synth.Speak("{escaped_text}")'
                subprocess.run(['powershell', '-NoProfile', '-ExecutionPolicy', 'Bypass', '-Command', cmd],
                               creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, 'CREATE_NO_WINDOW') else 0)
            except Exception as e:
                print(f"[Audio] Voice synthesis error: {e}")

        threading.Thread(target=_speak_thread, daemon=True).start()

# Global singleton
speaker = VoiceSpeaker()
