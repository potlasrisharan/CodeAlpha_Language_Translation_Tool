"""Translation service providing multi-language translation and text chunking."""

import time
from dataclasses import dataclass
from typing import Optional, Tuple
from deep_translator import GoogleTranslator, single_detection
from src.constants import SUPPORTED_LANGUAGES


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
    error: Optional[str] = None


class TranslationService:
    def __init__(self):
        self._lang_name_to_code = SUPPORTED_LANGUAGES
        self._lang_code_to_name = {v: k for k, v in SUPPORTED_LANGUAGES.items()}

    def detect_language(self, text: str) -> Tuple[str, str]:
        """Detect language code and return (code, human_readable_name)."""
        if not text.strip():
            return "auto", "Auto Detect"
        try:
            detected_code = single_detection(text[:250], api_key=None)
            name = self._lang_code_to_name.get(detected_code, detected_code.upper())
            return detected_code, name
        except Exception:
            return "en", "English"

    def translate(
        self,
        text: str,
        source_lang_name: str = "Auto Detect",
        target_lang_name: str = "Spanish",
    ) -> TranslationResult:
        """Translate text with timing and error resilience."""
        start_time = time.perf_counter()
        cleaned_text = text.strip()

        if not cleaned_text:
            return TranslationResult(
                source_text="",
                translated_text="",
                source_lang_name=source_lang_name,
                source_lang_code="auto",
                target_lang_name=target_lang_name,
                target_lang_code=self._lang_name_to_code.get(target_lang_name, "es"),
                char_count=0,
                word_count=0,
                latency_ms=0.0,
            )

        src_code = self._lang_name_to_code.get(source_lang_name, "auto")
        tgt_code = self._lang_name_to_code.get(target_lang_name, "es")

        # Fallback if source and target are the same
        if src_code != "auto" and src_code == tgt_code:
            elapsed = (time.perf_counter() - start_time) * 1000
            return TranslationResult(
                source_text=cleaned_text,
                translated_text=cleaned_text,
                source_lang_name=source_lang_name,
                source_lang_code=src_code,
                target_lang_name=target_lang_name,
                target_lang_code=tgt_code,
                char_count=len(cleaned_text),
                word_count=len(cleaned_text.split()),
                latency_ms=round(elapsed, 1),
            )

        try:
            translator = GoogleTranslator(source=src_code, target=tgt_code)
            
            # Handle large texts (>4500 chars) by paragraph chunking
            if len(cleaned_text) > 4000:
                paragraphs = cleaned_text.split("\n\n")
                translated_chunks = [translator.translate(p) for p in paragraphs if p.strip()]
                translated_text = "\n\n".join(translated_chunks)
            else:
                translated_text = translator.translate(cleaned_text)

            detected_src_name = source_lang_name
            if src_code == "auto":
                # Determine detected code
                _, detected_src_name = self.detect_language(cleaned_text)

            elapsed = (time.perf_counter() - start_time) * 1000
            return TranslationResult(
                source_text=cleaned_text,
                translated_text=translated_text or "",
                source_lang_name=detected_src_name,
                source_lang_code=src_code,
                target_lang_name=target_lang_name,
                target_lang_code=tgt_code,
                char_count=len(cleaned_text),
                word_count=len(cleaned_text.split()),
                latency_ms=round(elapsed, 1),
            )
        except Exception as exc:
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
                error=f"Translation failed: {str(exc)}",
            )
