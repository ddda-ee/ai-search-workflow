from models.research import SearchResult

from tools.web_search import WebSearchTool

from tools.search.base import BaseSearchPlugin


class SearXNGPlugin(BaseSearchPlugin):

    @property
    def name(self) -> str:
        return "searxng"

    @property
    def capabilities(self) -> set[str]:
        return {
            "web"
        }

    def __init__(self):
        self.tool = WebSearchTool()

    def search(
        self,
        keyword: str,
        max_results: int = 5
    ) -> list[SearchResult]:

        return self.tool.search(
            keyword,
            max_results=max_results
        )

    def can_handle(
        self,
        keyword: str
    ) -> bool:

        return bool(
            keyword.strip()
        )