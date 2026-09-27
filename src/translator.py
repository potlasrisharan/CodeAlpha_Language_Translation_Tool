"""High-Performance Translation Service utilizing Google Chrome Neural API & MyMemory Fallback."""

import time
import urllib.parse
from dataclasses import dataclass
from typing import Optional, Tuple
import requests
from deep_translator import MyMemoryTranslator
from langdetect import detect
from src.constants import SUPPORTED_LANGUAGES, MYMEMORY_LANG_MAP


@dataclass
class TranslationResult:
    source_text: str
    translated_text: str
    source_lang_name: str
    source_lang_code: str
    target_lang_name: str
    target_lang_code: str
    char_count: int
    word_count: int
    latency_ms: float
    provider_used: str = "Google Chrome Neural"
    error: Optional[str] = None


class TranslationService:
    def __init__(self):
        self._name_to_code = SUPPORTED_LANGUAGES
        self._code_to_name = {v: k for k, v in SUPPORTED_LANGUAGES.items()}
        self._mymemory_map = MYMEMORY_LANG_MAP
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            "Accept": "*/*",
        })

    def detect_language(self, text: str) -> Tuple[str, str]:
        """Detect language code using offline langdetect model."""
        cleaned = text.strip()
        if not cleaned:
            return "auto", "Auto Detect"
        try:
            detected_code = detect(cleaned[:300])
            name = self._code_to_name.get(detected_code, "English")
            return detected_code, name
        except Exception:
            return "en", "English"

    def _translate_google_chrome(self, text: str, src_code: str, tgt_code: str) -> Tuple[str, str]:
        """Call Google Neural translation API via Chrome client without API key restrictions."""
        encoded_query = urllib.parse.quote(text)
        url = f"https://clients5.google.com/translate_a/t?client=dict-chrome-ex&sl={src_code}&tl={tgt_code}&q={encoded_query}"
        
        response = self.session.get(url, timeout=6)
        if response.status_code != 200:
            raise RuntimeError(f"Google Chrome API returned HTTP {response.status_code}")

        data = response.json()
        detected_src = src_code

        if isinstance(data, list):
            if isinstance(data[0], list):
                translated_text = str(data[0][0])
                if len(data[0]) > 1:
                    detected_src = str(data[0][1])
            else:
                translated_text = str(data[0])
            return translated_text, detected_src
        return str(data), detected_src

    def _translate_mymemory(self, text: str, src_name: str, tgt_name: str) -> str:
        """Call MyMemory API fallback."""
        my_src = self._mymemory_map.get(src_name, src_name.lower())
        my_tgt = self._mymemory_map.get(tgt_name, tgt_name.lower())
        translator = MyMemoryTranslator(source=my_src, target=my_tgt)
        return translator.translate(text)

    def translate(
        self,
        text: str,
        source_lang_name: str = "Auto Detect",
        target_lang_name: str = "Spanish",
    ) -> TranslationResult:
        """Execute translation with primary Google Chrome Neural engine and MyMemory fallback."""
        start_time = time.perf_counter()
        cleaned_text = text.strip()

        if not cleaned_text:
            return TranslationResult(
                source_text="",
                translated_text="",
                source_lang_name=source_lang_name,
                source_lang_code="auto",
                target_lang_name=target_lang_name,
                target_lang_code=self._name_to_code.get(target_lang_name, "es"),
                char_count=0,
                word_count=0,
                latency_ms=0.0,
            )

        src_code = self._name_to_code.get(source_lang_name, "auto")
        tgt_code = self._name_to_code.get(target_lang_name, "es")

        # Engine 1: Google Chrome Neural API
        try:
            translated, detected_code = self._translate_google_chrome(cleaned_text, src_code, tgt_code)
            detected_name = self._code_to_name.get(detected_code, source_lang_name)
            elapsed = (time.perf_counter() - start_time) * 1000

            return TranslationResult(
                source_text=cleaned_text,
                translated_text=translated,
                source_lang_name=detected_name,
                source_lang_code=detected_code,
                target_lang_name=target_lang_name,
                target_lang_code=tgt_code,
                char_count=len(cleaned_text),
                word_count=len(cleaned_text.split()),
                latency_ms=round(elapsed, 1),
                provider_used="Google Neural Engine",
            )
        except Exception:
            # Engine 2: Fallback to MyMemory
            try:
                det_code, detected_name = self.detect_language(cleaned_text)
                actual_src_name = detected_name if source_lang_name == "Auto Detect" else source_lang_name
                translated = self._translate_mymemory(cleaned_text, actual_src_name, target_lang_name)
                elapsed = (time.perf_counter() - start_time) * 1000

                return TranslationResult(
                    source_text=cleaned_text,
                    translated_text=translated,
                    source_lang_name=actual_src_name,
                    source_lang_code=det_code,
                    target_lang_name=target_lang_name,
                    target_lang_code=tgt_code,
                    char_count=len(cleaned_text),
                    word_count=len(cleaned_text.split()),
                    latency_ms=round(elapsed, 1),
                    provider_used="MyMemory Engine",
                )
            except Exception as final_err:
                elapsed = (time.perf_counter() - start_time) * 1000
                return TranslationResult(
                    source_text=cleaned_text,
                    translated_text="",
                    source_lang_name=source_lang_name,
                    source_lang_code=src_code,
                    target_lang_name=target_lang_name,
                    target_lang_code=tgt_code,
                    char_count=len(cleaned_text),
                    word_count=len(cleaned_text.split()),
                    latency_ms=round(elapsed, 1),
                    error=f"Translation failed: {str(final_err)}",
                )
