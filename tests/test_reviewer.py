from models.llm import LLMClient
from models.research import ResearchReport
from workflow.reviewer import review_report


def main():
    report = ResearchReport(
        title="NeRF 研究现状分析",
        executive_summary="NeRF 使用神经网络表示场景，并通过体渲染实现新视角合成。",
        background="传统新视角合成方法在复杂场景表示方面存在一定限制。",
        research_status=[
            "NeRF 能够实现复杂场景的新视角合成。",
            "NeRF 使用连续 5D 场景函数表示场景。",
        ],
        key_methods=["全连接神经网络", "连续 5D 坐标表示", "体渲染"],
        key_findings=["NeRF 在新视角合成任务上取得了较好的效果。"],
        comparison=["NeRF 相比部分传统方法能够获得更高质量的新视角合成结果。"],
        limitations=["论文原文指出该方法存在较高的计算成本。"],
        research_gaps=["如何进一步提高 NeRF 的训练和渲染效率仍值得研究。"],
        future_directions=["研究更加高效的神经场表示方法。"],
        references=["https://arxiv.org/abs/2003.08934"],
    )

    llm = LLMClient()
    result = review_report(report, llm)

    print("评审通过：", result.passed)
    print("问题：")
    for item in result.issues:
        print(f"- {item}")
    print("建议：")
    for item in result.suggestions:
        print(f"- {item}")


if __name__ == "__main__":
    main()