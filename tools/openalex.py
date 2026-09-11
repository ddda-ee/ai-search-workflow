import requests

from models.research import SearchResult


class OpenAlexSearchTool:

    API_URL = "https://api.openalex.org/works"

    def search(
        self,
        query: str,
        max_results: int = 5
    ) -> list[SearchResult]:

        params = {
            "search": query,
            "per-page": max_results,
        }

        response = requests.get(
            self.API_URL,
            params=params,
            timeout=30
        )

        response.raise_for_status()

        data = response.json()

        results = []

        for item in data.get(
            "results",
            []
        ):

            title = item.get(
                "display_name",
                ""
            )

            url = item.get(
                "doi"
            )

            if not url:
                primary_location = item.get(
                    "primary_location"
                ) or {}

                landing_page = (
                    primary_location
                    .get("landing_page_url")
                )

                url = landing_page or ""

            abstract = self._reconstruct_abstract(
                item.get("abstract_inverted_index")
            )

            publication_date = item.get(
                "publication_date"
            )

            results.append(
                SearchResult(
                    title=title,
                    url=url,
                    snippet=abstract,
                    source="openalex",
                    published_at=publication_date
                )
            )

        return results

    @staticmethod
    def _reconstruct_abstract(
        inverted_index
    ) -> str:

        if not inverted_index:
            return ""

        words = []

        for word, positions in inverted_index.items():

            for position in positions:
                words.append(
                    (position, word)
                )

        words.sort(
            key=lambda item: item[0]
        )

        return " ".join(
            word
            for _, word in words
        )