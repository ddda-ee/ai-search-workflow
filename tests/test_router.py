from models.research import SearchTask
from workflow.search_router import SearchRouter


def main():

    router = SearchRouter()

    tasks = [

        SearchTask(
            question="NeRF 的研究现状是什么？",
            keywords=["NeRF", "Neural Radiance Fields"],
            source_types=["学术论文", "arXiv"],
            priority="high",
            purpose="了解研究现状"
        ),

        SearchTask(
            question="NeRF 有哪些开源项目？",
            keywords=["NeRF GitHub", "NeRF open source"],
            source_types=["GitHub", "官网"],
            priority="medium",
            purpose="寻找开源项目"
        ),

        SearchTask(
            question="3D 重建市场规模是多少？",
            keywords=["3D reconstruction market"],
            source_types=["行业报告", "权威媒体"],
            priority="high",
            purpose="分析市场规模"
        ),
    ]

    for task in tasks:

        routes = router.route(task)

        print("\n" + "=" * 60)
        print(task.question)
        print("=" * 60)

        print(
            f"资料类型：{task.source_types}"
        )

        print(
            f"搜索路线：{routes}"
        )


if __name__ == "__main__":
    main()