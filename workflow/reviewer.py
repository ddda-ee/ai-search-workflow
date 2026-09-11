from models.research import (
    ResearchReport,
    ReviewResult,
    review_result_schema,
)

from prompts.system import SYSTEM_PROMPT


def review_report(
    report: ResearchReport,
    llm,
) -> ReviewResult:

    report_text = report.model_dump_json(
        indent=2,
        ensure_ascii=False
    )

    prompt = f"""
你是一名非常严格的科研报告审稿专家。

请审查下面这份科研研究报告。

研究报告：

{report_text}

请重点检查：

1. 是否存在明显的事实错误。
2. 是否存在没有证据支持的结论。
3. 是否存在把推断写成事实的情况。
4. 是否存在逻辑矛盾。
5. 是否存在重复内容。
6. 是否遗漏研究计划中的重要问题。
7. 是否存在虚构论文、数据、来源或实验结果。
8. references 是否与报告内容一致。
9. research_gaps 是否有足够依据。
10. future_directions 是否属于合理推导，而不是凭空提出。

判断标准：

- 如果存在严重问题，passed=false。
- 如果只有轻微表达问题，但不影响事实准确性，可以 passed=true。
- 不要为了挑问题而制造不存在的问题。
- 只根据提供的报告进行审查。
"""

    data = llm.generate_structured(
        stage="reviewer",
        system_prompt=SYSTEM_PROMPT,
        user_prompt=prompt,
        schema=review_result_schema(),
        schema_name="review_result",
    )

    return ReviewResult(**data)