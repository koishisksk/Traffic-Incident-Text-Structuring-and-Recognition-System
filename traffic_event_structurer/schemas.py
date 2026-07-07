"""Output schema definitions for traffic event extraction."""

from __future__ import annotations

JSON_SCHEMA = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "title": "TrafficEvent",
    "type": "object",
    "required": ["source_text", "event_type"],
    "properties": {
        "source_text": {"type": "string", "description": "原始输入文本"},
        "event_time_text": {"type": ["string", "null"], "description": "原文时间表达"},
        "event_time": {"type": ["string", "null"], "description": "标准化事件时间"},
        "location": {"type": ["string", "null"], "description": "事件地点"},
        "event_type": {
            "type": "string",
            "enum": [
                "交通事故",
                "道路拥堵",
                "道路施工",
                "交通管制",
                "设施故障",
                "恶劣天气影响",
                "其他",
            ],
        },
        "event_subtype": {"type": ["string", "null"], "description": "事件子类型"},
        "vehicles_involved": {
            "type": "array",
            "items": {"type": "string"},
            "description": "涉及车辆类型",
        },
        "vehicle_count": {"type": ["integer", "null"], "minimum": 0},
        "casualties": {"type": ["string", "null"], "description": "伤亡情况描述"},
        "injured_count": {"type": ["integer", "null"], "minimum": 0},
        "death_count": {"type": ["integer", "null"], "minimum": 0},
        "road_impact": {"type": ["string", "null"], "description": "道路影响"},
        "congestion_level": {
            "type": "string",
            "enum": ["无明显影响", "缓慢", "拥堵", "严重拥堵", "未知"],
        },
        "confidence": {"type": "number", "minimum": 0, "maximum": 1},
        "need_llm_review": {"type": "boolean"},
        "extract_method": {"type": "string"},
    },
}


EMPTY_EVENT = {
    "source_text": "",
    "event_time_text": None,
    "event_time": None,
    "location": None,
    "event_type": "其他",
    "event_subtype": None,
    "vehicles_involved": [],
    "vehicle_count": None,
    "casualties": None,
    "injured_count": None,
    "death_count": None,
    "road_impact": None,
    "congestion_level": "未知",
    "confidence": 0.0,
    "need_llm_review": False,
    "extract_method": "rule",
}
