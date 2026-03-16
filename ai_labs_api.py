"""
ai_labs_api.py
--------------
STT API integratsiyasi:
  1. ElevenLabs Scribe v1 (ustuvor — o'zbek tilini mukammal taniydi)
"""

import os
import tempfile
from typing import List, Dict, Optional
from elevenlabs.client import ElevenLabs
import httpx


# ─── ElevenLabs ───
ELEVENLABS_API_KEY = os.environ.get("ELEVENLABS_API_KEY", "sk_4334f8d4a5a00b6cc18e08b4d68d726297da5b224871ac79")
ELEVENLABS_STT_URL = "https://api.elevenlabs.io/v1/speech-to-text"


class ElevenLabsClient:
    """
    ElevenLabs Scribe v2 — eng aniq ko'p tilli STT modeli.
    O'zbek tilini (uzb) mukammal taniydi, gap yoki so'z belgilari bilan.
    Sayt: https://elevenlabs.io/speech-to-text
    """

    def __init__(self, api_key: str = None):
        self.api_key = api_key or ELEVENLABS_API_KEY
        self.available = bool(self.api_key)

    def is_available(self) -> bool:
        return self.available

    def transcribe_audio(self, audio_path: str, language: str = "uz") -> List[Dict]:
        """
        ElevenLabs Scribe v1 orqali audio faylni matnga o'tkazadi.

        Args:
            audio_path: Audio fayl yo'li
            language: Til kodi (standart: 'uz' — o'zbek)

        Returns:
            Segmentlar ro'yxati: [{"start": float, "end": float, "text": str}]
        """
        if not self.available:
            raise ValueError("ElevenLabs API kaliti mavjud emas.")

        headers = {"xi-api-key": self.api_key}

        # Scribe v2 requires 3-letter codes (ISO 639-3)
        lang_map = {
            "uz": "uzb",
            "ru": "rus",
            "en": "eng",
            "tr": "tur"
        }
        iso3_lang = lang_map.get(language, "uzb")

        try:
            client = ElevenLabs(api_key=self.api_key)
            
            with open(audio_path, "rb") as audio_file:
                # Official Python SDK method for STT (Scribe v2)
                response = client.speech_to_text.convert(
                    file=audio_file,
                    model_id="scribe_v2",
                    language_code=iso3_lang,
                    tag_audio_events=False,
                    diarize=False
                )
                
                # SDK qaytaradigan model obyektini .dict() yoki .model_dump() orqali dict ga aynatiramiz (agar pydantic bo'lsa)
                result = response.model_dump() if hasattr(response, 'model_dump') else (
                    response.dict() if hasattr(response, 'dict') else response
                )
                
                return self._parse_response(result)

        except httpx.HTTPStatusError as e:
            print(f"[ElevenLabs] HTTP xato {e.response.status_code}: {e.response.text[:200]}")
            return []
        except Exception as e:
            print(f"[ElevenLabs] Umumiy xato: {e}")
            return []

    def _parse_response(self, result: dict) -> List[Dict]:
        """
        ElevenLabs API javobini standart segment formatiga o'tkazadi.
        So'z darajasidagi vaqtlardan gap segmentlari yaratadi.
        """
        segments = []

        # ElevenLabs words-based format
        words = result.get("words", [])
        if words:
            segments = self._words_to_segments(words)
        # Sodda text format (fallback)
        elif "text" in result:
            segments = [{
                "start": 0.0,
                "end": 0.0,
                "text": result["text"].strip(),
            }]

        return [s for s in segments if s.get("text", "").strip()]

    def _words_to_segments(self, words: list) -> List[Dict]:
        """
        So'zlarni to'g'ridan-to'g'ri alohida segmentlar sifatida qaytaradi.
        Bu bilan subtitrda har bir so'z aniq o'z vaqtida yonadi.
        """
        if not words:
            return []

        segments = []
        for w in words:
            # Ba'zi modellarda "type" = "word" yoki shunchaki text mavjud
            if w.get("type", "word") != "word":
                continue
            
            word_text = w.get("text", w.get("word", "")).strip()
            if not word_text:
                continue

            # Har bir so'zni o'zining aniq boshlanish va tugash vaqtida alohida frame qilamiz
            segments.append({
                "start": float(w.get("start", 0)),
                "end": float(w.get("end", 0)),
                "text": word_text
            })

        return segments

    def test_connection(self) -> bool:
        """API ulanishini tekshiradi."""
        if not self.available:
            return False
        try:
            client = ElevenLabs(api_key=self.api_key)
            # user ma'lumotlarini olish orqali token haqiqiyligini tekshirish
            client.user.get()
            return True
        except Exception:
            return False


def get_best_api_client():
    """
    Mavjud eng yaxshi API mijozini qaytaradi.
    Faqat ElevenLabs!
    """
    elevenlabs = ElevenLabsClient()
    if elevenlabs.is_available():
        return elevenlabs, "ElevenLabs Scribe v2"

    return None, None
