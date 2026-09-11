# 内置的大模型服务商预设。
# 这里的服务商都提供 OpenAI 兼容接口，通过 OpenAI SDK 即可调用。
# 想新增服务商，只需要在这里加一条配置。

PROVIDERS = [
    {
        "key": "openai",
        "name": "OpenAI",
        "base_url": "https://api.openai.com/v1",
        "api_key_env": "OPENAI_API_KEY",
        "default_models": ["gpt-4o", "gpt-4o-mini", "gpt-4.1", "o3-mini"],
    },
    {
        "key": "deepseek",
        "name": "DeepSeek",
        "base_url": "https://api.deepseek.com/v1",
        "api_key_env": "DEEPSEEK_API_KEY",
        "default_models": ["deepseek-chat", "deepseek-reasoner"],
    },
    {
        "key": "qwen",
        "name": "通义千问 Qwen",
        "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
        "api_key_env": "QWEN_API_KEY",
        "default_models": ["qwen-plus", "qwen-turbo", "qwen-max"],
    },
    {
        "key": "moonshot",
        "name": "Moonshot / Kimi",
        "base_url": "https://api.moonshot.cn/v1",
        "api_key_env": "MOONSHOT_API_KEY",
        "default_models": ["moonshot-v1-8k", "moonshot-v1-32k", "moonshot-v1-128k"],
    },
    {
        "key": "zhipu",
        "name": "智谱 GLM",
        "base_url": "https://open.bigmodel.cn/api/paas/v4",
        "api_key_env": "ZHIPU_API_KEY",
        "default_models": ["glm-4-plus", "glm-4-air", "glm-4-flash"],
    },
    {
        "key": "siliconflow",
        "name": "硅基流动 SiliconFlow",
        "base_url": "https://api.siliconflow.cn/v1",
        "api_key_env": "SILICONFLOW_API_KEY",
        "default_models": [],
    },
    {
        "key": "openrouter",
        "name": "OpenRouter",
        "base_url": "https://openrouter.ai/api/v1",
        "api_key_env": "OPENROUTER_API_KEY",
        "default_models": [],
    },
    {
        "key": "ollama",
        "name": "Ollama（本地）",
        "base_url": "http://localhost:11434/v1",
        "api_key_env": None,
        "default_models": ["llama3", "qwen2.5"],
    },
    {
        "key": "custom",
        "name": "自定义 OpenAI 兼容接口",
        "base_url": None,
        "api_key_env": "LLM_API_KEY",
        "default_models": [],
    },
]


PROVIDER_MAP = {item["key"]: item for item in PROVIDERS}