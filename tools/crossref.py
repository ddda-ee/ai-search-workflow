import requests

from models.research import SearchResult


class CrossrefSearchTool:

    API_URL = "https://api.crossref.org/v1/works"

    def search(
        self,
        query: str,
        max_results: int = 5
    ) -> list[SearchResult]:

        params = {
            "query": query,
            "rows": max_results,
        }

        response = requests.get(
            self.API_URL,
            params=params,
            timeout=30
        )

        response.raise_for_status()

        data = response.json()

        items = (
            data
            .get("message", {})
            .get("items", [])
        )

        results = []

        for item in items:

            titles = item.get(
                "title",
                []
            )

            title = (
                titles[0]
                if titles
                else ""
            )

            doi = item.get(
                "DOI",
                ""
            )

            url = (
                f"https://doi.org/{doi}"
                if doi
                else ""
            )

            abstract = item.get(
                "abstract",
                ""
            )

            published_at = (
                self._get_published_date(item)
            )

            results.append(
                SearchResult(
                    title=title,
                    url=url,
                    snippet=abstract,
                    source="crossref",
                    published_at=published_at
                )
            )

        return results

    @staticmethod
    def _get_published_date(
        item: dict
    ) -> str | None:

        date_parts = (
            item
            .get("published-print")
            or item.get("published-online")
            or item.get("issued")
        )

        if not date_parts:
            return None

        parts = date_parts.get(
            "date-parts",
            []
        )

        if not parts:
            return None

        values = parts[0]

        if not values:
            return None

        if len(values) == 1:
            return str(values[0])

        if len(values) == 2:
            return (
                f"{values[0]:04d}-"
                f"{values[1]:02d}"
            )

        return (
            f"{values[0]:04d}-"
            f"{values[1]:02d}-"
            f"{values[2]:02d}"
        )