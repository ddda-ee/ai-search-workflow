from models.research import SearchTask, SearchResult

from tools.web_search import WebSearchTool
from tools.arxiv_search import ArxivSearchTool
from tools.semantic_scholar import SemanticScholarSearchTool
from tools.openalex import OpenAlexSearchTool
from tools.crossref import CrossrefSearchTool

from workflow.search_router import SearchRouter


class Searcher:

    def __init__(self):

        self.router = SearchRouter()

        self.web_search = WebSearchTool()
        self.arxiv_search = ArxivSearchTool()
        self.semantic_scholar = SemanticScholarSearchTool()

        self.openalex = OpenAlexSearchTool()
        self.crossref = CrossrefSearchTool()

    def search_task(
        self,
        task: SearchTask
    ) -> list[SearchResult]:

        print("\n正在执行搜索任务：")

        print(
            f"问题：{task.question}"
        )

        routes = self.router.route(
            task
        )

        print(
            f"搜索路线：{routes}"
        )

        keywords = task.keywords[:2]

        all_results = []

        for keyword in keywords:

            print(
                f"\n搜索关键词：{keyword}"
            )

            task_results = self._search_keyword(
                keyword,
                routes
            )

            print(
                f"获得结果："
                f"{len(task_results)}"
            )

            all_results.extend(
                task_results
            )

        return all_results

    def search_tasks(
        self,
        tasks: list[SearchTask]
    ) -> list[SearchResult]:

        all_results = []

        for i, task in enumerate(
            tasks,
            1
        ):

            print(
                f"\n{'=' * 60}"
            )

            print(
                f"执行搜索任务 "
                f"{i}/{len(tasks)}"
            )

            task_results = self.search_task(
                task
            )

            all_results.extend(
                task_results
            )

        return all_results

    
    def _search_keyword(
        self,
        keyword: str,
        routes: list[str]
    ) -> list[SearchResult]:

        results = []

        for route in routes:

            if route == "semantic_scholar":

                results.extend(
                    self._safe_search(
                        self.semantic_scholar,
                        keyword
                    )
                )

            elif route == "arxiv":

                results.extend(
                    self._safe_search(
                        self.arxiv_search,
                        keyword
                    )
                )

            elif route == "web":

                results.extend(
                    self._safe_search(
                        self.web_search,
                        keyword
                    )
                )

        return results

    @staticmethod
    def _safe_search(
        search_tool,
        keyword: str
    ) -> list[SearchResult]:

        try:

            return search_tool.search(
                keyword,
                max_results=5
            )

        except Exception as exc:

            print(
                f"⚠ 搜索失败："
                f"{type(search_tool).__name__}"
                f" → {exc}"
            )

            return []