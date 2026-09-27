"""集中读取本地 Demo 的服务设置和 Laya 推理设置。"""

from pathlib import Path

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


# 以本文件所在目录定位项目根目录，避免从不同工作目录启动时找错 .env。
PROJECT_DIR = Path(__file__).resolve().parent


class Settings(BaseSettings):
    """从环境变量和项目根目录的 .env 加载并校验配置。

    变量统一使用 ``LAYA_DEMO_`` 前缀；运行进程中的环境变量优先于 .env，
    因而部署环境可以覆盖本地文件中的默认设置。
    """

    # 固定 .env 编码和路径，并忽略空环境变量与未知配置项。
    model_config = SettingsConfigDict(
        env_file=PROJECT_DIR / ".env",
        env_file_encoding="utf-8",
        env_prefix="LAYA_DEMO_",
        env_ignore_empty=True,
        extra="ignore",
    )

    # 默认仅监听本机；端口为 0 时交由操作系统分配可用端口。
    host: str = "127.0.0.1"
    port: int = Field(default=0, ge=0, le=65535)

    # Laya Router 的默认模型别名；device=None 表示由 Laya 自动选择设备。
    model_default: str = "multilingual"
    device: str | None = None

    # 默认延迟加载模型权重，避免仅启动网页时就触发模型下载或加载。
    preload: bool = False

    @field_validator("device", mode="before")
    @classmethod
    def auto_device_marker_means_none(cls, value: object) -> object:
        """把空字符串或文本 ``none`` 统一解释为设备自动选择。"""
        if isinstance(value, str) and value.strip().lower() in {"", "none"}:
            return None
        return value
