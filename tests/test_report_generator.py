from models.research import ResearchReport
from workflow.report_generator import ReportGenerator


def main():

    report = ResearchReport(
        title="NeRF 研究现状分析",

        executive_summary=(
            "NeRF 使用神经网络表示场景，"
            "并通过体渲染实现新视角合成。"
        ),

        background=(
            "NeRF 是神经场研究中的代表性方法，"
            "主要用于三维场景表示和新视角合成。"
        ),

        research_status=[
            "NeRF 使用连续 5D 场景函数表示场景。",
            "NeRF 使用神经网络学习场景表示。"
        ],

        key_methods=[
            "全连接神经网络",
            "连续 5D 坐标表示",
            "体渲染"
        ],

        key_findings=[
            "NeRF 在新视角合成任务上取得了较好的效果。"
        ],

        comparison=[
            "相比部分传统方法，NeRF 能够获得更高质量的新视角合成结果。"
        ],

        limitations=[
            "训练和渲染计算成本较高。"
        ],

        research_gaps=[
            "如何进一步提高 NeRF 的训练和渲染效率仍值得研究。"
        ],

        future_directions=[
            "研究更加高效的神经场表示方法。"
        ],

        references=[
            "https://arxiv.org/abs/2003.08934"
        ]
    )

    generator = ReportGenerator()

    output_path = generator.generate_markdown(
        report,
        "test_report.md"
    )

    print("=" * 60)
    print("报告生成完成")
    print("=" * 60)

    print(f"\n报告路径：{output_path}")


if __name__ == "__main__":
    main()