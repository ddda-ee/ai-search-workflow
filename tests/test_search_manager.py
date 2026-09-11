from models.research import SearchTask

from tools.search.registry import (
    SearchPluginRegistry
)

from tools.search.searxng import (
    SearXNGPlugin
)

from tools.search.arxiv import (
    ArxivPlugin
)

from workflow.search_manager import (
    SearchManager
)


def main():

    # ================================
    # 1. 注册搜索插件
    # ================================

    registry = SearchPluginRegistry()

    registry.register(
        SearXNGPlugin()
    )

    registry.register(
        ArxivPlugin()
    )

    print("\n已注册搜索插件：")

    for plugin in registry.all():

        print(
            f"✓ {plugin.name}"
            f" | capabilities={plugin.capabilities}"
        )

    # ================================
    # 2. 用户配置
    # ================================

    enabled_sources = [
        "searxng",
        "arxiv"
    ]

    print("\n用户启用的搜索插件：")

    for source in enabled_sources:
        print(f"✓ {source}")

    # ================================
    # 3. 创建 SearchManager
    # ================================

    manager = SearchManager(
        registry=registry,
        enabled_sources=enabled_sources
    )

    # ================================
    # 4. 创建 SearchTask
    # ================================

    task = SearchTask(
        question="NeRF 最新研究进展",
        keywords=[
            "NeRF",
            "Neural Radiance Fields"
        ],
        source_types=[
            "paper",
            "arxiv"
        ],
        purpose="寻找 NeRF 相关学术论文",
        priority="high"
    )

    # ================================
    # 5. 查看 Router 判断
    # ================================

    capabilities = manager.router.route(
        task
    )

    print(
        "\n任务需要的搜索能力："
        f"{capabilities}"
    )

    # ================================
    # 6. 测试 Keyword 级插件选择
    # ================================

    print(
        "\n==============================="
    )

    print(
        "测试 Keyword 级插件选择"
    )

    print(
        "==============================="
    )

    for keyword in task.keywords:

        print(
            f"\n关键词：{keyword}"
        )

        plugins = manager.select_plugins(
            task,
            keyword
        )

        print(
            "选择的插件："
        )

        for plugin in plugins:

            print(
                f"✓ {plugin.name}"
            )

    # ================================
    # 7. 执行完整 SearchTask
    # ================================

    print(
        "\n==============================="
    )

    print(
        "执行完整搜索任务"
    )

    print(
        "==============================="
    )

    results = manager.search_task(
        task
    )

    # ================================
    # 8. 输出结果
    # ================================

    print(
        "\n==============================="
    )

    print(
        f"最终搜索结果：{len(results)}"
    )

    print(
        "==============================="
    )

    for i, result in enumerate(
        results,
        1
    ):

        print(
            f"\n{i}. {result.title}"
        )

        print(
            f"   URL: {result.url}"
        )

        print(
            f"   Source: {result.source}"
        )


if __name__ == "__main__":
    main()