from __future__ import annotations

import json

from src.pipeline import TrafficEventPipeline


SAMPLES = [
    "今天上午8点30分，重庆市南岸区学府大道发生两车追尾事故，造成1人轻伤，占用右侧车道，现场通行缓慢，交警正在疏导。",
    "昨日17:20，人民路与建设路路口发生小轿车与电动车碰撞，2人受伤，车辆排队约300米，交警已到场处置。",
    "7月6日早上6:20，机场快速路因占道施工实施临时管制，部分路段通行缓慢，请过往车辆绕行。",
    "今晚20:10，解放碑隧道内信号灯故障，现场交通拥堵，正在抢修，暂无人员伤亡。",
    "受暴雨影响，滨江路低洼路段出现积水，车辆通行受阻，交警采取分流措施。",
    "中山路附近有车辆违法停车，占用非机动车道，请驾驶员尽快驶离。",
]


def main() -> None:
    pipeline = TrafficEventPipeline()
    for index, sample in enumerate(SAMPLES, start=1):
        print(f"\n===== 样例 {index} =====")
        print(sample)
        print(json.dumps(pipeline.parse(sample), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
