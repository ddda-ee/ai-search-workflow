from models.research import SearchResult
from tools.openalex import OpenAlexSearchTool
from tools.search.base import BaseSearchPlugin


class OpenAlexPlugin(BaseSearchPlugin):

    @property
    def name(self) -> str:
        return "openalex"

    @property
    def capabilities(self) -> set[str]:
        return {"academic"}

    @property
    def language(self) -> str:
        return "en"

    def __init__(self):
        self.tool = OpenAlexSearchTool()

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