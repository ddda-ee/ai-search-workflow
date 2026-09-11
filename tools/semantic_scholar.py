import time

import requests

from models.research import SearchResult


class SemanticScholarSearchTool:

    API_URL = (
        "https://api.semanticscholar.org/"
        "graph/v1/paper/search"
    )

    def __init__(
        self,
        retry_count: int = 2,
        retry_delay: int = 3,
    ):
        self.retry_count = retry_count
        self.retry_delay = retry_delay

    def search(
        self,
        query: str,
        max_results: int = 5
    ) -> list[SearchResult]:

        params = {
            "query": query,
            "limit": max_results,
            "fields": (
                "title,"
                "abstract,"
                "url,"
                "year,"
                "publicationDate,"
                "openAccessPdf"
            )
        }

        for attempt in range(
            self.retry_count + 1
        ):

            try:

                response = requests.get(
                    self.API_URL,
                    params=params,
                    timeout=30
                )

                if response.status_code == 429:

                    if attempt < self.retry_count:

                        print(
                            f"⚠ Semantic Scholar 限流，"
                            f"{self.retry_delay} 秒后重试..."
                        )

                        time.sleep(
                            self.retry_delay
                        )

                        continue

                    print(
                        "⚠ Semantic Scholar 多次限流，"
                        "本次搜索跳过"
                    )

                    return []

                response.raise_for_status()

                data = response.json()

                return self._parse_results(
                    data
                )

            except requests.RequestException as exc:

                if attempt < self.retry_count:

                    print(
                        f"⚠ Semantic Scholar 请求失败："
                        f"{exc}"
                    )

                    time.sleep(
                        self.retry_delay
                    )

                    continue

                print(
                    f"⚠ Semantic Scholar 最终失败："
                    f"{exc}"
                )

                return []

        return []

    @staticmethod
    def _parse_results(
        data: dict
    ) -> list[SearchResult]:

        results = []

        for item in data.get(
            "data",
            []
        ):

            title = item.get(
                "title",
                ""
            )

            abstract = item.get(
                "abstract"
            ) or ""

            url = item.get(
                "url"
            ) or ""

            open_access_pdf = item.get(
                "openAccessPdf"
            )

            if open_access_pdf:

                pdf_url = open_access_pdf.get(
                    "url"
                )

                if pdf_url:
                    url = pdf_url

            published_at = item.get(
                "publicationDate"
            )

            if not published_at:

                year = item.get(
                    "year"
                )

                if year:
                    published_at = str(year)

            results.append(
                SearchResult(
                    title=title,
                    url=url,
                    snippet=abstract,
                    source="semantic_scholar",
                    published_at=published_at
                )
            )

        return results