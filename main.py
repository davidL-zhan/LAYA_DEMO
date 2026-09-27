"""本地考试题知识点匹配 Demo 的 FastAPI 应用入口。

该模块负责网页路由、API 请求校验和 Laya Router 的生命周期；具体输入清理与
知识点问题构造放在 ``matching.py``，便于独立测试和理解。
"""

import logging
from pathlib import Path
from typing import Any

import uvicorn
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from laya import Router
from pydantic import BaseModel

from config import Settings
from matching import normalize_inputs, predict_matches


# 静态资源和模板都相对于项目目录定位，不依赖启动命令所在的当前目录。
BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"
TEMPLATES_DIR = BASE_DIR / "templates"
logger = logging.getLogger(__name__)

# 配置在应用导入时读取一次，服务与 Router 后续共用同一份设置。
settings = Settings()

# 页面入口、静态文件和 API 都由同一个 FastAPI 应用提供。
app = FastAPI(title="考试题知识点匹配")
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
templates = Jinja2Templates(directory=TEMPLATES_DIR)

# Router 在应用启动时创建一次，避免每个请求重复初始化路由器。
# 是否立即加载模型权重由配置控制；默认等到第一次预测时再加载检查点。
router = Router(
    default=settings.model_default,
    device=settings.device,
    preload=settings.preload,
)


class MatchRequest(BaseModel):
    """一次临时分析的输入：题目正文及用户本次提交的候选知识点。"""

    question: str
    knowledge_points: list[str]


@app.get("/", response_class=HTMLResponse)
async def index(request: Request) -> HTMLResponse:
    """渲染交互页面；模板由 Starlette 根据请求上下文生成 HTML。"""
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={},
    )


@app.post("/api/match")
def match(payload: MatchRequest) -> dict[str, Any]:
    """执行一轮匹配并返回 Laya 原始结果及知识点映射信息。

    这是同步路由，因为模型预测是阻塞调用；FastAPI 会在线程池中运行同步
    路由，避免把阻塞推理直接放在异步事件循环里。
    """
    try:
        # 在调用模型前清理首尾空白，并把空题目或空知识点列表转成 422。
        question, knowledge_points = normalize_inputs(
            payload.question, payload.knowledge_points
        )
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    try:
        # raw_result 保留 Laya 的结构化输出，前端再据此展示逐知识点概率。
        return predict_matches(router, question, knowledge_points)
    except Exception as exc:
        # 详细异常留在服务日志中；响应只给出适合用户阅读的提示。
        logger.exception("Laya checkpoint loading or prediction failed")
        raise HTTPException(
            status_code=503,
            detail="模型加载或推理失败，请检查 Hugging Face 网络连接后重试。",
        ) from exc


def main() -> None:
    """按 .env / 环境变量中的地址和端口启动本地 ASGI 服务。"""
    # 端口 0 表示让操作系统挑选可用端口，避免撞上已占用端口。
    uvicorn.run(app, host=settings.host, port=settings.port)


if __name__ == "__main__":
    main()
