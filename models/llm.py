import json
import re

from openai import OpenAI

from config.settings import (
    LLM_API_KEY,
    LLM_BASE_URL,
    MODEL_NAME,
)


class LLMClient:
    """基于 OpenAI 兼容接口的大模型客户端。

    通过 base_url 适配 OpenAI、DeepSeek、Qwen、Moonshot、智谱、
    硅基流动等绝大多数提供 OpenAI 兼容接口的大模型服务。

    说明：LLMClient 是单模型版本，为兼容多模型路由接口，结构化生成方法
    额外接受可选的 stage 参数，但该参数在单模型模式下会被忽略。
    """

    def __init__(self):
        self.client = OpenAI(
            api_key=LLM_API_KEY,
            base_url=LLM_BASE_URL,
        )

    def generate(
        self,
        system_prompt: str,
        user_prompt: str,
    ) -> str:
        """调用大模型生成纯文本。"""
        response = self.client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        )

        content = response.choices[0].message.content
        return content or ""

    def generate_structured(
        self,
        system_prompt: str,
        user_prompt: str,
        schema: dict,
        schema_name: str,
        stage: str = "",
    ) -> dict:
        """调用大模型生成符合给定 JSON Schema 的结构化数据。

        参数 stage 仅为兼容多模型路由（LLMManager）的接口而保留，
        单模型模式下不使用该参数。

        为了兼容绝大多数 OpenAI 兼容服务，这里使用 json_object 模式，
        并把 schema 注入提示词；若服务端不支持 response_format，
        则自动降级为不带该参数的普通 JSON 请求。
        """
        schema_text = json.dumps(schema, ensure_ascii=False, indent=2)
        structured_prompt = (
            f"{user_prompt}\n\n"
            f"请严格按照下面的 JSON Schema（名称：{schema_name}）"
            f"输出一个合法的 JSON 对象，只输出 JSON，不要输出任何多余文字：\n"
            f"```json\n{schema_text}\n```"
        )

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": structured_prompt},
        ]

        response = self._chat_completion(messages)

        content = response.choices[0].message.content or ""
        return json.loads(self._extract_json(content))

    def _chat_completion(self, messages):
        """发起 chat.completions 请求，并对 response_format 做降级处理。"""
        try:
            return self.client.chat.completions.create(
                model=MODEL_NAME,
                messages=messages,
                response_format={"type": "json_object"},
            )
        except Exception as exc:
            # 部分服务不支持 response_format，去掉该参数再试一次
            error_text = str(exc).lower()
            if "response_format" in error_text or "json_object" in error_text:
                return self.client.chat.completions.create(
                    model=MODEL_NAME,
                    messages=messages,
                )
            raise

    @staticmethod
    def _extract_json(content: str) -> str:
        """从模型输出中提取 JSON 文本，兼容 markdown 代码块等包裹。"""
        text = content.strip()

        # 去掉 markdown 代码块包裹
        if text.startswith("```"):
            text = re.sub(r"^```[a-zA-Z]*\s*", "", text)
            text = re.sub(r"\s*```$", "", text).strip()

        # 若仍有额外文字，只取第一个完整 JSON 对象
        if not text.startswith("{"):
            match = re.search(r"\{.*\}", text, re.DOTALL)
            if match:
                text = match.group(0)

        return text