from models.llm_manager import LLMManager

from prompts.system import SYSTEM_PROMPT
from prompts.scientific import SCIENTIFIC_PROMPT
from prompts.market import MARKET_PROMPT

from models.research import (
    ResearchPlan,
    research_plan_schema,
)


def create_research_plan(
    user_request: str,
    research_type: str,
    llm: LLMManager
) -> ResearchPlan:

    if research_type == "scientific":
        domain_prompt = SCIENTIFIC_PROMPT
    elif research_type == "market":
        domain_prompt = MARKET_PROMPT
    else:
        raise ValueError(f"不支持的研究类型: {research_type}")

    prompt = f"""
{domain_prompt}

现在请根据用户的研究需求，制定研究计划。

用户研究需求：

{user_request}

请完成：

1. 明确研究目标
2. 拆分核心研究问题
3. 拆分子问题
4. 生成中文搜索关键词
5. 生成英文搜索关键词
6. 梳理可能的技术路线
7. 推荐需要重点搜索的资料类型
"""

    data = llm.generate_structured(
        stage="planner",
        system_prompt=SYSTEM_PROMPT,
        user_prompt=prompt,
        schema=research_plan_schema(),
        schema_name="research_plan",
    )

    return ResearchPlan(**data)