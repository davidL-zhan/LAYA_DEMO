"""FastAPI entry point for the local exam knowledge-point matching demo."""

import logging
import os
from pathlib import Path
from typing import Any

import uvicorn
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from laya import Router
from pydantic import BaseModel

from matching import normalize_inputs, predict_matches


BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"
TEMPLATES_DIR = BASE_DIR / "templates"
logger = logging.getLogger(__name__)

app = FastAPI(title="考试题知识点匹配")
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
templates = Jinja2Templates(directory=TEMPLATES_DIR)

# Constructing Router does not load weights. The first prediction downloads and
# loads only the checkpoint selected for that request.
router = Router(default="multilingual", device=None, preload=False)


class MatchRequest(BaseModel):
    question: str
    knowledge_points: list[str]


@app.get("/", response_class=HTMLResponse)
async def index(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={},
    )


@app.post("/api/match")
def match(payload: MatchRequest) -> dict[str, Any]:
    try:
        question, knowledge_points = normalize_inputs(
            payload.question, payload.knowledge_points
        )
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    try:
        return predict_matches(router, question, knowledge_points)
    except Exception as exc:
        logger.exception("Laya checkpoint loading or prediction failed")
        raise HTTPException(
            status_code=503,
            detail="模型加载或推理失败，请检查 Hugging Face 网络连接后重试。",
        ) from exc


def main() -> None:
    port_text = os.environ.get("LAYA_DEMO_PORT", "0")
    try:
        port = int(port_text)
    except ValueError as exc:
        raise SystemExit("LAYA_DEMO_PORT 必须是 0 到 65535 之间的整数。") from exc
    if not 0 <= port <= 65535:
        raise SystemExit("LAYA_DEMO_PORT 必须是 0 到 65535 之间的整数。")

    # Port 0 asks the OS for an available port, avoiding local reserved ports.
    uvicorn.run(app, host="127.0.0.1", port=port)


if __name__ == "__main__":
    main()
