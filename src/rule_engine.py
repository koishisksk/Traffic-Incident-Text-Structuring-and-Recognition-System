from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class RuleEngine:
    """Keyword rule matcher backed by a JSON traffic-domain dictionary."""

    def __init__(self, rules_path: str | Path | None = None) -> None:
        project_root = Path(__file__).resolve().parents[1]
        self.rules_path = Path(rules_path) if rules_path else project_root / "rules" / "event_keywords.json"
        self.rules = self._load_rules(self.rules_path)

    def match_event_type(self, text: str) -> dict[str, Any]:
        best: dict[str, Any] | None = None
        for event_type, rule in self.rules["event_types"].items():
            score = self._score_keywords(text, rule.get("keywords", []))
            if score <= 0:
                continue
            candidate = {
                "event_type": event_type,
                "event_type_code": rule.get("code"),
                "event_subtype": self._match_subtype(text, rule.get("subtypes", {})),
                "score": score + float(rule.get("priority", 0)),
            }
            if best is None or candidate["score"] > best["score"]:
                best = candidate

        if best is None:
            other_rule = self.rules["event_types"]["其他事件"]
            return {
                "event_type": "其他事件",
                "event_type_code": other_rule["code"],
                "event_subtype": None,
                "score": 0,
            }
        return best

    def keywords(self, group: str) -> list[str]:
        return list(self.rules.get("dictionaries", {}).get(group, []))

    def _match_subtype(self, text: str, subtype_rules: dict[str, list[str]]) -> str | None:
        best_subtype = None
        best_score = 0
        for subtype, keywords in subtype_rules.items():
            score = self._score_keywords(text, keywords)
            if score > best_score:
                best_subtype = subtype
                best_score = score
        return best_subtype

    @staticmethod
    def _score_keywords(text: str, keywords: list[str]) -> int:
        return sum(1 for keyword in keywords if keyword and keyword in text)

    @staticmethod
    def _load_rules(path: Path) -> dict[str, Any]:
        with path.open("r", encoding="utf-8") as file:
            return json.load(file)
