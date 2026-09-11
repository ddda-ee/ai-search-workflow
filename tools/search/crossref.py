from models.research import SearchResult
from tools.crossref import CrossrefSearchTool
from tools.search.base import BaseSearchPlugin


class CrossrefPlugin(BaseSearchPlugin):

    @property
    def name(self) -> str:
        return "crossref"

    @property
    def capabilities(self) -> set[str]:
        return {"academic", "metadata"}

    @property
    def language(self) -> str:
        return "en"

    def __init__(self):
        self.tool = CrossrefSearchTool()

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