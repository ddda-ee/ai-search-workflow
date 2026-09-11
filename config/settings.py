import os
from dotenv import load_dotenv

from config.providers import PROVIDER_MAP


load_dotenv()


# =========================
# LLM 通用配置
# =========================

LLM_PROVIDER = (os.getenv("LLM_PROVIDER") or "").strip().lower()

if not LLM_PROVIDER:
    raise ValueError("LLM_PROVIDER 未设置，请检查 .env 文件")

MODEL_NAME = (os.getenv("MODEL_NAME") or "").strip()

if not MODEL_NAME:
    raise ValueError("MODEL_NAME 未设置，请检查 .env 文件")


# =========================
# 按 Provider 解析 base_url 与 API Key
# =========================

_provider = PROVIDER_MAP.get(LLM_PROVIDER)

# 优先使用显式配置，未配置时回退到预设默认值。
# 通过 LLM_BASE_URL + LLM_API_KEY 可以接入任意 OpenAI 兼容的大模型服务。
LLM_BASE_URL = os.getenv("LLM_BASE_URL") or (
    _provider["base_url"] if _provider else None
)

LLM_API_KEY = os.getenv("LLM_API_KEY") or (
    os.getenv(_provider["api_key_env"]) if _provider and _provider.get("api_key_env") else None
)

# 本地服务（如 Ollama）通常不需要 API Key，给个占位值避免报错
if not LLM_API_KEY and _provider and not _provider.get("api_key_env"):
    LLM_API_KEY = "local"

# 未识别的 provider 必须显式配置 base_url，以支持任意 OpenAI 兼容服务
if not LLM_BASE_URL:
    raise ValueError(
        f"暂不支持的 LLM Provider: {LLM_PROVIDER}，"
        f"请在 .env 中设置 LLM_BASE_URL（任意 OpenAI 兼容接口）"
    )

if not LLM_API_KEY:
    raise ValueError(f"{LLM_PROVIDER} 的 API Key 未设置，请检查 .env 文件")


# =========================
# 向后兼容：保留常用 Provider 的 API Key 变量
# =========================

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
QWEN_API_KEY = os.getenv("QWEN_API_KEY")