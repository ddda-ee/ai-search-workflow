import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET

from models.research import SearchResult


class ArxivSearchTool:

    API_URL = "https://export.arxiv.org/api/query"

    def search(
        self,
        query: str,
        max_results: int = 5
    ) -> list[SearchResult]:

        params = urllib.parse.urlencode({
            "search_query": f"all:{query}",
            "start": 0,
            "max_results": max_results,
            "sortBy": "relevance",
            "sortOrder": "descending",
        })

        url = f"{self.API_URL}?{params}"

        request = urllib.request.Request(
            url,
            headers={
                "User-Agent": "AI-Research-Assistant/1.0"
            }
        )

        with urllib.request.urlopen(
            request,
            timeout=30
        ) as response:

            xml_data = response.read()

        root = ET.fromstring(xml_data)

        namespace = {
            "atom": "http://www.w3.org/2005/Atom"
        }

        results = []

        for entry in root.findall(
            "atom:entry",
            namespace
        ):

            title = entry.findtext(
                "atom:title",
                default="",
                namespaces=namespace
            ).strip()

            summary = entry.findtext(
                "atom:summary",
                default="",
                namespaces=namespace
            ).strip()

            published = entry.findtext(
                "atom:published",
                default=None,
                namespaces=namespace
            )

            link = ""

            for link_element in entry.findall(
                "atom:link",
                namespace
            ):

                href = link_element.attrib.get(
                    "href",
                    ""
                )

                if href.endswith(".pdf"):
                    link = href
                    break

                if (
                    link_element.attrib.get("type")
                    == "text/html"
                ):
                    link = href

            results.append(
                SearchResult(
                    title=title,
                    url=link,
                    snippet=summary,
                    source="arxiv",
                    published_at=published
                )
            )

        return results