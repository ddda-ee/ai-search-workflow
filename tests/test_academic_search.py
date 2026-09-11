from tools.arxiv_search import ArxivSearchTool
from tools.semantic_scholar import SemanticScholarSearchTool
from tools.openalex import OpenAlexSearchTool
from tools.crossref import CrossrefSearchTool


def test_tool(name, tool):

    print("\n" + "=" * 60)
    print(name)
    print("=" * 60)

    try:

        results = tool.search(
            "NeRF",
            max_results=3
        )

        print(
            f"结果数量：{len(results)}"
        )

        for i, result in enumerate(
            results,
            1
        ):

            print(
                f"\n{i}. {result.title}"
            )

            print(
                f"来源：{result.source}"
            )

            print(
                f"URL：{result.url}"
            )

            print(
                f"摘要："
                f"{result.snippet[:200]}"
            )

    except Exception as exc:

        print(
            f"✗ 测试失败：{exc}"
        )


def main():

    test_tool(
        "arXiv",
        ArxivSearchTool()
    )

    test_tool(
        "Semantic Scholar",
        SemanticScholarSearchTool()
    )

    test_tool(
        "OpenAlex",
        OpenAlexSearchTool()
    )

    test_tool(
        "Crossref",
        CrossrefSearchTool()
    )


if __name__ == "__main__":
    main()