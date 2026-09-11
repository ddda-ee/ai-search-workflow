from abc import ABC, abstractmethod
from models.research import SearchResult


class BaseSearchPlugin(ABC):

    @property
    @abstractmethod
    def name(self) -> str:
        """搜索插件名称"""
        raise NotImplementedError

    @property
    @abstractmethod
    def capabilities(self) -> set[str]:
        """
        搜索插件支持的能力。
        例如：{"web"}, {"academic"}
        """
        raise NotImplementedError

    @property
    def language(self) -> str:
        """
        搜索插件适用的语言体系。
        默认为 'en' (如 arXiv, OpenAlex, Semantic Scholar)。
        中文源（如知网、万方等）重写为 'zh'。
        """
        return "en"

    @abstractmethod
    def search(
        self,
        keyword: str,
        max_results: int = 5
    ) -> list[SearchResult]:
        """执行搜索"""
        raise NotImplementedError

    def can_handle(
        self,
        keyword: str
    ) -> bool:
        """判断插件是否可以处理当前关键词。默认非空即可。"""
        return bool(keyword.strip())