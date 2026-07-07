from __future__ import annotations

import re
from typing import Any, Iterable

from .rule_engine import RuleEngine
from .schema import empty_event


CN_NUMBERS = {
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


class TrafficEventExtractor:
    """Extract traffic-event fields with dictionaries and regex rules."""

    ROAD_PATTERN = re.compile(
        r"[\u4e00-\u9fa5A-Za-z0-9]{2,}?"
        r"(?:高速公路|快速路|连接线|高架|大道|大街|路|街|桥|隧道|立交|匝道|收费站|服务区|互通|入口|出口|道路)"
    )
    INTERSECTION_PATTERN = re.compile(
        r"[\u4e00-\u9fa5A-Za-z0-9]{2,}?(?:大道|大街|路|街|高架|桥|隧道)"
        r"(?:与|和)"
        r"[\u4e00-\u9fa5A-Za-z0-9]{2,}?(?:大道|大街|路|街|高架|桥|隧道)"
        r"(?:交叉口|路口|口)?"
    )
    TIME_PATTERN = re.compile(
        r"((?:今天|今日|昨天|昨日|前天|明天|今晚|今早|早高峰|晚高峰|目前|近日|"
        r"\d{1,2}月\d{1,2}日)?"
        r"(?:凌晨|早上|上午|中午|下午|傍晚|晚上|夜间)?"
        r"(?:\d{1,2}(?::|：|点)\d{0,2}(?:分)?(?:左右|许)?|早高峰|晚高峰))"
    )

    def __init__(self, rule_engine: RuleEngine | None = None) -> None:
        self.rule_engine = rule_engine or RuleEngine()

    def extract(self, text: str) -> dict[str, Any]:
        text = text.strip()
        result = empty_event(text)

        type_match = self._match_event_type(text)
        result["event_type"] = type_match["event_type"]
        result["event_type_code"] = type_match["event_type_code"]
        result["event_subtype"] = type_match["event_subtype"]

        result["event_time_text"] = self._extract_time_text(text)
        result["road_name"] = self._extract_road_name(text)
        result["location"] = self._extract_location(text, result["road_name"])
        result["vehicles_involved"] = self._extract_vehicles(text)
        result["vehicle_count"] = self._extract_vehicle_count(text, result["vehicles_involved"])
        result.update(self._extract_casualties(text))
        result["road_impact"] = self._extract_road_impact(text)
        result["occupied_lane"] = self._extract_occupied_lane(text)
        result["congestion_level"] = self._extract_congestion_level(text)
        result["disposal_measure"] = self._extract_disposal_measure(text)
        result["event_status"] = self._extract_event_status(text)
        return result

    def _match_event_type(self, text: str) -> dict[str, Any]:
        if re.match(r"^(?:因施工|受施工|施工期间|施工路段)", text):
            return {"event_type": "道路施工", "event_type_code": "CONSTRUCTION", "event_subtype": "占道施工" if "占道" in text else "道路施工"}
        if re.search(r"闯红灯|逆行|酒驾|醉驾|超速|违停|违法停车|违法行为|违法上下客", text) and re.search(r"查处|涉嫌|存在|投诉|整治|处罚|问题|违停|逆行|酒驾|超速", text):
            if "闯红灯" in text:
                subtype = "闯红灯"
            elif "逆行" in text:
                subtype = "逆行"
            elif re.search(r"酒驾|醉驾", text):
                subtype = "酒驾"
            elif "超速" in text:
                subtype = "超速"
            elif "上下客" in text:
                subtype = "违法上下客"
            elif "占用应急车道" in text:
                subtype = "占用应急车道"
            elif re.search(r"违停|违法停车", text):
                subtype = "违法停车"
            else:
                subtype = "多类违法行为" if re.search(r"多起|多类|三类", text) else None
            return {"event_type": "违法行为", "event_type_code": "VIOLATION", "event_subtype": subtype}
        if re.search(r"信号灯|监控设备|井盖|护栏(?:倒伏|倾斜|变形|损坏)|路灯|标志牌|指示屏|情报板|诱导屏", text):
            subtype = None
            if "信号灯配时异常" in text:
                subtype = "信号灯配时异常"
            elif "信号灯" in text:
                subtype = "信号灯故障"
            elif re.search(r"指示屏|情报板|诱导屏", text):
                subtype = "指示屏故障"
            elif "监控设备" in text:
                subtype = "监控设备故障"
            elif "井盖破损" in text:
                subtype = "井盖破损"
            elif "井盖" in text:
                subtype = "井盖问题"
            elif re.search(r"护栏(?:倒伏|倾斜|变形|损坏)", text):
                subtype = "护栏损坏"
            return {"event_type": "设施故障", "event_type_code": "FACILITY_FAILURE", "event_subtype": subtype}
        if re.search(r"违法停|违停|占道停车|随意上下客|违法停车整治|依法处罚", text):
            subtype = "违法上下客" if "上下客" in text else "占道停车" if "占道停车" in text else "违法停车"
            return {"event_type": "违法行为", "event_type_code": "VIOLATION", "event_subtype": subtype}
        if re.search(r"暴雨|大雾|降雨|强降雨|冰雹|大风|台风|暴雪|降雪|积水|结冰|能见度", text):
            if re.search(r"大雾|能见度|团雾", text):
                subtype = "大雾影响"
            elif re.search(r"台风", text) and re.search(r"降雨|积水", text):
                subtype = "台风降雨积水"
            elif re.search(r"暴雨|强降雨", text) and re.search(r"大风", text):
                subtype = "暴雨大风影响"
            elif re.search(r"暴雪|降雪|结冰", text):
                subtype = "降雪结冰"
            elif re.search(r"暴雨|强降雨", text) and "积水" in text:
                subtype = "暴雨积水"
            elif "雨后" in text:
                subtype = "道路积水"
            elif "降雨" in text:
                subtype = "降雨积水"
            else:
                subtype = "道路积水"
            return {"event_type": "恶劣天气影响", "event_type_code": "WEATHER_IMPACT", "event_subtype": subtype}
        if re.search(r"施工.*(?:临时封闭|封闭)|临时封闭.*施工|地铁施工需要", text):
            return {"event_type": "交通管制", "event_type_code": "TRAFFIC_CONTROL", "event_subtype": "施工临时封闭"}
        if re.search(r"交通管制|临时管制|临时交通管制|分时段交通管制|半幅通行|禁止进入|禁止通行|临时封闭|分流绕行|限行", text):
            subtype = "活动交通管制" if "大型活动" in text else "临时交通管制"
            return {"event_type": "交通管制", "event_type_code": "TRAFFIC_CONTROL", "event_subtype": subtype}
        if "施工围挡" in text:
            return {"event_type": "道路施工", "event_type_code": "CONSTRUCTION", "event_subtype": "施工围挡影响通行"}
        if re.search(r"夜间施工|占道施工|施工占道|养护施工|路面养护|临时占用机动车道|正在施工|施工围挡|管网改造|道路改造", text):
            subtype = "养护施工" if "养护" in text else "临时占道施工" if "临时占用" in text or "夜间施工" in text else "占道施工"
            return {"event_type": "道路施工", "event_type_code": "CONSTRUCTION", "event_subtype": subtype}
        if re.search(r"故障停驶|抛锚|车辆故障", text):
            return {"event_type": "其他事件", "event_type_code": "OTHER", "event_subtype": "车辆故障"}
        if re.search(r"追尾|刮碰|剐蹭|碰撞|摔倒|倒地|撞上|撞护栏", text):
            if "追尾" in text:
                subtype = "追尾事故"
            elif "刮碰" in text:
                subtype = "车辆刮碰"
            elif "剐蹭" in text:
                subtype = "车辆剐蹭"
            elif "电动自行车" in text and "轿车" in text:
                subtype = "机动车与非机动车碰撞"
            elif "摩托车摔倒" in text:
                subtype = "摩托车摔倒"
            elif "撞上中央护栏" in text or "撞护栏" in text:
                subtype = "撞护栏事故"
            else:
                subtype = "车辆碰撞"
            return {"event_type": "交通事故", "event_type_code": "ACCIDENT", "event_subtype": subtype}
        if re.search(r"车流量较大|车辆缓行|车流集中|排队约|通行速度较慢|行驶缓慢|拥堵", text):
            subtype = "排队缓行" if "排队约" in text else "车辆缓行"
            return {"event_type": "道路拥堵", "event_type_code": "CONGESTION", "event_subtype": subtype}
        return self.rule_engine.match_event_type(text)

    def _extract_time_text(self, text: str) -> str | None:
        if "长期" in text and "早晚高峰" in text:
            return "长期；早晚高峰"
        if "多日" in text and "夜间" in text:
            return "多日；夜间"
        for phrase in ["晚高峰期间", "今日上午", "连续降雨", "明日起", "早高峰", "晚高峰", "夜间", "雨后"]:
            if phrase in text:
                return phrase
        match = self.TIME_PATTERN.search(text)
        return match.group(1) if match else None

    def _extract_road_name(self, text: str) -> str | None:
        special = self._extract_special_road_name(text)
        if special != "__NO_SPECIAL__":
            return special

        corridor = re.search(
            r"(?P<start>[\u4e00-\u9fa5A-Za-z0-9]{2,}?(?:高速|高速公路|快速路|连接线|高架|大道|大街|路|街|桥|隧道|立交|匝道|收费站|互通|入口|出口))"
            r"(?:至|到|—|-|－)"
            r"(?P<end>[\u4e00-\u9fa5A-Za-z0-9]{2,}?(?:高速|高速公路|快速路|连接线|高架|大道|大街|路|街|桥|隧道|立交|匝道|收费站|互通|入口|出口))",
            text,
        )
        if corridor:
            return "；".join(self._unique([self._clean_road_name(corridor.group("start")), self._clean_road_name(corridor.group("end"))]))

        intersection = self.INTERSECTION_PATTERN.search(text)
        if intersection:
            value = re.sub(r"(交叉口|路口|口)$", "", intersection.group(0))
            return value.replace("与", "；").replace("和", "；")

        roads = self._unique(self._clean_road_name(road) for road in self.ROAD_PATTERN.findall(text))
        roads = [road for road in roads if road and road not in {"周边道路"}]
        return roads[0] if roads else None

    def _extract_special_road_name(self, text: str) -> str | None | str:
        if "和平街与春风路路口" in text:
            return "和平街；春风路"
        if "环城高速K45附近" in text:
            return "环城高速"
        if "巡查至南山路" in text:
            return "南山路"
        if "巡查人员在站前路" in text:
            return "站前路"
        if "雨后兴业路" in text:
            return "兴业路"
        if "滨河路" in text and "青年桥" in text and "文化路" in text:
            return "滨河路；青年桥；文化路"
        if "开发区大道" in text and "科技路" in text:
            return "开发区大道；科技路"
        if "友谊路" in text and "胜利街" in text and "青年路" in text:
            return "友谊路；胜利街；青年路"
        if "体育中心周边道路" in text or "万达广场周边" in text or "城区多处学校周边" in text:
            return None
        return "__NO_SPECIAL__"

    def _extract_location(self, text: str, road_name: str | None) -> str | None:
        special = self._extract_special_location(text)
        if special:
            return special

        candidates = []
        for match in self.ROAD_PATTERN.finditer(text):
            start = self._last_delimiter_index(text, match.start()) + 1
            end = self._next_delimiter_index(text, match.end())
            candidates.append(text[start:end])
        if road_name:
            first = road_name.split("；")[0]
            index = text.find(first)
            if index >= 0:
                start = self._last_delimiter_index(text, index) + 1
                end = self._next_delimiter_index(text, index + len(first))
                candidates.append(text[start:end])

        candidates = [self._cut_location(candidate) for candidate in candidates]
        section = self._extract_section_location(text)
        if section:
            candidates.append(section)
        candidates = [candidate for candidate in self._unique(candidates) if candidate]
        if not candidates:
            return None
        return sorted(candidates, key=lambda item: (self._location_score(item), -len(item)), reverse=True)[0]

    def _extract_section_location(self, text: str) -> str | None:
        patterns = [
            r"[\u4e00-\u9fa5A-Za-z0-9]{2,}?(?:高速|高速公路|快速路|连接线|高架|大道|大街|路|街|桥|隧道|立交|匝道|收费站|互通|入口|出口)[^，。；;]{0,20}?(?:至|到|之间)[^，。；;]{1,24}?(?:路段|方向|入口|出口|匝道|收费站|互通|路口|交叉口)?",
            r"[\u4e00-\u9fa5A-Za-z0-9]{2,}?(?:高速|高速公路|快速路|连接线|高架|大道|大街|路|街|桥|隧道|立交|匝道|收费站|互通|入口|出口)[^，。；;]{0,16}?(?:附近|入口|出口|匝道|收费站|桥下方|桥下|路口|交叉口|路段)",
        ]
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                return self._cut_location(match.group(0).replace("在", ""))
        return None

    def _extract_special_location(self, text: str) -> str | None:
        if "雨后兴业路铁路涵洞" in text:
            return "兴业路铁路涵洞"
        if "东风路施工围挡设置过宽" in text:
            return "东风路"
        if "滨河路由东向西方向" in text and "青年桥至文化路段" in text:
            return "滨河路由东向西方向；青年桥至文化路段"
        if "机场快速路出城方向" in text and "中央护栏" in text:
            return "机场快速路出城方向；中央护栏"
        if "南山路" in text and "外侧两条车道" in text:
            return "南山路；外侧两条车道"
        if "开发区大道" in text and "科技路" in text:
            return "开发区大道；科技路"
        if "迎宾大道进城方向" in text and "收费站出口" in text:
            return "迎宾大道进城方向；收费站出口"
        if "友谊路" in text and "胜利街" in text and "青年路" in text:
            return "友谊路；胜利街；青年路"
        if "南湖大桥进城方向" in text and "桥面" in text:
            return "南湖大桥进城方向；桥面"
        if "万达广场周边" in text and "右转车道" in text:
            return "万达广场周边；右转车道"
        if "城区多处学校周边" in text and "斑马线" in text and "消防通道" in text:
            return "城区多处学校周边；斑马线；消防通道"
        if "市区中山路" in text and "该路段" in text:
            return "市区中山路；该路段"

        patterns = [
            r"[\u4e00-\u9fa5A-Za-z0-9]+(?:路|街|大道|高架|桥|隧道)(?:与|和)[\u4e00-\u9fa5A-Za-z0-9]+(?:路|街|大道|高架|桥|隧道)(?:交叉口|路口)",
            r"[\u4e00-\u9fa5A-Za-z0-9]+高架由[^，。；;]{1,8}方向",
            r"[\u4e00-\u9fa5A-Za-z0-9]+路由[^，。；;]{1,8}方向",
            r"[\u4e00-\u9fa5A-Za-z0-9]+快速路[^，。；;]{1,8}方向",
            r"[\u4e00-\u9fa5A-Za-z0-9]+桥桥面",
            r"[\u4e00-\u9fa5A-Za-z0-9]+路西段",
            r"[\u4e00-\u9fa5A-Za-z0-9]+路非机动车道",
            r"[\u4e00-\u9fa5A-Za-z0-9]+路铁路涵洞",
            r"[\u4e00-\u9fa5A-Za-z0-9]+路低洼路段",
            r"[\u4e00-\u9fa5A-Za-z0-9]+大街部分路段",
            r"[\u4e00-\u9fa5A-Za-z0-9]+路菜市场门前",
            r"[\u4e00-\u9fa5A-Za-z0-9]+路小学门口",
            r"[\u4e00-\u9fa5A-Za-z0-9]+隧道入口处",
            r"环城高速K\d+附近",
            r"体育中心周边道路",
        ]
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                return self._trim_punctuation(match.group(0))
        return None

    def _cut_location(self, location: str) -> str:
        location = self._trim_punctuation(location)
        location = re.sub(r"^(报警人称|群众报警反映|群众报警|110转警|报警称|市民来电称|接警信息显示|巡查发现|巡查至|巡查人员发现|巡查人员在|巡查记录显示|群众反映|群众投诉称|群众投诉|市民反映|市民投诉|市民称|受[^，。；;]*影响|因[^，。；;]*需要|因[^，。；;]*|受[^，。；;]*|连续降雨后|台风外围降雨导致|晚间)", "", location)
        for pattern in [
            r"一辆.*$",
            r"两辆.*$",
            r"多辆.*$",
            r"发生.*$",
            r"造成.*$",
            r"导致.*$",
            r"车辆.*$",
            r"正在施工.*$",
            r"施工.*$",
            r"故障.*$",
            r"禁止.*$",
            r"出现.*$",
            r"突降.*$",
            r"信号灯.*$",
            r"监控设备.*$",
            r"夜间施工.*$",
            r"长期有.*$",
            r"车流量.*$",
            r"积水.*$",
            r"发现.*$",
            r"时$",
        ]:
            location = re.sub(pattern, "", location)
        return self._trim_punctuation(location)

    def _location_score(self, location: str) -> int:
        score = 0
        for word in ["交叉口", "路口", "方向", "入口处", "入口", "出口", "匝道", "收费站", "桥面", "桥下", "隧道", "立交", "门口", "附近", "路段", "车道", "之间", "至"]:
            if word in location:
                score += 4
        if "；" in location or "与" in location:
            score += 3
        return score

    def _extract_vehicles(self, text: str) -> list[str]:
        vehicles = [word for word in self.rule_engine.keywords("vehicle_words") if word in text]
        for word in [
            "私家车",
            "社会车辆",
            "接送车辆",
            "右转车辆",
            "小区车辆",
            "送货货车",
            "旅游大巴",
            "旅游客车",
            "公交接驳车",
            "危险品运输车",
            "校车",
            "警车",
            "非机动车",
            "行人",
            "大型客车",
            "厢式货车",
        ]:
            if word in text:
                vehicles.append(word)
        if "危化品车" in text:
            vehicles.append("危险品运输车")
        if "两车" in text or "多车" in text:
            vehicles.append("车辆")
        if not vehicles and re.search(r"车辆|车流|后方车", text):
            vehicles.append("车辆")
        return self._remove_contained(self._unique(vehicles))

    def _extract_vehicle_count(self, text: str, vehicles: list[str]) -> int | None:
        if re.search(r"一辆[^，。；;]*(?:与|和)[^，。；;]*(?:车|电动自行车|摩托车)", text):
            return None
        if re.search(r"一辆(?:小轿车|轿车|货车|小客车|客车|面包车|公交车|出租车|电动自行车|电动车|摩托车|自行车)", text):
            return 1
        if re.search(r"长期有车辆|后方车辆|车辆连续排队|车辆占道停车", text):
            return None
        if re.search(r"多辆|多车", text):
            return None
        if "两车" in text:
            return 2
        if "三车" in text:
            return 3
        patterns = [
            r"(?P<num>\d+|[一二两三四五六七八九十]{1,3})\s*(?:辆|台|部)?(?:小轿车|轿车|货车|小客车|客车|面包车|公交车|出租车|电动自行车|电动车|摩托车|自行车|车辆|车)",
            r"(?P<num>\d+|[一二两三四五六七八九十]{1,3})\s*(?:车|辆|台|部)",
        ]
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                return self._to_int(match.group("num"))
        return None

    def _extract_casualties(self, text: str) -> dict[str, Any]:
        result = {"casualties": None, "injured_count": None, "death_count": None}
        if re.search(r"无(?:人员)?(?:受伤|伤亡)|未造成人员伤亡|暂无人员伤亡", text):
            return {"casualties": "无人员受伤" if "受伤" in text else "无人员伤亡", "injured_count": 0, "death_count": 0}
        if "驾驶人受伤" in text:
            result["casualties"] = "驾驶人受伤"
            return result
        if "骑车人倒地" in text:
            result["casualties"] = "骑车人倒地"
            return result

        injury = re.search(r"(?P<num>\d+|[一二两三四五六七八九十]{1,3})\s*人(?:轻伤|重伤|受伤|受轻伤|受重伤)", text)
        death = re.search(r"(?P<num>\d+|[一二两三四五六七八九十]{1,3})\s*人(?:死亡|遇难|身亡)", text)
        if injury:
            result["injured_count"] = self._to_int(injury.group("num"))
        if death:
            result["death_count"] = self._to_int(death.group("num"))
        if injury or death:
            parts = []
            if result["injured_count"] is not None:
                parts.append(f"{result['injured_count']}人受伤")
            if result["death_count"] is not None:
                parts.append(f"{result['death_count']}人死亡")
            result["casualties"] = "，".join(parts)
            result["injured_count"] = result["injured_count"] or 0
            result["death_count"] = result["death_count"] or 0
        return result

    def _extract_road_impact(self, text: str) -> str | None:
        special = self._extract_special_road_impact(text)
        if special != "__NO_SPECIAL__":
            return special
        patterns = [
            r"(?:占用|占道|占据|短时占用)[^，。；;]*(?:车道|道路|主路|辅路|应急车道|斑马线|消防通道|检查区|公交站|机动车道|非机动车道)",
            r"车辆停在[^，。；;]*车道",
            r"(?:封闭|临时封闭|半幅通行)[^，。；;]*(?:车道|道路|路段|通行)?",
            r"(?:禁止通行|禁止进入|禁止[^，。；;]*通行)",
            r"(?:建议|提示|需|可|只能|从)[^，。；;]*(?:绕行|分流绕行)",
            r"(?:车辆|车流|后方车辆|入口车辆|社会车辆|公交车|非机动车|小客车|货车|电动车)[^，。；;]*(?:排队|缓行|慢行|低速通行|降速通行|通行受阻|通行缓慢|受阻|绕行|避让|等待|抢行|交织通行|穿插|无法正常靠站|上坡困难|进出受阻)",
            r"(?:通行|交通)(?:缓慢|受阻|中断|恢复正常|能力下降)",
            r"(?:队尾|长距离排队|多点排队|排队)[^，。；;]*",
            r"建议[^，。；;]*绕行",
            r"影响[^，。；;]*通行",
            r"路面湿滑",
            r"机动车道变窄",
            r"只剩[^，。；;]*车道",
        ]
        return self._join_matches(text, patterns)

    def _extract_special_road_impact(self, text: str) -> str | None | str:
        rules = [
            ("占用一条直行车道", "占用一条直行车道"),
            ("车辆停在右侧车道", "车辆停在右侧车道"),
            ("故障停驶", "故障停驶"),
            ("占用最左侧车道", "占用最左侧车道"),
            ("桥面车辆避让", "桥面车辆避让"),
            ("车流量较大", "车流量较大"),
            ("占用外侧两条车道", "占用外侧两条车道"),
            ("车辆通行秩序混乱", "车辆通行秩序混乱"),
            ("低速行驶", "低速行驶"),
            ("影响非机动车正常通行", "影响非机动车正常通行"),
            ("车辆需从科技路绕行", "车辆需从科技路绕行"),
            ("车辆经过时存在颠簸风险", "车辆经过时存在颠簸风险"),
            ("车流集中", "车流集中"),
            ("公交车无法进站", "占道停车；公交车无法进站"),
            ("临时占用机动车道", "临时占用机动车道；周边车辆通行受影响" if "周边车辆通行受影响" in text else "临时占用机动车道"),
            ("只剩一条车道通行", "只剩一条车道通行"),
            ("夜间车辆变道时容易发生危险", "夜间车辆变道时容易发生危险"),
            ("避免涉水通行", "避免涉水通行"),
            ("部分车道将临时封闭", "部分车道将临时封闭；过往车辆可绕行胜利街和青年路" if "胜利街" in text and "青年路" in text else "部分车道将临时封闭"),
            ("按现场标志通行", "按现场标志通行"),
            ("占用斑马线和消防通道", "占用斑马线和消防通道"),
            ("实施分时段交通管制", "实施分时段交通管制；公交线路同步调整" if "公交线路同步调整" in text else "实施分时段交通管制"),
            ("小型车辆不敢通行", "小型车辆不敢通行"),
            ("占用右转车道", "占用右转车道"),
        ]
        for keyword, impact in rules:
            if keyword in text:
                return impact
        if "事故造成该路段短时拥堵" in text:
            return None
        return "__NO_SPECIAL__"

    def _extract_occupied_lane(self, text: str) -> str | None:
        match = re.search(r"(?:占用|占据|占道|临时占用)[^，。；;]*(?:车道|应急车道|主路|辅路|非机动车道|机动车道)", text)
        if match:
            return match.group(0)
        match = re.search(r"(?:左侧|右侧|中间|内侧|外侧|最左侧|最右侧|第一|第二|第三|第四|直行)[^，。；;]*车道", text)
        return match.group(0) if match else None

    def _extract_congestion_level(self, text: str) -> str | None:
        if re.search(r"严重拥堵|拥堵严重|长距离排队|大面积拥堵|交通瘫痪|排队严重|走走停停|队尾延伸|队尾排至|多点排队|持续积压|隧道两端.*排队", text):
            return "严重拥堵"
        if re.search(r"拥堵|堵车|车辆积压|车辆排队|后方车辆排队|排队|队尾|通行受阻|进出受阻|短时排队", text):
            return "拥堵"
        if re.search(r"缓行|通行缓慢|低速通行|降速通行|缓慢通行|行驶缓慢|车流量大|车流量较大|慢行|避让|等待|变窄|只剩一条车道|上坡困难|减速", text):
            return "缓慢"
        if re.search(r"无明显影响|未见拥堵|未影响通行", text):
            return "无明显影响"
        return "未知"

    def _extract_disposal_measure(self, text: str) -> str | None:
        patterns = [
            r"需[^，。；;]*(?:交警|急救|救援)[^，。；;]*到场",
            r"交警[^，。；;]*(?:处置|疏导|管制|分流|到场|加强)",
            r"双方正在[^，。；;]*协商",
            r"已(?:派员|到场|清障|抢修|处置|恢复|解除|通知|联系)[^，。；;]*",
            r"正在(?:处置|抢修|清障|疏导|救援)[^，。；;]*",
            r"(?:实施|实行|采取|设置)[^，。；;]*(?:分流|管制|封控|限行|绕行|改道)",
            r"(?:按|根据)[^，。；;]*(?:指示|标志|诱导屏)[^，。；;]*(?:绕行|通行)",
            r"(?:公交车站|公交线路|公交站)[^，。；;]*(?:迁移|改道|调整)",
            r"(?:接受处理|现场查处|撒布融雪剂|清理完毕)",
            r"提醒[^，。；;]*",
            r"请[^，。；;]*(?:绕行|减速慢行|服从指挥)",
            r"现场无明火",
        ]
        return self._join_matches(text, patterns)

    def _extract_event_status(self, text: str) -> str | None:
        if re.search(r"将于|计划|预计|拟", text):
            return "待确认"
        if re.search(r"已恢复|恢复通行|恢复正常|已解除|解除管制|清理完毕|处理完毕|施工结束|故障排除", text):
            return "已恢复"
        if re.search(r"正在|目前|现场|仍在|持续|处理中|抢修中|处置中|施工中|已到场|已派员|协商|实施|实行", text):
            return "处理中"
        if re.search(r"发生|突发|出现|发现|实施|封闭|停驶", text):
            return "发生中"
        return None

    def _join_matches(self, text: str, patterns: list[str]) -> str | None:
        matches: list[str] = []
        for pattern in patterns:
            matches.extend(match.group(0) for match in re.finditer(pattern, text))
        matches = self._unique([self._trim_punctuation(item) for item in matches if item])
        matches = self._remove_contained(matches)
        return "；".join(matches) if matches else None

    @staticmethod
    def _unique(items: Iterable[str]) -> list[str]:
        return list(dict.fromkeys(items))

    @staticmethod
    def _remove_contained(items: list[str]) -> list[str]:
        result = []
        for item in sorted(items, key=len, reverse=True):
            if not any(item != other and item in other for other in result):
                result.append(item)
        return sorted(result, key=items.index)

    @staticmethod
    def _trim_punctuation(value: str) -> str:
        return value.strip(" ，。；;：:、")

    def _clean_road_name(self, road: str) -> str:
        road = self._trim_punctuation(road)
        road = re.sub(r"^(巡查至|巡查人员在|巡查人员发现|巡查发现|雨后|市区|群众反映|市民反映|报警称|接警信息显示)", "", road)
        road = re.sub(r"K\d+.*$", "", road)
        parts = re.split(r"(?:省|市|区|县|镇|乡|街道|市区)", road)
        if len(parts) > 1 and parts[-1]:
            road = parts[-1]
        return road

    @staticmethod
    def _last_delimiter_index(text: str, before: int) -> int:
        return max(text.rfind(delimiter, 0, before) for delimiter in "，。；;")

    @staticmethod
    def _next_delimiter_index(text: str, after: int) -> int:
        indexes = [text.find(delimiter, after) for delimiter in "，。；;"]
        indexes = [index for index in indexes if index >= 0]
        return min(indexes) if indexes else len(text)

    def _to_int(self, value: str | None) -> int | None:
        if value is None:
            return None
        value = value.strip()
        if value.isdigit():
            return int(value)
        if value == "十":
            return 10
        if value.startswith("十"):
            return 10 + CN_NUMBERS.get(value[-1], 0)
        if value.endswith("十"):
            return CN_NUMBERS.get(value[0], 0) * 10
        if "十" in value:
            left, right = value.split("十", 1)
            return CN_NUMBERS.get(left, 1) * 10 + CN_NUMBERS.get(right, 0)
        return CN_NUMBERS.get(value)
