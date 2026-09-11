import re
from typing import List, Optional
from models.research import SearchResult, SearchTask, ResearchPlan


class GlobalSelector:
    """
    全局文献与网页结果选择器。
    
    负责将所有 SearchTask 产生的全部 SearchResult 进行：
    1. DOI / URL 规范化去重
    2. 标题模糊清洗去重
    3. 多源交叉命中与学术加权打分
    4. 全局 Top-N 截断与覆盖度保底
    """

    def __init__(self, max_global_documents: int = 15):
        self.max_global_documents = max_global_documents

    @staticmethod
    def _normalize_title(title: str) -> str:
        """清洗标题：转小写、去除所有标点符号与多余空格，以便模糊去重。"""
        if not title:
            return ""
        # 去掉常见后缀与省略号
        t = re.sub(r"\.{3,}$", "", title.strip().lower())
        # 去掉非字母数字字符（保留中文字符和英文字符）
        t = re.sub(r"[^\w\u4e00-\u9fa5]", "", t)
        return t

    @staticmethod
    def _extract_doi_or_arxiv_id(url: str) -> Optional[str]:
        """从 URL 中提取标准标识符（DOI 或 arXiv ID）用于硬核去重。"""
        if not url:
            return None
        url_lower = url.lower()
        
        # 提取 arXiv ID (例如 2308.04079)
        arxiv_match = re.search(r"arxiv\.org/(?:abs|html|pdf)/([0-9]{4}\.[0-9]{4,5})", url_lower)
        if arxiv_match:
            return f"arxiv:{arxiv_match.group(1)}"
            
        # 提取 DOI (例如 10.1145/3592433)
        doi_match = re.search(r"(10\.\d{4,9}/[-._;()/:a-z0-9]+)", url_lower)
        if doi_match:
            return f"doi:{doi_match.group(1).rstrip('.')}"

        return None

    def _calculate_score(
        self,
        result: SearchResult,
        plan_keywords: List[str],
        appearance_count: int
    ) -> float:
        """多维综合评分。"""
        score = 0.0
        title_lower = result.title.lower()
        snippet_lower = result.snippet.lower()
        url_lower = result.url.lower()
        source_lower = result.source.lower()

        # 1. 关键词命中（标题权重 > 摘要权重）
        for kw in plan_keywords:
            kw_clean = kw.strip().lower()
            if not kw_clean:
                continue
            if kw_clean in title_lower:
                score += 8.0
            elif kw_clean in snippet_lower:
                score += 3.0

        # 2. 权威学术库加权
        academic_sources = {"arxiv", "openalex", "semantic_scholar", "crossref"}
        if source_lower in academic_sources:
            score += 5.0

        # 3. 权威域名加权
        if any(domain in url_lower for domain in ["arxiv.org", "nature.com", "ieee.org", "acm.org"]):
            score += 4.0
        elif "github.com" in url_lower:
            score += 2.0

        # 4. 交叉验证加权：如果同一篇论文被多个源/多个 Query 搜出来，说明是核心文献
        if appearance_count > 1:
            score += (appearance_count - 1) * 6.0

        # 5. 内容丰富度惩罚：没有摘要/snippet 的降权
        if len(snippet_lower.strip()) < 30:
            score -= 3.0

        return score

    def select_global(
        self,
        all_results: List[SearchResult],
        plan: Optional[ResearchPlan] = None,
        tasks: Optional[List[SearchTask]] = None,
    ) -> List[SearchResult]:
        """
        跨任务执行全局去重与打分截断。
        """
        if not all_results:
            return []

        # 收集全局参考关键词
        global_keywords = set()
        if plan:
            global_keywords.update(plan.chinese_keywords)
            global_keywords.update(plan.english_keywords)
            global_keywords.update(plan.technology_routes)
        if tasks:
            for t in tasks:
                global_keywords.update(t.keywords)

        # ① 全局去重与频次统计（同一文献多次被搜到，合并统计 appearance_count）
        # ① 全局去重与频次统计
        deduped_map = {}  # key -> (SearchResult, appearance_count)

        for res in all_results:
            norm_title = self._normalize_title(res.title)
            
            # 1. 优先使用归一化标题作为主键（标题长度 >= 5 即可作为最可靠的去重基准）
            if len(norm_title) >= 5:
                ident = f"title:{norm_title}"
            else:
                # 2. 备用：从 URL 提取 DOI 或 arXiv ID
                extracted_id = self._extract_doi_or_arxiv_id(res.url)
                ident = extracted_id if extracted_id else f"url:{res.url.strip()}"

            if ident in deduped_map:
                existing_res, count = deduped_map[ident]
                # 若新结果带有更丰富的 snippet，保留内容更完整的那一份
                better_res = res if len(res.snippet) > len(existing_res.snippet) else existing_res
                deduped_map[ident] = (better_res, count + 1)
            else:
                deduped_map[ident] = (res, 1)

        # ② 计算综合得分
        scored_list = []
        for ident, (res, count) in deduped_map.items():
            score = self._calculate_score(res, list(global_keywords), appearance_count=count)
            scored_list.append((score, res, count))

        # ③ 按得分从高到低排序
        scored_list.sort(key=lambda x: x[0], reverse=True)

        # ④ 截断 Top-N
        final_selected = [item[1] for item in scored_list[:self.max_global_documents]]

        return final_selected