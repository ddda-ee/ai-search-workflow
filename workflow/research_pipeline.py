from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Optional, Tuple

from models.research import (
    ResearchPlan,
    SearchTask,
    SearchResult,
    Document,
    Finding,
    FactCheckResult,
)
from models.llm import LLMClient
from tools.search.registry import SearchPluginRegistry
from tools.search.searxng import SearXNGPlugin
from tools.search.arxiv import ArxivPlugin
from tools.search.openalex import OpenAlexPlugin
from tools.search.semantic_scholar import SemanticScholarPlugin
from tools.search.crossref import CrossrefPlugin

from workflow.query_analyzer import QueryAnalyzer
from workflow.search_manager import SearchManager
from workflow.selector import GlobalSelector
from workflow.collector import Collector
from workflow.chunker import DocumentChunker
from workflow.analyzer import analyze_and_verify_document
from workflow.fact_checker import fact_check_finding
from storage.cache import SimpleJsonCache


class ResearchPipeline:

    def __init__(
        self,
        llm_client: Optional[LLMClient] = None,
        enabled_sources: Optional[List[str]] = None,
        max_global_documents: int = 8,
        chunk_size: int = 6000,
        chunk_overlap: int = 500,
        max_doc_workers: int = 4,
    ):
        self.llm = llm_client or LLMClient()
        self.cache = SimpleJsonCache()
        self.max_doc_workers = max_doc_workers

        # 1. 注册插件系统
        self.registry = SearchPluginRegistry()
        self.registry.register(SearXNGPlugin())
        self.registry.register(ArxivPlugin())
        self.registry.register(OpenAlexPlugin())
        self.registry.register(SemanticScholarPlugin())
        self.registry.register(CrossrefPlugin())

        # 2. 搜索调度层
        sources = enabled_sources or ["searxng", "arxiv", "openalex", "semantic_scholar", "crossref"]
        self.query_analyzer = QueryAnalyzer(self.llm, cache=self.cache)
        self.search_manager = SearchManager(
            registry=self.registry,
            enabled_sources=sources,
            query_analyzer=self.query_analyzer,
            cache=self.cache,
            max_workers=5,
        )

        # 3. 筛选、抓取与分块
        self.selector = GlobalSelector(max_global_documents=max_global_documents)
        self.collector = Collector(max_workers=5)
        self.chunker = DocumentChunker(chunk_size=chunk_size, overlap=chunk_overlap)

    def _analyze_and_verify_single(
        self,
        doc: Document
    ) -> Tuple[Finding, FactCheckResult]:
        """单篇文档处理：信息提取 -> RAG 局部切片核查。"""
        
        # 1. 抽取核心内容
        finding, fact_check = analyze_and_verify_document(doc, llm=self.llm)
        
        # 2. 对关键论点执行局部精准核验 
        verified_fact_check = fact_check_finding(doc, finding, llm=self.llm)
        
        supported = sum(1 for e in verified_fact_check.evidences if e.supported)
        print(f"  ✓ [{doc.source}] {doc.title[:26]}... (证据支持: {supported}/{len(verified_fact_check.evidences)})")
        return finding, verified_fact_check

    def run(
        self,
        tasks: List[SearchTask],
        plan: Optional[ResearchPlan] = None,
        max_results_per_plugin: int = 3,
    ) -> tuple[List[Document], List[Finding], List[FactCheckResult]]:

        # 阶段 3：并行执行搜索
        print("\n" + "=" * 60)
        print(f"阶段 3：并发执行 {len(tasks)} 个搜索任务")
        print("=" * 60)

        all_raw_results: List[SearchResult] = self.search_manager.search_tasks_parallel(
            tasks=tasks,
            max_results_per_plugin=max_results_per_plugin,
            task_workers=2
        )
        print(f"\n>>> 搜索完成，多源累计收集候选条目: {len(all_raw_results)} 条")

        # 阶段 4：全局去重与打分筛选
        print("\n" + "=" * 60)
        print("阶段 4：全局文献去重与权威度筛选")
        print("=" * 60)

        selected_results = self.selector.select_global(
            all_results=all_raw_results,
            plan=plan,
            tasks=tasks,
        )
        print(f"筛选完成：{len(all_raw_results)} -> 保留核心文献 {len(selected_results)} 篇:")
        for idx, item in enumerate(selected_results, 1):
            print(f"  ✓ [{idx}] ({item.source}) {item.title}")

        if not selected_results:
            raise RuntimeError("筛选后可用资料为空，流程中止。")

        # 阶段 5：并发正文抓取
        print("\n" + "=" * 60)
        print(f"阶段 5：并发正文抓取 ({len(selected_results)} 篇)")
        print("=" * 60)

        documents = self.collector.collect(selected_results)
        print(f"\n成功抓取正文: {len(documents)} 篇")

        # 阶段 6：并发分析与事实核查
        print("\n" + "=" * 60)
        print(f"阶段 6：并发文档分析与事实核查 (并行度: {self.max_doc_workers})")
        print("=" * 60)

        findings: List[Finding] = []
        fact_checks: List[FactCheckResult] = []

        with ThreadPoolExecutor(max_workers=self.max_doc_workers) as executor:
            futures = [
                executor.submit(self._analyze_and_verify_single, doc)
                for doc in documents
            ]
            for future in as_completed(futures):
                try:
                    finding, fact_check = future.result()
                    findings.append(finding)
                    fact_checks.append(fact_check)
                except Exception as exc:
                    print(f"⚠ 文档分析核查异常: {exc}")

        return documents, findings, fact_checks