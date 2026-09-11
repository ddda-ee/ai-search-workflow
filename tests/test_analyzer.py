from models.llm import LLMClient
from models.research import Document
from tools.webpage_reader import WebpageReader
from workflow.analyzer import analyze_and_verify_document


def main():
    url = "https://arxiv.org/abs/2003.08934"

    print("=" * 60)
    print("开始读取真实论文")
    print("=" * 60)

    reader = WebpageReader()
    content = reader.read(url)

    print(f"论文正文长度：{len(content)}")

    document = Document(
        title="Representing Scenes as Neural Radiance Fields for View Synthesis",
        url=url,
        source="arxiv",
        published_at=None,
        content=content,
    )

    llm = LLMClient()

    print("\n" + "=" * 60)
    print("开始分析论文")
    print("=" * 60)

    finding, fact_check = analyze_and_verify_document(document, llm)

    print("\n核心观点：")
    for item in finding.key_points:
        print(f"- {item}")

    print("\n方法：")
    for item in finding.methods:
        print(f"- {item}")

    print("\n数据集：")
    for item in finding.datasets:
        print(f"- {item}")

    print("\n评价指标：")
    for item in finding.evaluation_metrics:
        print(f"- {item}")

    print("\n主要发现：")
    for item in finding.findings:
        print(f"- {item}")

    print("\n局限性：")
    for item in finding.limitations:
        print(f"- {item}")

    print("\n内联核查证据条数：", len(fact_check.evidences))


if __name__ == "__main__":
    main()