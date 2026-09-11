# 离线逻辑单元测试（不依赖网络与 LLM）。
# 运行方式：
#   pytest tests/test_offline_units.py
# 或直接执行本文件，会以极简方式跑一遍所有用例。

from models.research import Document, ResearchPlan, SearchResult
from workflow.selector import GlobalSelector
from workflow.chunker import DocumentChunker
from tools.text_matcher import SimpleSnippetMatcher


def _build_plan():
    return ResearchPlan(
        research_goal="调研 3D Gaussian Splatting 技术",
        research_questions=["3DGS 核心原理是什么？"],
        sub_questions=[],
        chinese_keywords=["三维高斯溅射"],
        english_keywords=["3D Gaussian Splatting", "Radiance Field"],
        technology_routes=["3DGS", "NeRF"],
        source_types=["academic"],
    )


def test_global_selector_dedup_and_rank():
    """验证重复文献被合并，且多源交叉命中的核心文献排在前面。"""
    raw_results = [
        SearchResult(
            title="3D Gaussian Splatting for Real-Time Radiance Field Rendering",
            url="https://arxiv.org/abs/2308.04079v1",
            snippet="Radiance field methods have recently revolutionized novel view synthesis...",
            source="arxiv",
        ),
        SearchResult(
            title="3D Gaussian Splatting for Real-Time Radiance Field Rendering.",
            url="https://doi.org/10.1145/3592433",
            snippet="Radiance field methods have recently revolutionized novel view synthesis of scenes...",
            source="openalex",
        ),
        SearchResult(
            title="Gaussian-JEPA: Joint-Embedding Predictive Learning for 3D Gaussian Splats",
            url="https://arxiv.org/abs/2608.15651v1",
            snippet="We present Gaussian-JEPA for predictive representation...",
            source="arxiv",
        ),
        SearchResult(
            title="Gaussian Splatting vs NeRF Models - What's the Difference and ...",
            url="https://www.reddit.com/r/GaussianSplatting/comments/1ckmboa/",
            snippet="What is the real difference between gaussian splatting and nerf?",
            source="google cse",
        ),
    ]

    selector = GlobalSelector(max_global_documents=2)
    selected = selector.select_global(all_results=raw_results, plan=_build_plan())

    assert len(selected) == 2
    assert "3D Gaussian Splatting for Real-Time" in selected[0].title


def test_global_selector_empty_input():
    selector = GlobalSelector(max_global_documents=3)
    assert selector.select_global(all_results=[]) == []


def test_document_chunker_split():
    document = Document(
        title="Test",
        url="https://example.com",
        source="test",
        published_at=None,
        content="A" * 15000,
    )
    chunker = DocumentChunker(chunk_size=6000, overlap=500)
    chunks = chunker.split(document)

    assert len(chunks) == 3
    assert sum(len(c.content) for c in chunks) > len(document.content)


def test_simple_snippet_matcher():
    text = "\n".join(
        [
            "第一段介绍 3D Gaussian Splatting 使用可微栅格化实现实时渲染。",
            "第二段说明 NeRF 使用 MLP 表示连续辐射场。",
            "第三段比较两者在速度和画质上的差异。",
        ]
    )
    chunks = SimpleSnippetMatcher.chunk_document(text, chunk_size=50, overlap=0)
    assert len(chunks) >= 1

    matched = SimpleSnippetMatcher.find_relevant_snippets("NeRF 连续辐射场", chunks, top_k=1)
    assert matched
    assert "NeRF" in matched[0]


def _main():
    cases = [
        test_global_selector_dedup_and_rank,
        test_global_selector_empty_input,
        test_document_chunker_split,
        test_simple_snippet_matcher,
    ]
    for case in cases:
        case()
        print(f"PASS {case.__name__}")


if __name__ == "__main__":
    _main()