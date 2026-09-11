from typing import List

from models.llm_manager import LLMManager
from models.research import (
    ResearchPlan,
    SearchTask,
    search_task_schema,
)

from prompts.system import SYSTEM_PROMPT


def generate_search_tasks(
    research_plan: ResearchPlan,
    llm: LLMManager
) -> List[SearchTask]:

    research_plan_text = research_plan.model_dump_json(
        indent=2,
        ensure_ascii=False
    )

    prompt = f"""
你是一名专业的科研与市场研究搜索规划专家。

现在需要根据下面的 ResearchPlan，
将研究计划拆分成可以实际执行的搜索任务。

ResearchPlan：

{research_plan_text}

请遵守以下要求：

1. 每个搜索任务必须对应一个明确的问题。

2. 一个搜索任务应该能够通过搜索网页、
论文、报告或其他资料得到答案。

3. 不要生成重复的搜索任务。

4. 搜索关键词应该尽可能具体。

5. 科研调研优先考虑：
   - 学术论文
   - 会议论文
   - 期刊
   - arXiv
   - 官方项目
   - GitHub
   - 专利

6. 市场调研优先考虑：
   - 公司官网
   - 财报
   - 政府统计
   - 行业报告
   - 权威媒体

7. 对重要问题设置 high 优先级。

8. 每个任务必须说明搜索目的。

9. 最终生成多个 SearchTask。
"""

    data = llm.generate_structured(
        stage="search_task_generator",
        system_prompt=SYSTEM_PROMPT,
        user_prompt=prompt,
        schema=search_task_schema(),
        schema_name="search_tasks",
    )

    return [
        SearchTask(**task)
        for task in data["tasks"]
    ]