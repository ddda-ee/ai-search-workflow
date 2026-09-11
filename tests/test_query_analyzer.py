from models.llm import LLMClient
from models.research import SearchTask
from tools.search.registry import SearchPluginRegistry
from tools.search.searxng import SearXNGPlugin
from tools.search.arxiv import ArxivPlugin
from workflow.query_analyzer import QueryAnalyzer
from workflow.search_manager import SearchManager


def test_search_manager_with_query_analyzer():
    print("=" * 60)
    print("🚀 测试 SearchManager + QueryAnalyzer 闭环")
    print("=" * 60)

    # 1. 注册插件
    registry = SearchPluginRegistry()
    registry.register(SearXNGPlugin())
    registry.register(ArxivPlugin())

    # 2. 准备组件
    llm = LLMClient()
    analyzer = QueryAnalyzer(llm)
    manager = SearchManager(
        registry=registry,
        enabled_sources=["searxng", "arxiv"],
        query_analyzer=analyzer
    )

    # 3. 构造容易产生歧义的 Task
    task = SearchTask(
        question="NeRF 在三维场景重建中的最新进展是什么？",
        keywords=["NeRF", "Neural Radiance Fields"],
        source_types=["academic", "web"],
        priority="high",
        purpose="调研神经辐射场算法演变及其最新加速方案"
    )

    # 4. 执行搜索任务
    results = manager.search_task(task, max_results_per_plugin=3)

    # 5. 打印最终检验结果
    print("\n" + "=" * 60)
    print(f"🎉 任务执行完成！共收集到 {len(results)} 条搜索结果。")
    print("=" * 60)

    for i, res in enumerate(results[:6], 1):
        print(f"\n[{i}] 来源: {res.source}")
        print(f"    标题: {res.title}")
        print(f"    链接: {res.url}")
        print(f"    摘要: {res.snippet[:120]}...")


if __name__ == "__main__":
    test_search_manager_with_query_analyzer()