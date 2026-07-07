"""Rule-based extraction engine for Chinese traffic event texts."""

from __future__ import annotations

import copy
import re
from datetime import date, datetime, time, timedelta
from typing import Any

from .schemas import EMPTY_EVENT


CHINESE_NUMBER_MAP = {
    "零": 0,
    "一": 1,
    "二": 2,
    "两": 2,
    "三": 3,
    "四": 4,
    "五": 5,
    "六": 6,
    "七": 7,
    "八": 8,
    "九": 9,
    "十": 10,
}


class RuleBasedExtractor:
    """Extract structured fields using dictionaries and regex rules."""

    EVENT_RULES = [
        ("交通事故", ["事故", "追尾", "碰撞", "相撞", "剐蹭", "侧翻", "撞上"], "事故"),
        ("道路施工", ["施工", "抢修", "养护", "占道施工"], None),
        ("交通管制", ["管制", "封闭", "临时交通管制", "禁止通行"], None),
        ("设施故障", ["信号灯故障", "路灯故障", "井盖", "护栏损坏", "标志牌损坏"], None),
        ("道路拥堵", ["拥堵", "堵车", "排队", "通行缓慢", "车流缓慢"], None),
        ("恶劣天气影响", ["暴雨", "大雾", "降雪", "积水", "结冰", "强降雨"], None),
    ]

    SUBTYPE_RULES = [
        ("追尾事故", ["追尾"]),
        ("碰撞事故", ["碰撞", "相撞", "撞上"]),
        ("剐蹭事故", ["剐蹭"]),
        ("侧翻事故", ["侧翻"]),
        ("道路积水", ["积水"]),
        ("信号灯故障", ["信号灯故障"]),
    ]

    VEHICLE_WORDS = [
        "小轿车",
        "轿车",
        "货车",
        "客车",
        "公交车",
        "出租车",
        "网约车",
        "电动车",
        "摩托车",
        "自行车",
        "三轮车",
        "渣土车",
        "危化品车",
    ]

    ROAD_SUFFIX_PATTERN = (
        r"[\u4e00-\u9fa5A-Za-z0-9]{2,}"
        r"(?:大道|快速路|高速|公路|路口|街口|立交|隧道|匝道|收费站|路|街|巷|桥)"
    )

    def extract(self, text: str, reference_date: date | None = None) -> dict[str, Any]:
        reference_date = reference_date or date.today()
        result = copy.deepcopy(EMPTY_EVENT)
        result["source_text"] = text.strip()

        result.update(self._extract_time(text, reference_date))
        result["location"] = self._extract_location(text)
        event_type, event_subtype, type_score = self._extract_event_type(text)
        result["event_type"] = event_type
        result["event_subtype"] = event_subtype

        vehicles, vehicle_count = self._extract_vehicles(text)
        result["vehicles_involved"] = vehicles
        result["vehicle_count"] = vehicle_count

        result.update(self._extract_casualties(text))
        result["road_impact"] = self._extract_road_impact(text)
        result["congestion_level"] = self._extract_congestion_level(text)

        result["confidence"] = self._estimate_confidence(result, type_score)
        result["need_llm_review"] = result["confidence"] < 0.75
        return result

    def _extract_time(self, text: str, reference_date: date) -> dict[str, str | None]:
        patterns = [
            r"(?P<prefix>今天|今日|昨天|昨日|明天|前天|后天)?"
            r"(?P<period>凌晨|早上|上午|中午|下午|傍晚|晚上|夜间)?"
            r"(?P<hour>\d{1,2}|[一二两三四五六七八九十]{1,3})点"
            r"(?P<minute>半|\d{1,2}分?)?",
            r"(?P<month>\d{1,2})月(?P<day>\d{1,2})日"
            r"(?P<period>凌晨|早上|上午|中午|下午|傍晚|晚上|夜间)?"
            r"(?P<hour>\d{1,2})[:：点](?P<minute>\d{1,2})?分?",
            r"(?P<hour>\d{1,2})[:：](?P<minute>\d{1,2})",
        ]
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                raw = match.group(0)
                standard = self._normalize_time(match.groupdict(), reference_date)
                return {"event_time_text": raw, "event_time": standard}
        return {"event_time_text": None, "event_time": None}

    def _normalize_time(self, data: dict[str, str | None], reference_date: date) -> str | None:
        event_date = reference_date
        prefix = data.get("prefix")
        if prefix in {"昨天", "昨日"}:
            event_date = reference_date - timedelta(days=1)
        elif prefix == "前天":
            event_date = reference_date - timedelta(days=2)
        elif prefix == "明天":
            event_date = reference_date + timedelta(days=1)
        elif prefix == "后天":
            event_date = reference_date + timedelta(days=2)

        if data.get("month") and data.get("day"):
            event_date = date(reference_date.year, int(data["month"]), int(data["day"]))

        hour = self._to_int(data.get("hour"))
        if hour is None:
            return None
        minute_raw = data.get("minute")
        minute = 30 if minute_raw == "半" else self._to_int((minute_raw or "0").replace("分", ""))
        minute = minute if minute is not None else 0

        period = data.get("period")
        if period in {"下午", "傍晚", "晚上", "夜间"} and hour < 12:
            hour += 12
        if period == "中午" and hour < 11:
            hour += 12
        if hour > 23 or minute > 59:
            return None
        return datetime.combine(event_date, time(hour, minute)).isoformat()

    def _extract_location(self, text: str) -> str | None:
        road_match = re.search(self.ROAD_SUFFIX_PATTERN, text)
        if not road_match:
            return None

        road = road_match.group(0)
        start = max(0, road_match.start() - 20)
        prefix_text = text[start : road_match.start()]
        admin_parts = re.findall(r"[\u4e00-\u9fa5]{2,}(?:省|市|区|县|镇|街道)", prefix_text)
        location = "".join(admin_parts) + road if admin_parts else road
        return location

    def _extract_event_type(self, text: str) -> tuple[str, str | None, float]:
        best_type = "其他"
        best_score = 0.2
        for event_type, keywords, _ in self.EVENT_RULES:
            hits = sum(1 for keyword in keywords if keyword in text)
            if hits:
                score = min(0.6 + hits * 0.15, 0.95)
                if score > best_score:
                    best_type = event_type
                    best_score = score

        subtype = None
        for candidate, keywords in self.SUBTYPE_RULES:
            if any(keyword in text for keyword in keywords):
                subtype = candidate
                break
        return best_type, subtype, best_score

    def _extract_vehicles(self, text: str) -> tuple[list[str], int | None]:
        vehicles = [word for word in self.VEHICLE_WORDS if word in text]
        vehicles = self._remove_contained_terms(list(dict.fromkeys(vehicles)))

        count_patterns = [
            r"(?P<num>\d+|[一二两三四五六七八九十]{1,3})车",
            r"(?P<num>\d+|[一二两三四五六七八九十]{1,3})辆",
        ]
        vehicle_count = None
        for pattern in count_patterns:
            match = re.search(pattern, text)
            if match:
                vehicle_count = self._to_int(match.group("num"))
                break

        if vehicle_count is None and vehicles:
            vehicle_count = len(vehicles)
        return vehicles, vehicle_count

    def _remove_contained_terms(self, terms: list[str]) -> list[str]:
        result = []
        for term in sorted(terms, key=len, reverse=True):
            if not any(term != other and term in other for other in result):
                result.append(term)
        return sorted(result, key=terms.index)

    def _extract_casualties(self, text: str) -> dict[str, Any]:
        result = {"casualties": None, "injured_count": None, "death_count": None}
        casualty_match = re.search(
            r"(?P<num>\d+|[一二两三四五六七八九十]{1,3})人"
            r"(?P<level>轻伤|重伤|受伤|伤|死亡|遇难|被困)",
            text,
        )
        if casualty_match:
            result["casualties"] = casualty_match.group(0)
            num = self._to_int(casualty_match.group("num"))
            level = casualty_match.group("level")
            if level in {"死亡", "遇难"}:
                result["death_count"] = num
                result["injured_count"] = 0
            elif level in {"轻伤", "重伤", "受伤", "伤"}:
                result["injured_count"] = num
                result["death_count"] = 0
        elif any(word in text for word in ["无人员伤亡", "未造成人员伤亡"]):
            result["casualties"] = "无人员伤亡"
            result["injured_count"] = 0
            result["death_count"] = 0
        return result

    def _extract_road_impact(self, text: str) -> str | None:
        patterns = [
            r"占用[^，。；;]*车道",
            r"封闭[^，。；;]*",
            r"通行缓慢",
            r"车辆排队[^，。；;]*",
            r"交通拥堵",
            r"临时管制",
            r"禁止通行",
            r"积水严重",
        ]
        impacts = []
        for pattern in patterns:
            impacts.extend(match.group(0) for match in re.finditer(pattern, text))
        if impacts:
            return "；".join(dict.fromkeys(impacts))
        return None

    def _extract_congestion_level(self, text: str) -> str:
        if any(word in text for word in ["严重拥堵", "大面积拥堵", "长时间拥堵", "积压严重"]):
            return "严重拥堵"
        if any(word in text for word in ["拥堵", "堵车", "排队", "车辆积压"]):
            return "拥堵"
        if any(word in text for word in ["通行缓慢", "缓行", "车流缓慢"]):
            return "缓慢"
        if any(word in text for word in ["无明显影响", "通行正常", "已恢复"]):
            return "无明显影响"
        return "未知"

    def _estimate_confidence(self, result: dict[str, Any], type_score: float) -> float:
        field_score = 0.0
        important_fields = [
            "event_time",
            "location",
            "event_type",
            "vehicle_count",
            "casualties",
            "road_impact",
            "congestion_level",
        ]
        for field in important_fields:
            value = result.get(field)
            if value not in (None, "", [], "未知", "其他"):
                field_score += 1
        confidence = 0.35 * type_score + 0.65 * (field_score / len(important_fields))
        return round(min(max(confidence, 0.0), 0.99), 2)

    def _to_int(self, value: str | None) -> int | None:
        if value is None or value == "":
            return None
        if value.isdigit():
            return int(value)
        if value == "十":
            return 10
        if value.startswith("十"):
            return 10 + CHINESE_NUMBER_MAP.get(value[-1], 0)
        if value.endswith("十"):
            return CHINESE_NUMBER_MAP.get(value[0], 0) * 10
        if "十" in value:
            left, right = value.split("十", 1)
            return CHINESE_NUMBER_MAP.get(left, 1) * 10 + CHINESE_NUMBER_MAP.get(right, 0)
        return CHINESE_NUMBER_MAP.get(value)
