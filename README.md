# Laya 考试题知识点匹配 Demo

在本地网页中输入一道考试题和若干知识点，让 Laya 分别判断解题是否需要每个知识点。结果按阈值显示“匹配 / 不匹配”和概率，同时可以展开查看 Laya 返回的原始结构化 JSON。

项目在 Windows 和 Linux 上使用 PyTorch 2.14.0 的 CUDA 12.6 构建；macOS 使用 PyPI 上的 PyTorch 构建，不安装 CUDA（Apple Silicon 可由 PyTorch 使用 MPS）。

## 环境与启动

需要 Python 3.13 或更高版本，以及 `uv`。在项目根目录运行：

```shell
uv sync --locked
uv run python main.py
```

Windows PowerShell 7 和 macOS 终端使用相同的启动命令。默认由操作系统分配一个可用端口，启动日志会打印实际访问地址；在本机浏览器打开该地址即可。服务只监听本机回环地址，不对局域网开放。

首次使用时可从模板创建本地配置文件：

```powershell
# Windows PowerShell 7
Copy-Item .env.example .env
```

```shell
# macOS / Linux
cp .env.example .env
```

然后按需编辑 `.env`。所有配置项都可省略，默认值如下：

| 环境变量 | 默认值 | 说明 |
| --- | --- | --- |
| `LAYA_DEMO_HOST` | `127.0.0.1` | 服务监听地址；默认仅本机可访问。改为 `0.0.0.0` 会监听所有网卡，可能向局域网或其他网络暴露服务。 |
| `LAYA_DEMO_PORT` | `0` | `0` 由操作系统分配可用端口；也可指定 `1`–`65535`。 |
| `LAYA_DEMO_MODEL_DEFAULT` | `multilingual` | 传给 Laya Router 的默认模型。 |
| `LAYA_DEMO_DEVICE` | 空（自动选择） | 留空时由 Laya/PyTorch 自动选择设备；也可按 Laya 支持的设备值显式指定。 |
| `LAYA_DEMO_PRELOAD` | `false` | 是否在启动时预加载 Laya 模型；默认首次预测时再加载。 |

操作系统环境变量优先于 `.env` 中的同名配置。例如，PowerShell 中设置 `$env:LAYA_DEMO_PORT = "6410"`，或在 macOS/Linux 中运行 `LAYA_DEMO_PORT=6410 uv run python main.py`，可临时覆盖文件值。`.env` 是本地文件，不会提交到 Git。

## 使用方式

1. 在“考试题目”中临时输入一道题。
2. 在“知识点”中每行输入一个概念；空行会被忽略，重复项会保留。
3. 提交后，页面对每个知识点显示 Laya 的 `noul` 是/否概率，并用滑块阈值决定“匹配”或“不匹配”。阈值默认是 60%，调整阈值只会在浏览器本地重算状态，不会再次调用模型。
4. 展开“查看 Laya 原始 JSON”查看模型未经改写的结构化返回值。

## 模型下载与设备

服务启动时不会加载模型。首次提交预测时，Laya 才会从 Hugging Face 下载本次路由需要的 checkpoint；之后由 Hugging Face 缓存在本机复用。首次预测需要能访问 Hugging Face，耗时会比后续预测更长。

应用使用 `Router(default="multilingual", device=None, preload=False)`。Laya 不是通用文本相似度/embedding 工具，而是对每个知识点提出一个 `noul` 是/否判断；Router 会在英文 ModernBERT checkpoint 和多语言 mmBERT checkpoint 间路由，中文通常使用多语言模型。`device=None` 交由 Laya/PyTorch 在 CUDA、Apple MPS、XPU 或 CPU 中选择可用设备。模型支持的语言和匹配效果仍应使用你的真实考试题目验证；概率是模型分数，不代表经过本项目数据校准的置信度。

Windows/Linux 使用 CUDA 需要可用的 NVIDIA GPU 和兼容的驱动。可用下面的命令检查 PyTorch 是否检测到 CUDA：

```shell
uv run python -c "import torch; print(torch.__version__, torch.version.cuda, torch.cuda.is_available())"
```

## 验证

```shell
uv run python -X utf8 -m unittest discover -s tests -v
```
