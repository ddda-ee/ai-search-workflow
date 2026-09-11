from typing import Optional
from models.query import QueryAnalysis
from storage.cache import SimpleJsonCache


class QueryAnalyzer:
    """关键词意图识别、消歧与中英双语学术检索词扩展器。"""

    def __init__(
        self,
        llm,
        cache: Optional[SimpleJsonCache] = None,
    ):
        self.llm = llm
        self.cache = cache

    def analyze(self, keyword: str, task_context: str) -> QueryAnalysis:
        cache_key = f"{keyword.strip().lower()}||{task_context.strip().lower()}"

        # 1. 尝试从缓存读取
        if self.cache:
            cached_data = self.cache.get("query_analysis", cache_key)
            if cached_data:
                print(f"  ⚡ [Cache Hit] QueryAnalyzer 命中本地缓存: '{keyword}'")
                return QueryAnalysis.model_validate(cached_data)

        # 2. 缓存未命中，调用 LLM
        system_prompt = (
            "你是一个顶级的科研与技术检索分析专家。\n"
            "你的任务是结合研究任务上下文，对输入的简短搜索关键词进行意图识别、消歧、概念对齐与中英双语专业学术术语转换。\n\n"
            "【输出要求】\n"
            "1. academic_queries_zh: 针对中文学术数据库（知网、万方等），生成 2-3 个规范的中文学术专业词。\n"
            "2. academic_queries_en: 针对国际英文学术数据库（arXiv、Semantic Scholar、OpenAlex 等），生成 2-3 个精准的纯英文专业学术检索词。\n"
            "3. web_queries: 生成 2-3 个适合通用搜索引擎（SearXNG）的带上下文限定的复合查询词。\n"
            "4. 无论输入是中文还是英文，academic_queries_zh 必须为高质量中文学术词，academic_queries_en 必须为纯英文学术词。"
        )

        user_prompt = (
            f"【研究任务上下文】\n{task_context}\n\n"
            f"【待分析关键词】\n{keyword}\n\n"
            f"请针对该关键词生成消歧与中英双语学术检索分析。"
        )

        schema = QueryAnalysis.model_json_schema()

        data = self.llm.generate_structured(
            stage="query_analyzer",
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            schema=schema,
            schema_name="QueryAnalysis",
        )

        analysis = QueryAnalysis.model_validate(data)

        # 3. 写入缓存
        if self.cache:
            self.cache.set("query_analysis", cache_key, analysis.model_dump())

        return analysis