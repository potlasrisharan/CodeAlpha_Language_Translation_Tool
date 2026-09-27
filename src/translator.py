"""Resilient Multi-Provider Translation Service with offline auto-detection."""

import time
from dataclasses import dataclass
from typing import Optional, Tuple
from deep_translator import MyMemoryTranslator, GoogleTranslator
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
    provider_used: str = "MyMemory"
    error: Optional[str] = None


class TranslationService:
    def __init__(self):
        self._name_to_code = SUPPORTED_LANGUAGES
        self._code_to_name = {v: k for k, v in SUPPORTED_LANGUAGES.items()}
        self._mymemory_map = MYMEMORY_LANG_MAP

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

    def _resolve_mymemory_name(self, lang_name: str) -> str:
        """Map standard display name to MyMemory supported identifier."""
        if lang_name in self._mymemory_map:
            return self._mymemory_map[lang_name]
        return lang_name.lower()

    def translate(
        self,
        text: str,
        source_lang_name: str = "Auto Detect",
        target_lang_name: str = "Spanish",
    ) -> TranslationResult:
        """Translate text with multi-provider fallback and accurate timing."""
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

        detected_name = source_lang_name
        src_code = self._name_to_code.get(source_lang_name, "auto")
        tgt_code = self._name_to_code.get(target_lang_name, "es")

        # Auto detection if requested
        if source_lang_name == "Auto Detect":
            det_code, detected_name = self.detect_language(cleaned_text)
            src_code = det_code

        # If source and target are the same language
        if detected_name.lower() == target_lang_name.lower():
            elapsed = (time.perf_counter() - start_time) * 1000
            return TranslationResult(
                source_text=cleaned_text,
                translated_text=cleaned_text,
                source_lang_name=detected_name,
                source_lang_code=src_code,
                target_lang_name=target_lang_name,
                target_lang_code=tgt_code,
                char_count=len(cleaned_text),
                word_count=len(cleaned_text.split()),
                latency_ms=round(elapsed, 1),
                provider_used="PassThrough",
            )

        my_src = self._resolve_mymemory_name(detected_name)
        my_tgt = self._resolve_mymemory_name(target_lang_name)

        # Provider 1: MyMemoryTranslator (Free, high reliability)
        try:
            translator = MyMemoryTranslator(source=my_src, target=my_tgt)
            if len(cleaned_text) > 400:
                paragraphs = [p for p in cleaned_text.split("\n") if p.strip()]
                translated_paragraphs = [translator.translate(p) for p in paragraphs]
                translated_text = "\n".join(translated_paragraphs)
            else:
                translated_text = translator.translate(cleaned_text)

            elapsed = (time.perf_counter() - start_time) * 1000
            return TranslationResult(
                source_text=cleaned_text,
                translated_text=translated_text or "",
                source_lang_name=detected_name,
                source_lang_code=src_code,
                target_lang_name=target_lang_name,
                target_lang_code=tgt_code,
                char_count=len(cleaned_text),
                word_count=len(cleaned_text.split()),
                latency_ms=round(elapsed, 1),
                provider_used="MyMemory",
            )
        except Exception as my_exc:
            # Provider 2: Fallback to GoogleTranslator
            try:
                g_translator = GoogleTranslator(
                    source=src_code if src_code != "auto" else "auto",
                    target=tgt_code,
                )
                translated_text = g_translator.translate(cleaned_text)
                elapsed = (time.perf_counter() - start_time) * 1000
                return TranslationResult(
                    source_text=cleaned_text,
                    translated_text=translated_text or "",
                    source_lang_name=detected_name,
                    source_lang_code=src_code,
                    target_lang_name=target_lang_name,
                    target_lang_code=tgt_code,
                    char_count=len(cleaned_text),
                    word_count=len(cleaned_text.split()),
                    latency_ms=round(elapsed, 1),
                    provider_used="Google",
                )
            except Exception as g_exc:
                elapsed = (time.perf_counter() - start_time) * 1000
                return TranslationResult(
                    source_text=cleaned_text,
                    translated_text="",
                    source_lang_name=detected_name,
                    source_lang_code=src_code,
                    target_lang_name=target_lang_name,
                    target_lang_code=tgt_code,
                    char_count=len(cleaned_text),
                    word_count=len(cleaned_text.split()),
                    latency_ms=round(elapsed, 1),
                    error=f"Translation error: {str(my_exc)} / {str(g_exc)}",
                )
