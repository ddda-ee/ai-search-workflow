from html.parser import HTMLParser
from urllib.request import Request, urlopen


class TextExtractor(HTMLParser):

    def __init__(self):
        super().__init__()

        self.text_parts = []

        self.ignore_tags = {
            "script",
            "style",
            "noscript",
            "svg"
        }

        self.current_ignore = 0

    def handle_starttag(self, tag, attrs):

        if tag in self.ignore_tags:
            self.current_ignore += 1

    def handle_endtag(self, tag):

        if tag in self.ignore_tags and self.current_ignore > 0:
            self.current_ignore -= 1

    def handle_data(self, data):

        if self.current_ignore == 0:
            text = data.strip()

            if text:
                self.text_parts.append(text)

    def get_text(self):

        return "\n".join(self.text_parts)


class WebpageReader:

    def read(self, url: str) -> str:

        request = Request(
            url,
            headers={
                "User-Agent": (
                    "Mozilla/5.0 "
                    "(Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 "
                    "(KHTML, like Gecko) "
                    "Chrome/120 Safari/537.36"
                )
            }
        )

        with urlopen(request, timeout=30) as response:

            html = response.read().decode(
                "utf-8",
                errors="ignore"
            )

        parser = TextExtractor()
        parser.feed(html)

        return parser.get_text()