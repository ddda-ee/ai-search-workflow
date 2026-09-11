from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Optional
from models.research import SearchResult, Document
from tools.academic_reader import AcademicReader


class Collector:
    """多格式文献与正文并发采集器。"""

    def __init__(self, max_workers: int = 5):
        self.reader = AcademicReader(timeout=15)
        self.max_workers = max_workers

    def _fetch_single(self, result: SearchResult) -> Document:
        """单篇抓取与降级隔离函数。"""
        content = ""
        try:
            content = self.reader.read(result.url)
        except Exception as exc:
            print(f"  ⚠ 抓取受限 [{result.source}]: {result.title[:25]}... ({exc})")

        # 熔断策略：若无正文（403/反爬/超时），使用检索阶段的 snippet 作为降级正文，避免数据完全丢失
        if not content or len(content.strip()) < 100:
            fallback_text = result.snippet or "未获取到正文内容"
            print(f"  ⚡ 触发兜底：使用检索摘要作为正文 ({len(fallback_text)} 字)")
            content = f"【正文未成功拉取，根据文献检索摘要替代】\n{fallback_text}"
        else:
            print(f"  ✓ 采集完成 ({len(content)} 字符): {result.title[:28]}...")

        return Document(
            title=result.title,
            url=result.url,
            content=content,
            source=result.source,
            published_at=result.published_at,
        )

    def collect(self, results: list[SearchResult]) -> list[Document]:
        if not results:
            return []

        # 1. URL 基础去重
        unique_results = []
        seen_urls = set()
        for r in results:
            if r.url and r.url not in seen_urls:
                seen_urls.add(r.url)
                unique_results.append(r)

        print(f"⚡ 开始并发采集 {len(unique_results)} 篇文献正文 (并发度: {self.max_workers})...")

        documents = []
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_res = {
                executor.submit(self._fetch_single, res): res
                for res in unique_results
            }

            for future in as_completed(future_to_res):
                doc = future.result()
                documents.append(doc)

        return documents