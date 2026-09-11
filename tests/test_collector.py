from models.research import SearchResult
from workflow.selector import GlobalSelector


def main():
    results = [
        SearchResult(
            title="NeRF: Representing Scenes as Neural Radiance Fields",
            url="https://arxiv.org/abs/2003.08934",
            snippet="NeRF represents scenes using a continuous 5D function.",
            source="arxiv",
        ),
        SearchResult(
            title="NeRF: Representing Scenes as Neural Radiance Fields",
            url="https://example.com/nerf-copy",
            snippet="NeRF paper.",
            source="blog",
        ),
        SearchResult(
            title="NeRF GitHub Implementation",
            url="https://github.com/example/nerf",
            snippet="Official implementation.",
            source="github",
        ),
        SearchResult(
            title="NeRF Introduction",
            url="https://example.com/nerf",
            snippet="Introduction to neural radiance fields.",
            source="blog",
        ),
        SearchResult(
            title="NeRF Survey Paper",
            url="https://arxiv.org/abs/nerf-survey",
            snippet="A survey of neural radiance fields.",
            source="arxiv",
        ),
    ]

    selector = GlobalSelector(max_global_documents=3)
    selected = selector.select_global(all_results=results)

    print("=" * 60)
    print("搜索结果筛选测试")
    print("=" * 60)

    print(f"\n原始结果：{len(results)}")
    print(f"筛选结果：{len(selected)}")

    print("\n最终选择：")
    for i, result in enumerate(selected, 1):
        print(f"{i}. {result.title}")
        print(f"   {result.url}")


if __name__ == "__main__":
    main()