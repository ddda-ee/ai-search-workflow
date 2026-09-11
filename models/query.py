from typing import List
from pydantic import BaseModel, Field


class QueryAnalysis(BaseModel):
    original_query: str = Field(description="原始关键词")
    normalized_query: str = Field(description="规范化清洗后的关键词")
    intent: str = Field(description="搜索意图，如 academic_research, tech_spec")
    domain: str = Field(description="所属领域，例如 computer_vision")
    entities: List[str] = Field(default_factory=list, description="核心实体词")
    concepts: List[str] = Field(default_factory=list, description="相关概念或完整学术全称")
    is_ambiguous: bool = Field(description="是否存在歧义")
    context_terms: List[str] = Field(default_factory=list, description="补充的上下文约束限定词")

    web_queries: List[str] = Field(
        default_factory=list,
        description="通用 Web 搜索引擎查询词（包含上下文消歧词）"
    )
    academic_queries_zh: List[str] = Field(
        default_factory=list,
        description="针对中文学术源（如知网、万方、维普）的标准专业学术检索词（规范中文术语）"
    )
    academic_queries_en: List[str] = Field(
        default_factory=list,
        description="针对国际英文学术源（如 arXiv、Semantic Scholar、OpenAlex）的标准英文学术检索词（纯英文学术术语）"
    )
    confidence: float = Field(ge=0.0, le=1.0, description="置信度 0-1")