from __future__ import annotations

from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

from src.pipeline import TrafficEventPipeline


app = FastAPI(title="交通事件文本结构化识别系统", version="1.0")
pipeline = TrafficEventPipeline()
BASE_DIR = Path(__file__).resolve().parent


class AnalyzeRequest(BaseModel):
    text: str = Field(..., description="交通事件文本")


class BatchAnalyzeRequest(BaseModel):
    texts: list[str] = Field(..., description="多个交通事件文本")


@app.get("/")
def root() -> dict[str, Any]:
    return {
        "name": "交通事件文本结构化识别系统",
        "version": "1.0",
        "interfaces": {
            "GET /health": "健康检查，返回服务状态",
            "GET /demo": "打开前端演示页面",
            "POST /analyze": "输入单条交通事件文本，返回标准 JSON",
            "POST /batch_analyze": "输入多条交通事件文本，返回多条标准 JSON",
        },
    }


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/demo", response_class=FileResponse)
def demo() -> FileResponse:
    return FileResponse(BASE_DIR / "index.html")


@app.get("/index.html", response_class=FileResponse)
def index_page() -> FileResponse:
    return FileResponse(BASE_DIR / "index.html")


@app.post("/analyze")
def analyze(request: AnalyzeRequest) -> dict[str, Any]:
    try:
        return dict(pipeline.parse(request.text))
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/batch_analyze")
def batch_analyze(request: BatchAnalyzeRequest) -> list[dict[str, Any]]:
    if not request.texts:
        raise HTTPException(status_code=400, detail="输入文本列表不能为空")

    results: list[dict[str, Any]] = []
    for index, text in enumerate(request.texts):
        try:
            results.append(dict(pipeline.parse(text)))
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=f"第{index + 1}条文本错误：{exc}") from exc
    return results
