from typing import List, Optional
from models.llm_manager import LLMManager
from models.research import (
    ResearchPlan,
    Finding,
    FactCheckResult,
    ResearchReport,
    ReviewResult,
    research_report_schema,
)
from prompts.system import SYSTEM_PROMPT


def synthesize_report(
    research_plan: ResearchPlan,
    findings: List[Finding],
    fact_checks: List[FactCheckResult],
    llm: LLMManager,
) -> ResearchReport:
    """初次合成研究报告。"""
    # 提取事实核查中被有效支持的事实证据
    supported_evidences = []
    for fc in fact_checks:
        for ev in fc.evidences:
            if ev.supported:
                supported_evidences.append(f"[{fc.document_title}] {ev.claim} (凭证: {ev.evidence})")

    user_prompt = f"""
你是一名顶级的学术研究报告撰写专家。
请根据以下经过核实的技术事实与研究计划，撰写一份详尽、专业、严谨的技术综述报告。

【研究目标】
{research_plan.research_goal}

【核心技术路线】
{', '.join(research_plan.technology_routes)}

【经事实核验的技术证据清单】
{chr(10).join(supported_evidences[:30])}

【输出规范】
1. 结构完整，包含背景、现状、方法、发现、对比、局限、未来方向等。
2. 论点必须严格建立在事实证据之上，不得随意脑补。
3. references 字段必须列出实际引用的完整 URL。
"""

    data = llm.generate_structured(
        stage="synthesizer",
        system_prompt=SYSTEM_PROMPT,
        user_prompt=user_prompt,
        schema=research_report_schema(),
        schema_name="research_report",
    )
    return ResearchReport(**data)


def refine_report(
    original_report: ResearchReport,
    review: ReviewResult,
    fact_checks: List[FactCheckResult],
    llm: LLMManager,
) -> ResearchReport:
    """根据审稿专家的修改意见实施针对性反思修正（Self-Correction）。"""
    
    issues_text = "\n".join(f"- {issue}" for issue in review.issues)
    suggestions_text = "\n".join(f"- {sug}" for sug in review.suggestions)

    # 补充有效参考源，防止引用链条断裂
    valid_sources = list({fc.document_url for fc in fact_checks if fc.document_url})

    user_prompt = f"""
你是一名顶级的学术报告修订专家。
你之前起草的报告在同行评审阶段被驳回或提出了重要修改建议。请根据审稿专家的意见，对报告进行全面修正与精炼。

【审稿指出的缺陷】
{issues_text}

【审稿专家的修改建议】
{suggestions_text}

【合法可用的参考来源 (URL)】
{chr(10).join(valid_sources)}

【原报告草稿内容】
{original_report.model_dump_json(indent=2, ensure_ascii=False)}

【修订执行要求】
1. 逐条对应并解决审稿意见中的所有缺陷。
2. 剔除或重写缺乏事实依据的主张，纠正引用与正文不一致的缺陷。
3. 确保输出的结构完全符合规范，保持专业客观的学术口吻。
"""

    data = llm.generate_structured(
        stage="synthesizer",
        system_prompt=SYSTEM_PROMPT,
        user_prompt=user_prompt,
        schema=research_report_schema(),
        schema_name="refined_research_report",
    )
    return ResearchReport(**data)