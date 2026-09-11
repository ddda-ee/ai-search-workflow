from models.research import SearchTask
from workflow.searcher import Searcher


def main():

    searcher = Searcher()

    task = SearchTask(
        question="NeRF 的研究现状是什么？",
        keywords=[
            "NeRF",
            "Neural Radiance Fields"
        ],
        source_types=[
            "学术论文",
            "arXiv"
        ],
        priority="high",
        purpose="了解 NeRF 研究现状"
    )

    results = searcher.search_tasks(
        [task]
    )

    print("\n" + "=" * 60)
    print("最终搜索结果")
    print("=" * 60)

    print(
        f"总结果数：{len(results)}"
    )

    for i, result in enumerate(
        results[:10],
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


if __name__ == "__main__":
    main()