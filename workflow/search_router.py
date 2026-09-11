from models.research import SearchTask


class SearchRouter:

    """
    根据 SearchTask 判断任务需要什么搜索能力。

    注意：
    Router 不负责决定具体使用哪个插件。

    Router 只负责回答：

        这个任务需要什么类型的搜索能力？
    """

    ACADEMIC_KEYWORDS = [
        "paper",
        "论文",
        "academic",
        "journal",
        "conference",
        "arxiv",
        "学术",
    ]

    WEB_KEYWORDS = [
        "website",
        "web",
        "company",
        "官网",
        "公司",
        "新闻",
        "媒体",
        "industry",
        "行业",
        "market",
        "市场",
        "report",
        "报告",
    ]

    def route(
        self,
        task: SearchTask
    ) -> list[str]:

        source_text = " ".join(
            task.source_types
        ).lower()

        capabilities = []

        # -------------------------
        # 学术搜索
        # -------------------------

        if self._contains_any(
            source_text,
            self.ACADEMIC_KEYWORDS
        ):
            capabilities.append(
                "academic"
            )

        # -------------------------
        # Web 搜索
        # -------------------------

        if self._contains_any(
            source_text,
            self.WEB_KEYWORDS
        ):
            capabilities.append(
                "web"
            )

        # -------------------------
        # 默认
        # -------------------------

        if not capabilities:
            capabilities.append(
                "web"
            )

        return capabilities

    @staticmethod
    def _contains_any(
        text: str,
        keywords: list[str]
    ) -> bool:

        return any(
            keyword in text
            for keyword in keywords
        )