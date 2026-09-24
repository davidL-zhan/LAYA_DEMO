# 仓库指南

## 项目结构与模块组织

- `main.py` 是 FastAPI 应用入口，提供首页、`/api/match` 和本地启动函数 `main()`。
- `config.py` 使用 `pydantic-settings` 定义服务及 Laya Router 的类型化配置；`.env.example` 是本地配置模板。
- `matching.py` 负责清理题目/知识点输入、构造 Laya `noul` 判断并保留原始响应。
- `templates/index.html` 是网页模板；`static/app.js` 和 `static/style.css` 分别负责交互与样式。
- `pyproject.toml` 保存项目元数据、Python 版本要求（`>=3.13`）、`laya[serve]==0.3.20`、`pydantic-settings` 和 `torch==2.14.0` 依赖；`uv.lock` 锁定依赖版本及平台对应的 PyTorch 构建。
- `README.md` 说明 Windows/macOS 安装、启动、端口设置、模型下载和网页操作。
- `.python-version` 将本地解释器版本系列指定为 Python 3.13。
- `tests/` 使用 Python 标准库 `unittest` 检查输入清理、知识点映射和单次 Router 调用。

## 构建、测试与开发命令

在 Windows 上使用 PowerShell 7，并采用 UTF-8 编码；macOS 可在终端使用相同的 `uv` 命令。

Windows/Linux 从 PyTorch CUDA 12.6 索引安装 PyTorch；macOS 使用 PyPI 构建，不安装 CUDA。改动依赖后更新并检查 `uv.lock`，不要手工编辑锁文件。

```powershell
uv sync --locked                         # 按锁文件安装项目及依赖
uv run python main.py                    # 启动网页；默认自动分配本机端口
uv run python -X utf8 -m unittest discover -s tests -v  # 运行单元测试
uv run python -X utf8 -m py_compile config.py main.py matching.py  # 检查 Python 语法
node --check static/app.js               # 可选：检查网页脚本语法
```

启动后使用 Uvicorn 日志显示的访问地址。服务和 Laya 设置使用 `LAYA_DEMO_` 前缀，可写在项目根目录 UTF-8 编码的 `.env` 中；非空操作系统环境变量优先，空值会忽略。`LAYA_DEMO_DEVICE` 留空或设为 `none` 表示自动选择设备；需用自动选择覆盖 `.env` 时显式设为 `none`。新增依赖应写入 `pyproject.toml` 并更新 `uv.lock`。

## 编码风格与命名约定

遵循标准 Python 风格：使用四个空格缩进，不使用制表符；函数和变量使用 `snake_case`，类使用 `PascalCase`，名称应清晰具体。在 `main.py` 中保留可执行入口保护。当前未配置格式化工具或代码检查器，因此修改应符合 PEP 8，并手动检查差异。

## 测试规范

测试使用 Python 标准库 `unittest`，文件名为 `tests/test_*.py`，聚焦可观察行为；配置测试覆盖 `.env`、环境变量优先级、自动设备选择和端口范围。修改后运行上面的完整单元测试命令，并在变更说明中报告命令和结果；网页交互变化还应检查桌面/窄屏布局、文本安全和错误恢复。

## 提交与拉取请求规范

仓库目前没有提交历史，因此无法推断既有提交信息规范。请使用简短、祈使式的主题，例如 `添加初始命令行行为` 或 `补充本地设置文档`。拉取请求应说明目的、列出重要变更文件、附上验证命令及结果，并在有相关问题单时提供链接。只有未来涉及界面的变更才需要截图。

## 安全与配置提示

不要提交密钥、本地凭据、生成的缓存或 `.venv/`。`.env` 和 `.env.*` 本地文件由 `.gitignore` 忽略，`.env.example` 是唯一保留的模板例外，不得在模板中放入秘密。新增运行时配置时，应使用有文档说明的 `LAYA_DEMO_` 环境变量；新增生成文件时，同时更新 `.gitignore`。

## Agent 专用说明

编辑前先检查仓库。源代码修改必须限定在明确要求的范围内；仅涉及文档的任务不得修改应用代码。请保持文本为 UTF-8，并保留用户已有的修改。
