import os
import re
import json
import yaml
from pathlib import Path
from typing import Any, Dict, Optional
from openai import OpenAI
from dotenv import load_dotenv

# 自动加载根目录下的 .env 文件
load_dotenv()


class LLMManager:
    """多厂家大模型连接池与环节路由管理器。"""

    def __init__(self, config_path: str = "config/llm_config.yaml"):
        self.config_path = Path(config_path)
        self.providers: Dict[str, Dict[str, Any]] = {}
        self.stage_routing: Dict[str, Dict[str, str]] = {}
        self._clients: Dict[str, OpenAI] = {}

        self._load_config()

    def _resolve_env_vars(self, value: str) -> str:
        """解析 ${VAR_NAME} 格式的环境变量。"""
        pattern = re.compile(r"\$\{([^}^{]+)\}")
        matches = pattern.findall(value)
        for match in matches:
            env_val = os.getenv(match, "")
            value = value.replace(f"${{{match}}}", env_val)
        return value

    def _load_config(self):
        if not self.config_path.exists():
            raise FileNotFoundError(f"未找到配置文件: {self.config_path}")

        raw_text = self.config_path.read_text(encoding="utf-8")
        resolved_text = self._resolve_env_vars(raw_text)
        config = yaml.safe_load(resolved_text)

        self.providers = config.get("providers", {})
        self.stage_routing = config.get("stage_routing", {})

    def _get_client(self, provider_name: str) -> OpenAI:
        """获取或创建特定 Provider 的 SDK 客户端实例。"""
        if provider_name in self._clients:
            return self._clients[provider_name]

        if provider_name not in self.providers:
            raise ValueError(f"未在 providers 中配置该厂商: '{provider_name}'")

        cfg = self.providers[provider_name]
        api_key = cfg.get("api_key")
        base_url = cfg.get("base_url")

        if not api_key:
            raise ValueError(
                f"❌ Provider [{provider_name}] 缺少有效 API Key！\n"
                f"请检查项目根目录的 .env 文件中是否配置了对应的变量（如 DEEPSEEK_API_KEY）。"
            )

        client = OpenAI(api_key=api_key, base_url=base_url)
        self._clients[provider_name] = client
        return client

    def generate_structured(
        self,
        stage: str,
        system_prompt: str,
        user_prompt: str,
        schema: dict,
        schema_name: str,
    ) -> dict[str, Any]:
        """根据环节路由，自动寻找绑定的厂家与模型完成调用。"""
        route = self.stage_routing.get(stage)
        if not route:
            raise KeyError(f"未在 stage_routing 中配置环节: '{stage}'")

        provider_name = route["provider"]
        model_name = route["model"]
        client = self._get_client(provider_name)

        response = client.chat.completions.create(
            model=model_name,
            messages=[
                {
                    "role": "system",
                    "content": f"{system_prompt}\n\n请严格按以下 JSON Schema 输出规范的 JSON 对象，不得输出任何其他解释说明内容:\n{json.dumps(schema, ensure_ascii=False)}",
                },
                {"role": "user", "content": user_prompt},
            ],
            response_format={"type": "json_object"},
            temperature=0.2,
        )

        content = response.choices[0].message.content
        return json.loads(content)