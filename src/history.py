"""Session translation history manager with export capabilities."""

import json
from dataclasses import asdict
from datetime import datetime
from typing import List, Dict, Any
from src.translator import TranslationResult


class HistoryManager:
    def __init__(self):
        self.records: List[Dict[str, Any]] = []

    def add(self, result: TranslationResult) -> None:
        """Record a completed translation result."""
        if not result.source_text.strip() or not result.translated_text.strip():
            return

        record = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "source_lang": result.source_lang_name,
            "target_lang": result.target_lang_name,
            "source_text": result.source_text,
            "translated_text": result.translated_text,
            "char_count": result.char_count,
            "word_count": result.word_count,
            "latency_ms": result.latency_ms,
        }
        self.records.insert(0, record)  # Most recent first

        # Cap memory history to last 50 items
        if len(self.records) > 50:
            self.records.pop()

    def get_all(self) -> List[Dict[str, Any]]:
        return self.records

    def clear(self) -> None:
        self.records.clear()

    def export_json(self) -> str:
        return json.dumps(self.records, indent=2, ensure_ascii=False)
