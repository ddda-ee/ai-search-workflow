import json
import os
from urllib.parse import urlencode
from urllib.request import urlopen

from models.research import SearchResult


class WebSearchTool:
    """基于 SearXNG 的通用网页搜索工具。

    SearXNG 地址可通过环境变量 SEARXNG_BASE_URL 覆盖，
    未配置时默认使用本地实例 http://localhost:8080。
    """

    def __init__(
        self,
        base_url: str = None,
    ):
        self.base_url = (base_url or os.getenv("SEARXNG_BASE_URL") or "http://localhost:8080").rstrip("/")

    def search(
        self,
        query: str,
        max_results: int = 5
    ) -> list[SearchResult]:

        params = urlencode({
            "q": query,
            "format": "json",
        })

        url = f"{self.base_url}/search?{params}"

        with urlopen(url, timeout=30) as response:
            data = json.loads(
                response.read().decode("utf-8")
            )

        results = []

        for item in data.get("results", [])[:max_results]:
            result = SearchResult(
                title=item.get("title", ""),
                url=item.get("url", ""),
                snippet=item.get("content", ""),
                source=item.get("engine", ""),
                published_at=item.get("publishedDate")
            )

            results.append(result)

        return results