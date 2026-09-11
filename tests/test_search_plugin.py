from tools.search.searxng import SearXNGPlugin
from tools.search.arxiv import ArxivPlugin


def test_plugin(plugin, keyword):

    print("\n" + "=" * 60)
    print(f"插件：{plugin.name}")
    print("=" * 60)

    print(
        "是否可以处理：",
        plugin.can_handle(keyword)
    )

    results = plugin.search(
        keyword,
        max_results=3
    )

    print(
        f"搜索结果：{len(results)}"
    )

    for i, result in enumerate(results, 1):

        print(f"\n{i}. {result.title}")
        print(result.url)
        print(result.source)


def main():

    keyword = "NeRF neural radiance fields"

    test_plugin(
        SearXNGPlugin(),
        keyword
    )

    test_plugin(
        ArxivPlugin(),
        keyword
    )


if __name__ == "__main__":
    main()