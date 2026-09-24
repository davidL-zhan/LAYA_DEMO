# `.env` 与 `config.py` 配置管理设计

## 目标

将服务运行参数和 Laya Router 参数集中到类型化配置对象中，由项目根目录的 UTF-8 `.env` 文件或操作系统环境变量提供值。保留当前行为作为默认值，不改变网页匹配逻辑、请求/响应格式或模型推理语义。

## 配置范围

配置项统一使用 `LAYA_DEMO_` 前缀：

| 设置 | 环境变量 | 默认值 | 说明 |
| --- | --- | --- | --- |
| 服务地址 | `LAYA_DEMO_HOST` | `127.0.0.1` | 默认只监听本机回环地址 |
| 服务端口 | `LAYA_DEMO_PORT` | `0` | `0` 表示由操作系统分配；允许范围 `0`–`65535` |
| Laya 默认模型 | `LAYA_DEMO_MODEL_DEFAULT` | `multilingual` | 传给 `Router(default=...)` |
| Laya 设备 | `LAYA_DEMO_DEVICE` | `none` | `none` 表示交由 Laya/PyTorch 自动选择；也可显式指定设备 |
| 预加载 | `LAYA_DEMO_PRELOAD` | `false` | 传给 `Router(preload=...)` |

匹配阈值继续由网页滑块管理，不进入后端配置。当前公开模型无需 Hugging Face token，因此本次不增加 token 配置字段。

## 方案与模块

采用 `pydantic-settings`：利用项目已有的 Pydantic 生态，将 `.env` 与系统环境变量解析为有类型的字段，并在启动时校验端口范围。相比手写 `python-dotenv`/`dataclass` 转换，可减少重复解析和校验逻辑。

- `config.py` 定义 `Settings`，以代码文件所在的项目根目录定位 `.env`，使用 UTF-8；操作系统环境变量覆盖 `.env` 中的同名项。
- `.env.example` 提供无密钥的默认配置模板；真实 `.env` 加入 `.gitignore`，由开发者从模板复制后本地编辑。
- `main.py` 从 `Settings` 读取服务 host/port 和 Laya Router 参数，移除直接读取 `os.environ` 的分散逻辑。
- `pyproject.toml` 声明 `pydantic-settings`，`uv.lock` 由 `uv lock` 更新。
- `README.md` 说明复制模板、可配置变量和本地启动；`AGENTS.md` 更新结构与命令约定。

## 错误处理与安全

无 `.env` 文件时使用代码默认值，不影响现有启动方式。非法端口等配置在启动阶段报出配置校验错误。默认 host 仍为 `127.0.0.1`；如果用户显式改为 `0.0.0.0`，服务会监听所有网卡，文档需提示其网络暴露风险。`.env` 不提交到 Git，模板不得包含凭据。

## 测试与验收

新增配置测试覆盖默认值、UTF-8 `.env` 读取、进程环境变量覆盖文件值、端口边界和非法值。现有匹配业务测试应保持通过。静态检查不启动服务器、不下载 Laya 模型，也不运行重量级依赖同步。

验收标准：

1. 未创建 `.env` 时，应用仍以原来的默认值启动。
2. 修改 `.env` 可调整 host、port 和 Laya Router 的模型/设备/预加载参数。
3. 同名进程环境变量优先于 `.env`。
4. `.env` 被忽略，`.env.example` 可提交且不包含秘密。
5. 配置测试和既有业务测试通过，README 与 AGENTS.md 描述与实现一致。
