from models.research import SearchTask
from workflow.searcher import Searcher


def main():

    task = SearchTask(
        question="NeRF 的基本原理是什么？",
        keywords=[
            "NeRF neural radiance fields",
            "NeRF volume rendering"
        ],
        source_types=[
            "学术论文"
        ],
        priority="high",
        purpose="了解 NeRF 的基本原理和核心技术"
    )

    searcher = Searcher()

    results = searcher.search_tasks(
        [task]
    )

    print("\n")
    print("=" * 60)
    print("最终搜索结果")
    print("=" * 60)

    for i, result in enumerate(results, 1):

        print(f"\n结果 {i}")
        print(f"标题：{result.title}")
        print(f"URL：{result.url}")
        print(f"来源：{result.source}")


if __name__ == "__main__":
    main()