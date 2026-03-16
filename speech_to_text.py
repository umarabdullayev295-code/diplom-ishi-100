"""
speech_to_text.py
-----------------
Nutqni matnga o'tkazish — unified interface.

Ustuvorlik tartibi:
  1. ElevenLabs Scribe v1  (API kalit mavjud bo'lsa — eng aniq va tez)
  2. faster-whisper        (offline, local model)

O'zbek tili uchun optimallashtirilgan.
"""

import os
from typing import List, Dict, Optional


class SpeechToText:
    """
    Unified Speech-to-Text engine.
    API mavjudligiga qarab eng yaxshi dvigatelni avtomatik tanlaydi.
    """

    def __init__(
        self,
        whisper_model_size: str = "medium",
        language: str = "uz",
        use_api: bool = True,
        elevenlabs_api_key: Optional[str] = None,
    ):
        """
        Args:
            whisper_model_size : 'tiny'|'base'|'small'|'medium'|'large-v2'|'large-v3'
            language           : Til kodi  ('uz' — o'zbek)
            use_api            : True bo'lsa API ishlatishga harakat qiladi
            elevenlabs_api_key : ElevenLabs API kaliti
        """
        self.language = language
        self.whisper_model_size = whisper_model_size
        self._whisper_model = None
        self._api_client = None
        self.active_engine: str = ""

        if use_api:
            self._api_client, self.active_engine = self._pick_api_client(
                elevenlabs_api_key
            )

        if not self.active_engine:
            self.active_engine = f"faster-whisper ({whisper_model_size})"

    # ------------------------------------------------------------------ #
    def _pick_api_client(
        self,
        el_key: Optional[str],
    ):
        """
        Mavjud va ishlaydigan API mijozini tanlaydi.
        """
        from ai_labs_api import ElevenLabsClient, get_best_api_client

        # 1. O'zbek AI (eng yuqori ustuvorlik)
        el = ElevenLabsClient(api_key=el_key) if el_key else ElevenLabsClient()
        if el.is_available():
            return el, "O'zbek AI Model (Pro)"

        # 2. Muhit o'zgaruvchilaridan avtomatik tanlash
        client, name = get_best_api_client()
        if client:
            return client, name

        return None, ""

    # ------------------------------------------------------------------ #
    def transcribe(self, audio_path: str) -> List[Dict]:
        """
        Audio faylni matnga o'tkazadi.

        Returns:
            [{"start": 0.0, "end": 3.4, "text": "Assalomu alaykum"}, ...]
        """
        if not os.path.exists(audio_path):
            print(f"[STT] Fayl topilmadi: {audio_path}")
            return []

        # API orqali
        client = self._api_client
        if client is not None and client.is_available():
            try:
                print(f"[STT] {self.active_engine} orqali transkripsiya...")
                results = client.transcribe_audio(audio_path, language=self.language)
                if results:
                    print(f"[STT] {len(results)} segment topildi ({self.active_engine}).")
                    return results
                print("[STT] API natija qaytarmadi. Whisperga o'tilmoqda...")
            except Exception as e:
                print(f"[STT] API xatosi: {e}. Whisperga o'tilmoqda...")

        # Whisper fallback
        return self._transcribe_whisper(audio_path)

    # ------------------------------------------------------------------ #
    def _load_whisper(self):
        """Whisper modelini lazy loading bilan yuklaydi."""
        if self._whisper_model is None:
            from faster_whisper import WhisperModel
            device = "cpu"
            compute_type = "int8"
            try:
                import torch
                if torch.cuda.is_available():
                    device = "cuda"
                    compute_type = "float16"
            except ImportError:
                pass
            print(f"[STT] Whisper yuklanmoqda: {self.whisper_model_size} ({device})...")
            self._whisper_model = WhisperModel(
                self.whisper_model_size, device=device, compute_type=compute_type
            )
        return self._whisper_model

    def _transcribe_whisper(self, audio_path: str) -> List[Dict]:
        """faster-whisper orqali lokal transkripsiya."""
        try:
            model = self._load_whisper()
            print(f"[STT] Whisper transkripsiya (til: {self.language})...")
            segments, info = model.transcribe(
                audio_path,
                language=self.language,
                beam_size=5,
                vad_filter=True,
                vad_parameters={"min_silence_duration_ms": 500, "speech_pad_ms": 400},
                condition_on_previous_text=True,
                word_timestamps=True,  # So'zma-so'z vaqtlar uchun
            )
            lang = getattr(info, "language", self.language)
            prob = getattr(info, "language_probability", 0)
            print(f"[STT] Til aniqlandi: {lang} ({prob:.0%})")

            result = []
            for seg in segments:
                # Agar word_timestamps=True bo'lsa, har bir segmentda .words bo'ladi
                if hasattr(seg, "words") and seg.words:
                    for w in seg.words:
                        w_text = w.word.strip()
                        if w_text:
                            result.append({
                                "start": round(w.start, 2),
                                "end": round(w.end, 2),
                                "text": w_text,
                            })
                else:
                    # Fallback — butun segment
                    text = seg.text.strip()
                    if text:
                        result.append({
                            "start": round(seg.start, 2),
                            "end": round(seg.end, 2),
                            "text": text,
                        })
            print(f"[STT] {len(result)} so'z/segment topildi (Whisper).")
            return result
        except Exception as e:
            print(f"[STT] Whisper xatosi: {e}")
            return []

    # ------------------------------------------------------------------ #
    def get_engine_name(self) -> str:
        return self.active_engine or "Noma'lum"

    def get_full_text(self, segments: List[Dict]) -> str:
        return " ".join(s["text"] for s in segments if s.get("text"))
