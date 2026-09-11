from tools.search.base import BaseSearchPlugin


class SearchPluginRegistry:

    def __init__(self):

        self._plugins: dict[
            str,
            BaseSearchPlugin
        ] = {}

    def register(
        self,
        plugin: BaseSearchPlugin
    ) -> None:

        if plugin.name in self._plugins:
            raise ValueError(
                f"搜索插件已存在：{plugin.name}"
            )

        self._plugins[
            plugin.name
        ] = plugin

    def get(
        self,
        name: str
    ) -> BaseSearchPlugin:

        if name not in self._plugins:
            raise KeyError(
                f"搜索插件不存在：{name}"
            )

        return self._plugins[name]

    def all(
        self
    ) -> list[BaseSearchPlugin]:

        return list(
            self._plugins.values()
        )

    def names(
        self
    ) -> list[str]:

        return list(
            self._plugins.keys()
        )