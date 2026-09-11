import argparse
import re
from datetime import datetime
from pathlib import Path
from typing import Optional

from models.llm_manager import LLMManager
from models.research import ResearchReport
from workflow.planner import create_research_plan
from workflow.search_task_generator import generate_search_tasks
from workflow.research_pipeline import ResearchPipeline
from workflow.synthesizer import synthesize_report, refine_report
from workflow.reviewer import review_report
from workflow.report_generator import ReportGenerator


def generate_report_filename(request_text: str, ext: str = ".md") -> str:
    """根据用户研究需求与当前系统时间动态生成合规的文件名。

    格式: [问题核心词]_[YYYYMMDD_HHMM].md
    """
    # 过滤路径保留字符与换行空格
    clean_title = re.sub(r'[\\/*?:"<>|\r\n\t\s]+', "_", request_text.strip())
    clean_title = clean_title[:30].strip("_")
    if not clean_title:
        clean_title = "research_report"

    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    return f"{clean_title}_{timestamp}{ext}"


def run_research(
    user_request: str,
    research_type: str = "scientific",
    max_global_documents: int = 5,
    max_results_per_plugin: int = 3,
    output_dir: str = "output",
    output_filename: Optional[str] = None,
    config_path: str = "config/llm_config.yaml",
) -> tuple[ResearchReport, str]:
    """端到端科研报告生成主流程接口。

    支持被外部作为函数导入（如 Web 服务、FastAPI、定时任务）。
    """
    if not output_filename:
        output_filename = generate_report_filename(user_request)

    print("\n" + "=" * 60)
    print("🤖 AI Research Assistant 启动")
    print("=" * 60)
    print(f"研究需求: {user_request}")
    print(f"研究类型: {research_type}")
    print(f"配置文件: {config_path}")
    print(f"拟保存文件名: {output_filename}")

    # 初始化统一的多厂家 LLM 路由管理器
    llm = LLMManager(config_path=config_path)

    # ==========================================
    # 阶段 1：制定研究计划 (Planner)
    # ==========================================
    print("\n" + "=" * 60)
    print("阶段 1：制定研究计划 (Stage: planner)")
    print("=" * 60)
    research_plan = create_research_plan(
        user_request=user_request,
        research_type=research_type,
        llm=llm
    )
    print(f"\n研究目标: {research_plan.research_goal}")
    print("\n核心研究问题:")
    for question in research_plan.research_questions:
        print(f"- {question}")

    # ==========================================
    # 阶段 2：拆解搜索任务 (Search Task Generator)
    # ==========================================
    print("\n" + "=" * 60)
    print("阶段 2：生成搜索任务 (Stage: search_task_generator)")
    print("=" * 60)
    search_tasks = generate_search_tasks(
        research_plan=research_plan,
        llm=llm
    )
    print(f"\n共生成 {len(search_tasks)} 个针对性搜索任务:")
    for i, task in enumerate(search_tasks, 1):
        print(f"  [{i}] (优先级: {task.priority}) {task.question}")
        print(f"      检索词: {', '.join(task.keywords)}")

    # ==========================================
    # 阶段 3～6：多源检索、全局去重与并发内联核查 (Research Pipeline)
    # ==========================================
    pipeline = ResearchPipeline(
        llm_client=llm,
        max_global_documents=max_global_documents,
    )
    documents, findings, fact_checks = pipeline.run(
        tasks=search_tasks,
        plan=research_plan,
        max_results_per_plugin=max_results_per_plugin,
    )

    # ==========================================
    # 阶段 7：综合生成研究报告 (Synthesizer)
    # ==========================================
    print("\n" + "=" * 60)
    print("阶段 7：生成研究报告 (Stage: synthesizer)")
    print("=" * 60)
    report = synthesize_report(
        research_plan=research_plan,
        findings=findings,
        fact_checks=fact_checks,
        llm=llm
    )
    print(f"\n报告初稿生成完成: 《{report.title}》")

    # ==========================================
    # 阶段 8：同行审查与质量检验 (Reviewer)
    # ==========================================
    print("\n" + "=" * 60)
    print("阶段 8：审查研究报告 (Stage: reviewer)")
    print("=" * 60)

    max_refinements = 2  # 默认最大自修重写轮次
    loop_count = 0

    while True:
        review = review_report(report=report, llm=llm)
        print(f"\n[轮次 {loop_count + 1}] 评审结论: {'通过 ✅' if review.passed else '需关注 ⚠️'}")

        if review.issues:
            print("审稿发现的问题:")
            for issue in review.issues:
                print(f"  - {issue}")

        if review.suggestions:
            print("修改建议:")
            for suggestion in review.suggestions:
                print(f"  - {suggestion}")

        # 检验通过或已达修正轮次上限，跳出闭环
        if review.passed or loop_count >= max_refinements:
            if not review.passed:
                print(f"\n⚠ 达到最大重修轮次上限 ({max_refinements})，导出当前修正版本。")
            break

        # 触发报告自愈重写
        print("\n" + "-" * 50)
        print("⚡ 触发自省重写机制：正在结合评审意见精炼报告...")
        print("-" * 50)
        report = refine_report(
            original_report=report,
            review=review,
            fact_checks=fact_checks,
            llm=llm,
        )
        print(f"✓ 报告重写完成: 《{report.title}》，重新提交审稿...")
        loop_count += 1

    # ==========================================
    # 阶段 9：生成 Markdown 报告并持久化落盘
    # ==========================================
    print("\n" + "=" * 60)
    print("阶段 9：生成 Markdown 报告")
    print("=" * 60)
    generator = ReportGenerator(output_dir=output_dir)
    output_path = generator.generate_markdown(report=report, filename=output_filename)

    print(f"\n✓ 报告生成成功: {output_path}")
    print("=" * 60)

    return report, output_path


def main():
    parser = argparse.ArgumentParser(description="AI Research Workflow - 模块化科研研究报告生成引擎")
    parser.add_argument(
        "--request",
        "-r",
        type=str,
        default="请调研 NeRF 的基本原理、核心技术、代表性方法、常用数据集以及当前研究方向。",
        help="用户调研需求或课题",
    )
    parser.add_argument(
        "--type",
        "-t",
        type=str,
        default="scientific",
        choices=["scientific", "market"],
        help="研究类型: scientific (科研) 或 market (商业/市场)",
    )
    parser.add_argument(
        "--max-docs",
        "-m",
        type=int,
        default=5,
        help="全局精选保留的核心文献/网页篇数 (默认: 5)",
    )
    parser.add_argument(
        "--output-file",
        "-o",
        type=str,
        default=None,
        help="指定输出报告文件名（默认自动按'问题+当前日期'命名）",
    )
    parser.add_argument(
        "--config",
        "-c",
        type=str,
        default="config/llm_config.yaml",
        help="多厂家大模型配置文件路径",
    )

    args = parser.parse_args()

    run_research(
        user_request=args.request,
        research_type=args.type,
        max_global_documents=args.max_docs,
        output_filename=args.output_file,
        config_path=args.config,
    )


if __name__ == "__main__":
    main()