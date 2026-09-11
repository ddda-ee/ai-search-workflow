from models.research import SearchResult
from tools.semantic_scholar import SemanticScholarSearchTool
from tools.search.base import BaseSearchPlugin
from tools.rate_limiter import RateLimiter


class SemanticScholarPlugin(BaseSearchPlugin):

    _limiter = RateLimiter(min_interval_seconds=1.5)

    @property
    def name(self) -> str:
        return "semantic_scholar"

    @property
    def capabilities(self) -> set[str]:
        return {"academic"}

    @property
    def language(self) -> str:
        return "en"

    def __init__(self):
        self.tool = SemanticScholarSearchTool()

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
        return bool(keyword.strip())