"""Text-to-Speech audio synthesizer using gTTS with in-memory streaming."""

import io
from typing import Optional
from gtts import gTTS


class TextToSpeechService:
    @staticmethod
    def synthesize_to_bytes(text: str, lang_code: str = "en") -> Optional[bytes]:
        """Convert text into in-memory MP3 audio bytes."""
        cleaned = text.strip()
        if not cleaned:
            return None

        # Clean lang_code (e.g. 'zh-CN' -> 'zh-CN' or 'zh')
        # gTTS supports base 2-letter codes or specific locales
        target_code = lang_code.split("-")[0] if "-" in lang_code and lang_code != "zh-CN" else lang_code
        if target_code == "auto":
            target_code = "en"

        try:
            tts = gTTS(text=cleaned[:500], lang=target_code, slow=False)
            fp = io.BytesIO()
            tts.write_to_fp(fp)
            fp.seek(0)
            return fp.read()
        except Exception:
            # Fallback to English if language code is not supported by gTTS
            try:
                tts = gTTS(text=cleaned[:500], lang="en", slow=False)
                fp = io.BytesIO()
                tts.write_to_fp(fp)
                fp.seek(0)
                return fp.read()
            except Exception:
                return None
