from models.research import SearchResult

from tools.arxiv_search import ArxivSearchTool
from tools.search.base import BaseSearchPlugin
from tools.rate_limiter import RateLimiter


class ArxivPlugin(BaseSearchPlugin):

    _limiter = RateLimiter(min_interval_seconds=2.5)

    @property
    def name(self) -> str:
        return "arxiv"

    @property
    def capabilities(self) -> set[str]:
        return {
            "academic"
        }

    def __init__(self):
        self.tool = ArxivSearchTool()

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