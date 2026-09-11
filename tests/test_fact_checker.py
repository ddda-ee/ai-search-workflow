from models.llm import LLMClient
from models.research import Document, Finding
from tools.webpage_reader import WebpageReader
from workflow.fact_checker import fact_check_finding


def main():
    url = "https://arxiv.org/abs/2003.08934"

    reader = WebpageReader()
    content = reader.read(url)

    document = Document(
        title="Representing Scenes as Neural Radiance Fields for View Synthesis",
        url=url,
        source="arxiv",
        published_at=None,
        content=content,
    )

    finding = Finding(
        document_title=document.title,
        document_url=document.url,
        key_points=["NeRF represents a scene as a continuous 5D function."],
        methods=[
            "The method uses a fully connected neural network.",
            "Volume rendering is used to render colors along camera rays.",
        ],
        datasets=[],
        evaluation_metrics=[],
        findings=["The method achieves state-of-the-art results."],
        limitations=[],
    )

    llm = LLMClient()

    print("=" * 60)
    print("开始事实核查")
    print("=" * 60)

    result = fact_check_finding(document, finding, llm)

    print("\n核查结果：")

    for evidence in result.evidences:
        print("\nClaim:")
        print(evidence.claim)
        print("Supported:")
        print(evidence.supported)
        print("Evidence:")
        print(evidence.evidence)
        print("Reason:")
        print(evidence.reason)


if __name__ == "__main__":
    main()