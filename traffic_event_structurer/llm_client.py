"""Reserved LLM enhancement interface.

The prototype works without any external API. A future implementation can call
an LLM here to review low-confidence fields or normalize complex long texts.
"""

from __future__ import annotations

from typing import Any


class LLMReviewClient:
    """Placeholder for LLM-based review and correction."""

    def __init__(self, enabled: bool = False) -> None:
        self.enabled = enabled

    def review(self, source_text: str, rule_result: dict[str, Any]) -> dict[str, Any]:
        """Return an enhanced result.

        Current behavior: keep rule output unchanged and mark whether LLM review
        would be useful. Replace this method when connecting to a real API.
        """
        if not self.enabled:
            return rule_result

        reviewed = dict(rule_result)
        reviewed["extract_method"] = "rule+llm_review_placeholder"
        reviewed["need_llm_review"] = False
        return reviewed
