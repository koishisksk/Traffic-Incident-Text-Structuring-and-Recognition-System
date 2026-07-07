from __future__ import annotations

import argparse
import json

from src.pipeline import TrafficEventPipeline


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="交通事件文本结构化识别系统 MVP")
    parser.add_argument("--text", "-t", help="待识别的中文交通事件文本")
    parser.add_argument("--compact", action="store_true", help="输出单行紧凑 JSON")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    text = args.text
    if not text:
        text = input("请输入交通事件文本：").strip()

    pipeline = TrafficEventPipeline()
    result = pipeline.parse(text)
    print(json.dumps(result, ensure_ascii=False, indent=None if args.compact else 2))


if __name__ == "__main__":
    main()
