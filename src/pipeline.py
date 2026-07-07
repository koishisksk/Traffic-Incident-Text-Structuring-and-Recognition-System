from __future__ import annotations

from collections import OrderedDict
from typing import Any

from .extractor import TrafficEventExtractor
from .schema import normalize_output


class TrafficEventPipeline:
    """Pipeline entry point for rule-based traffic event structuring."""

    def __init__(self, extractor: TrafficEventExtractor | None = None) -> None:
        self.extractor = extractor or TrafficEventExtractor()

    def parse(self, text: str) -> OrderedDict[str, Any]:
        if not text or not text.strip():
            raise ValueError("输入文本不能为空")
        extracted = self.extractor.extract(text)
        return normalize_output(extracted)
