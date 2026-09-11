from typing import Optional, List
from models.llm_manager import LLMManager
from models.research import (
    Document,
    Finding,
    Evidence,
    FactCheckResult,
    fact_check_schema,
)
from prompts.system import SYSTEM_PROMPT
from tools.text_matcher import SimpleSnippetMatcher


def fact_check_finding(
    document: Document,
    finding: Finding,
    llm: LLMManager,
) -> FactCheckResult:
    """RAG 风格的局部证据切片核查，长文本消耗降低 80%"""

    # 1. 整理待核验的断言清单
    claims = []
    claims.extend(finding.key_points)
    claims.extend(finding.methods)
    claims.extend(finding.findings)
    claims.extend(finding.limitations)
    claims = list(dict.fromkeys(claims))  # 去重

    if not claims:
        return FactCheckResult(
            document_title=document.title,
            document_url=document.url,
            evidences=[],
        )

    # 2. 如果文档篇幅极短（<= 2500 字），直接全文送入
    if len(document.content) <= 2500:
        context_text = document.content
    else:
        # 3. 长篇全文切片检索：对每条 Claim 定位 Top 2 最匹配正文段落
        chunks = SimpleSnippetMatcher.chunk_document(document.content, chunk_size=700, overlap=100)
        selected_snippets = set()

        for claim in claims:
            snippets = SimpleSnippetMatcher.find_relevant_snippets(claim, chunks, top_k=2)
            selected_snippets.update(snippets)

        # 限制最大注入段落数，防止超长
        context_text = "\n\n---\n\n".join(list(selected_snippets)[:10])

    claims_text = "\n".join(f"{i}. {claim}" for i, claim in enumerate(claims, 1))

    prompt = f"""
你是一名严谨的学术事实核查专家。
请核对以下主张是否在给定的论文/资料证据片段中有据可依。

资料标题：{document.title}
参考正文片段（通过相关性检索截取）：
{context_text}

待核验陈述：
{claims_text}

核查准则：
1. 只能依据上述正文片段裁定。
2. 若片段支持或语义完全一致，supported 填 true；若未提及或存在矛盾，supported 填 false。
3. evidence 必须精准引用片段中的关键原句，严禁自行发挥想象补充。
"""

    data = llm.generate_structured(
        stage="fact_checker",
        system_prompt=SYSTEM_PROMPT,
        user_prompt=prompt,
        schema=fact_check_schema(),
        schema_name="fact_check",
    )

    return FactCheckResult(**data)