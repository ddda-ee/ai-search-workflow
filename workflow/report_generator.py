from pathlib import Path

from models.research import ResearchReport


class ReportGenerator:

    def __init__(
        self,
        output_dir: str = "output"
    ):
        self.output_dir = Path(output_dir)

        self.output_dir.mkdir(
            parents=True,
            exist_ok=True
        )

    def generate_markdown(
        self,
        report: ResearchReport,
        filename: str = "research_report.md"
    ) -> str:

        output_path = self.output_dir / filename

        content = self._build_markdown(report)

        output_path.write_text(
            content,
            encoding="utf-8"
        )

        return str(output_path)

    def _build_markdown(
        self,
        report: ResearchReport
    ) -> str:

        sections = []

        sections.append(
            f"# {report.title}"
        )

        sections.append(
            "## 摘要\n\n"
            + report.executive_summary
        )

        sections.append(
            "## 研究背景\n\n"
            + report.background
        )

        sections.append(
            self._build_list_section(
                "## 研究现状",
                report.research_status
            )
        )

        sections.append(
            self._build_list_section(
                "## 主要研究方法",
                report.key_methods
            )
        )

        sections.append(
            self._build_list_section(
                "## 主要研究发现",
                report.key_findings
            )
        )

        sections.append(
            self._build_list_section(
                "## 方法比较",
                report.comparison
            )
        )

        sections.append(
            self._build_list_section(
                "## 局限性",
                report.limitations
            )
        )

        sections.append(
            self._build_list_section(
                "## 研究空白",
                report.research_gaps
            )
        )

        sections.append(
            self._build_list_section(
                "## 未来研究方向",
                report.future_directions
            )
        )

        sections.append(
            self._build_list_section(
                "## 参考文献",
                report.references
            )
        )

        return "\n\n".join(sections)

    @staticmethod
    def _build_list_section(
        title: str,
        items: list[str]
    ) -> str:

        if not items:
            return f"{title}\n\n暂无相关信息"

        content = "\n".join(
            f"- {item}"
            for item in items
        )

        return f"{title}\n\n{content}"