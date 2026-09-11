from models.research import SearchTask, ResearchPlan
from workflow.research_pipeline import ResearchPipeline
from workflow.synthesizer import synthesize_report
from workflow.reviewer import review_report
from workflow.report_generator import ReportGenerator


def test_full_pipeline():
    print("=" * 60)
    print("开始测试 ResearchPipeline 端到端全流程")
    print("=" * 60)

    # 1. 模拟 ResearchPlan
    plan = ResearchPlan(
        research_goal="调研三维高斯溅射 (3D Gaussian Splatting) 的前沿技术发展与演进趋势",
        research_questions=[
            "3DGS 相比于传统 NeRF 的核心理论优势是什么？",
            "3DGS 目前在工业落地与动态场景下存在哪些局限？",
        ],
        sub_questions=[],
        chinese_keywords=["三维高斯溅射", "辐射场渲染"],
        english_keywords=["3D Gaussian Splatting", "Neural Radiance Fields"],
        technology_routes=["3DGS", "NeRF", "Real-Time Rendering"],
        source_types=["academic", "web"],
    )

    # 2. 模拟 2 个搜索子任务
    tasks = [
        SearchTask(
            question="3D Gaussian Splatting 相比 NeRF 的渲染速度与画质优势是什么？",
            keywords=["3D Gaussian Splatting", "NeRF"],
            source_types=["academic", "web"],
            priority="high",
            purpose="分析 3DGS 在可微栅格化与实时渲染上的突破",
        ),
        SearchTask(
            question="3D Gaussian Splatting 针对动态场景重建的技术路线有哪些？",
            keywords=["Dynamic 3D Gaussian Splatting", "Deformable 3DGS"],
            source_types=["academic"],
            priority="medium",
            purpose="调研 4D/动态 3DGS 的核心解决方案",
        ),
    ]

    # 3. 初始化流水线（全局精选保留 3 篇核心文献，加快端到端验证速度）
    pipeline = ResearchPipeline(max_global_documents=3)

    # 4. 执行检索、筛选、正文采集、分析与事实核查阶段
    docs, findings, fact_checks = pipeline.run(
        tasks=tasks,
        plan=plan,
        max_results_per_plugin=2,
    )

    print("\n" + "=" * 60)
    print("检索与核查阶段完成")
    print("=" * 60)
    print(f"文档数：{len(docs)}，观点抽取数：{len(findings)}，核查结果数：{len(fact_checks)}")

    # 5. 合成报告并进行一轮评审
    report = synthesize_report(
        research_plan=plan,
        findings=findings,
        fact_checks=fact_checks,
        llm=pipeline.llm,
    )
    review = review_report(report, pipeline.llm)

    print(f"\n报告标题：{report.title}")
    print(f"评审通过：{review.passed}")

    # 6. 生成 Markdown
    generator = ReportGenerator(output_dir="output")
    output_path = generator.generate_markdown(report, "test_pipeline_report.md")
    print(f"\n报告已生成：{output_path}")

    print("\n" + "=" * 60)
    print("全流程端到端跑通成功！")
    print("=" * 60)


if __name__ == "__main__":
    test_full_pipeline()