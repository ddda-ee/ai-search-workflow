from models.llm import LLMClient
from models.research import SearchTask
from tools.search.registry import SearchPluginRegistry
from tools.search.searxng import SearXNGPlugin
from tools.search.arxiv import ArxivPlugin
from tools.search.openalex import OpenAlexPlugin
from tools.search.semantic_scholar import SemanticScholarPlugin
from tools.search.crossref import CrossrefPlugin
from workflow.query_analyzer import QueryAnalyzer
from workflow.search_manager import SearchManager


def test_all_plugins():
    print("=" * 60)
    print("🚀 测试全学术源 (SearXNG + arXiv + OpenAlex + Semantic Scholar + Crossref)")
    print("=" * 60)

    # 1. 注册所有学术源
    registry = SearchPluginRegistry()
    registry.register(SearXNGPlugin())
    registry.register(ArxivPlugin())
    registry.register(OpenAlexPlugin())
    registry.register(SemanticScholarPlugin())
    registry.register(CrossrefPlugin())

    print(f"已注册插件: {registry.names()}")

    # 2. 启用全部学术插件
    llm = LLMClient()
    analyzer = QueryAnalyzer(llm)
    manager = SearchManager(
        registry=registry,
        enabled_sources=[
            "searxng",
            "arxiv",
            "openalex",
            "semantic_scholar",
            "crossref"
        ],
        query_analyzer=analyzer
    )

    # 3. 构造学术检索任务
    task = SearchTask(
        question="3D Gaussian Splatting 与传统 NeRF 相比有哪些性能与画质优势？",
        keywords=["3D Gaussian Splatting", "3DGS"],
        source_types=["academic", "web"],
        priority="high",
        purpose="对比 3DGS 与 NeRF 在实时渲染和收敛速度上的技术差异"
    )

    # 4. 执行任务（每个插件取 2 条用于快速验证连通性）
    results = manager.search_task(task, max_results_per_plugin=2)

    print("\n" + "=" * 60)
    print(f"🎉 检索结束！共收集到 {len(results)} 条候选文献/网页")
    print("=" * 60)

    # 统计各源产生的结果数
    source_counts = {}
    for r in results:
        source_counts[r.source] = source_counts.get(r.source, 0) + 1
    
    print("\n各检索源结果分布:")
    for src, count in source_counts.items():
        print(f"  - {src}: {count} 条")

    print("\n精选返回结果示例:")
    for i, res in enumerate(results[:5], 1):
        print(f"\n[{i}] 来源: {res.source}")
        print(f"    标题: {res.title}")
        print(f"    链接: {res.url}")


if __name__ == "__main__":
    test_all_plugins()