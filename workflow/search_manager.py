from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Optional

from models.research import SearchTask, SearchResult
from models.query import QueryAnalysis
from tools.search.base import BaseSearchPlugin
from tools.search.registry import SearchPluginRegistry
from workflow.search_router import SearchRouter
from workflow.query_analyzer import QueryAnalyzer
from storage.cache import SimpleJsonCache


class SearchManager:
    def __init__(
        self,
        registry: SearchPluginRegistry,
        enabled_sources: list[str],
        query_analyzer: Optional[QueryAnalyzer] = None,
        cache: Optional[SimpleJsonCache] = None,
        max_workers: int = 5,
    ):
        self.registry = registry
        self.enabled_sources = enabled_sources
        self.router = SearchRouter()
        self.analyzer = query_analyzer
        self.cache = cache
        self.max_workers = max_workers

    def enabled_plugins(self) -> list[BaseSearchPlugin]:
        plugins = []
        for source_name in self.enabled_sources:
            try:
                plugin = self.registry.get(source_name)
                plugins.append(plugin)
            except KeyError:
                print(f"⚠ 搜索插件不存在：{source_name}")
                continue
        return plugins

    def select_plugins(
        self,
        task: SearchTask,
        keyword: str
    ) -> list[BaseSearchPlugin]:
        enabled_plugins = self.enabled_plugins()
        required_capabilities = self.router.route(task)

        selected = []
        for plugin in enabled_plugins:
            if plugin.name == "searxng":
                if plugin.can_handle(keyword):
                    selected.append(plugin)
                continue

            matched = plugin.capabilities & set(required_capabilities)
            if not matched:
                continue

            if not plugin.can_handle(task.question):
                continue

            selected.append(plugin)

        return selected

    def _determine_query_for_plugin(
        self,
        plugin: BaseSearchPlugin,
        keyword: str,
        analysis: Optional[QueryAnalysis]
    ) -> str:
        if not analysis:
            return keyword

        if "academic" in plugin.capabilities:
            is_zh_academic = (
                getattr(plugin, "language", "en") == "zh"
                or "zh" in plugin.capabilities
                or "chinese" in plugin.name.lower()
            )
            if is_zh_academic:
                if analysis.academic_queries_zh:
                    return analysis.academic_queries_zh[0]
            else:
                if analysis.academic_queries_en:
                    return analysis.academic_queries_en[0]

        if "web" in plugin.capabilities or plugin.name == "searxng":
            if analysis.web_queries:
                return analysis.web_queries[0]

        return analysis.normalized_query or keyword

    def _search_single_plugin(
        self,
        plugin: BaseSearchPlugin,
        target_query: str,
        max_results: int
    ) -> list[SearchResult]:
        cache_key = f"{plugin.name}:{target_query}:{max_results}"

        # 1. 检查搜索缓存
        if self.cache:
            cached_items = self.cache.get("search_results", cache_key)
            if cached_items is not None:
                results = [SearchResult.model_validate(item) for item in cached_items]
                print(f"  ⚡ [Cache Hit] {plugin.name:<16} | 命中缓存: {len(results)} 条")
                return results

        # 2. 实际发起插件请求
        try:
            results = plugin.search(target_query, max_results=max_results)
            print(f"  ✓ 来源: {plugin.name:<16} | 返回: {len(results)} 条 | Query: '{target_query}'")
            
            # 3. 结果写入缓存
            if self.cache:
                self.cache.set(
                    "search_results",
                    cache_key,
                    [r.model_dump() for r in results]
                )
            return results
        except Exception as exc:
            print(f"  ⚠ 来源: {plugin.name:<16} | 失败: {exc}")
            return []

    def search_keyword(
        self,
        keyword: str,
        plugins: list[BaseSearchPlugin],
        task_context: str = "",
        max_results: int = 5
    ) -> list[SearchResult]:
        results = []

        analysis = None
        if self.analyzer:
            print(f"\n[QueryAnalyzer] 正在对关键词 '{keyword}' 进行消歧扩展...")
            try:
                analysis = self.analyzer.analyze(keyword=keyword, task_context=task_context)
                print(f"✓ 概念展开: {analysis.concepts}")
                print(f"✓ 学术英文 Query: {analysis.academic_queries_en}")
                print(f"✓ Web Query: {analysis.web_queries}")
            except Exception as exc:
                print(f"⚠ QueryAnalyzer 分析失败，降级使用原始关键词: {exc}")

        print(f"⚡ 开始并发请求 {len(plugins)} 个搜索源...")
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {
                executor.submit(
                    self._search_single_plugin,
                    plugin,
                    self._determine_query_for_plugin(plugin, keyword, analysis),
                    max_results
                ): plugin
                for plugin in plugins
            }

            for future in as_completed(futures):
                plugin_results = future.result()
                results.extend(plugin_results)

        return results

    def search_task(
        self,
        task: SearchTask,
        max_results_per_plugin: int = 5
    ) -> list[SearchResult]:
        print(f"\n{'=' * 50}")
        print(f"执行搜索任务：{task.question}")
        print(f"任务目的：{task.purpose}")
        print(f"{'=' * 50}")

        results = []
        task_context = f"任务问题: {task.question}\n研究目的: {task.purpose}"

        for keyword in task.keywords[:2]:
            print(f"\n----------------------------------------")
            print(f"处理关键词：{keyword}")
            print(f"----------------------------------------")

            plugins = self.select_plugins(task, keyword)
            print(f"匹配的搜索插件: {[p.name for p in plugins]}")

            keyword_results = self.search_keyword(
                keyword=keyword,
                plugins=plugins,
                task_context=task_context,
                max_results=max_results_per_plugin
            )
            results.extend(keyword_results)

        return results

    def search_tasks_parallel(
        self,
        tasks: list[SearchTask],
        max_results_per_plugin: int = 3,
        task_workers: int = 3
    ) -> list[SearchResult]:
        all_results = []
        print(f"\n🚀 启动跨任务并行搜索，任务数: {len(tasks)}，并行度: {task_workers}")

        with ThreadPoolExecutor(max_workers=task_workers) as executor:
            future_to_task = {
                executor.submit(self.search_task, task, max_results_per_plugin): task
                for task in tasks
            }

            for future in as_completed(future_to_task):
                task = future_to_task[future]
                try:
                    task_results = future.result()
                    all_results.extend(task_results)
                except Exception as exc:
                    print(f"⚠ 任务执行异常 [{task.question[:20]}...]: {exc}")

        return all_results