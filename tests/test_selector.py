from models.research import SearchResult, ResearchPlan
from workflow.selector import GlobalSelector


def test_global_selector():
    print("=" * 60)
    print("🚀 测试 GlobalSelector 全局去重与评分...")
    print("=" * 60)

    # 模拟从不同插件收集到的结果（包含同一篇论文的不同链接和微小标题差异）
    raw_results = [
        # 1. 经典 3DGS 论文（arXiv 源）
        SearchResult(
            title="3D Gaussian Splatting for Real-Time Radiance Field Rendering",
            url="https://arxiv.org/abs/2308.04079v1",
            snippet="Radiance field methods have recently revolutionized novel view synthesis...",
            source="arxiv"
        ),
        # 2. 同样这篇论文（OpenAlex 源，带引号和 DOI，测试模糊去重与多源加权）
        SearchResult(
            title="3D Gaussian Splatting for Real-Time Radiance Field Rendering.",
            url="https://doi.org/10.1145/3592433",
            snippet="Radiance field methods have recently revolutionized novel view synthesis of scenes...",
            source="openalex"
        ),
        # 3. 另一篇相关文献
        SearchResult(
            title="Gaussian-JEPA: Joint-Embedding Predictive Learning for 3D Gaussian Splats",
            url="https://arxiv.org/abs/2608.15651v1",
            snippet="We present Gaussian-JEPA for predictive representation...",
            source="arxiv"
        ),
        # 4. 商业/社区讨论帖（低学术价值）
        SearchResult(
            title="Gaussian Splatting vs NeRF Models - What's the Difference and ...",
            url="https://www.reddit.com/r/GaussianSplatting/comments/1ckmboa/",
            snippet="What is the real difference between gaussian splatting and nerf?",
            source="google cse"
        ),
    ]

    plan = ResearchPlan(
        research_goal="调研 3D Gaussian Splatting 技术",
        research_questions=["3DGS 核心原理是什么？"],
        sub_questions=[],
        chinese_keywords=["三维高斯溅射"],
        english_keywords=["3D Gaussian Splatting", "Radiance Field"],
        technology_routes=["3DGS", "NeRF"],
        source_types=["academic"]
    )

    selector = GlobalSelector(max_global_documents=2)
    selected = selector.select_global(all_results=raw_results, plan=plan)

    print(f"\n原始搜索条数: {len(raw_results)}")
    print(f"全局筛选后保留条数: {len(selected)}")
    print("\n筛选出的最终文献列表:")
    for i, item in enumerate(selected, 1):
        print(f"[{i}] {item.title} ({item.source}) -> {item.url}")

    # 验证：重复的 3DGS 应该被合并成 1 条，并且排在第 1 名
    assert len(selected) == 2
    assert "3D Gaussian Splatting for Real-Time" in selected[0].title
    print("\n✅ 全局去重与多源加权验证通过！")


if __name__ == "__main__":
    test_global_selector()