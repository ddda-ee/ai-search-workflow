from tools.search.registry import (
    SearchPluginRegistry
)

from tools.search.searxng import (
    SearXNGPlugin
)

from tools.search.arxiv import (
    ArxivPlugin
)


def main():

    registry = SearchPluginRegistry()

    # 注册插件
    registry.register(
        SearXNGPlugin()
    )

    registry.register(
        ArxivPlugin()
    )

    print("\n已注册搜索插件：")

    for name in registry.names():

        print(
            f"✓ {name}"
        )

    print(
        "\n插件数量：",
        len(registry.all())
    )

    # 获取插件
    searxng = registry.get(
        "searxng"
    )

    print(
        "\n获取插件：",
        searxng.name
    )


if __name__ == "__main__":
    main()