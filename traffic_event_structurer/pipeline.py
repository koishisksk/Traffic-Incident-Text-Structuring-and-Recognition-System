"""Pipeline that combines rule extraction and optional LLM review."""

from __future__ import annotations

from datetime import date
from typing import Any

from .llm_client import LLMReviewClient
from .rule_engine import RuleBasedExtractor


class TrafficEventPipeline:
    """Main entry point for traffic event text structuring."""

    def __init__(
        self,
        extractor: RuleBasedExtractor | None = None,
        llm_client: LLMReviewClient | None = None,
    ) -> None:
        self.extractor = extractor or RuleBasedExtractor()
        self.llm_client = llm_client or LLMReviewClient(enabled=False)

    def parse(self, text: str, reference_date: date | None = None) -> dict[str, Any]:
        """Parse one Chinese traffic event text into JSON-serializable dict."""
        if not text or not text.strip():
            raise ValueError("输入文本不能为空")

        rule_result = self.extractor.extract(text, reference_date=reference_date)
        return self.llm_client.review(text, rule_result)
