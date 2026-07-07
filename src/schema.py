from __future__ import annotations

from collections import OrderedDict
from typing import Any


OUTPUT_FIELDS = [
    "source_text",
    "event_type",
    "event_type_code",
    "event_subtype",
    "event_time_text",
    "location",
    "road_name",
    "vehicles_involved",
    "vehicle_count",
    "casualties",
    "injured_count",
    "death_count",
    "road_impact",
    "occupied_lane",
    "congestion_level",
    "disposal_measure",
    "event_status",
]


EVENT_TYPE_CODES = {
    "交通事故": "ACCIDENT",
    "道路拥堵": "CONGESTION",
    "道路施工": "CONSTRUCTION",
    "交通管制": "TRAFFIC_CONTROL",
    "设施故障": "FACILITY_FAILURE",
    "恶劣天气影响": "WEATHER_IMPACT",
    "违法行为": "VIOLATION",
    "其他事件": "OTHER",
}


def empty_event(source_text: str = "") -> OrderedDict[str, Any]:
    return OrderedDict(
        [
            ("source_text", source_text),
            ("event_type", None),
            ("event_type_code", None),
            ("event_subtype", None),
            ("event_time_text", None),
            ("location", None),
            ("road_name", None),
            ("vehicles_involved", []),
            ("vehicle_count", None),
            ("casualties", None),
            ("injured_count", None),
            ("death_count", None),
            ("road_impact", None),
            ("occupied_lane", None),
            ("congestion_level", None),
            ("disposal_measure", None),
            ("event_status", None),
        ]
    )


def normalize_output(data: dict[str, Any]) -> OrderedDict[str, Any]:
    output = empty_event()
    for field in OUTPUT_FIELDS:
        value = data.get(field)
        if field == "vehicles_involved" and value is None:
            value = []
        output[field] = value

    if output["event_type"] and not output["event_type_code"]:
        output["event_type_code"] = EVENT_TYPE_CODES.get(output["event_type"])
    return output
