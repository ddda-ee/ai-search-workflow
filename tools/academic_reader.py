import io
import re
import requests
from typing import Optional
from bs4 import BeautifulSoup
import pypdf


class AcademicReader:
    """学术文献与综合网页全格式解析器。
    
    支持：
    1. ArXiv 页面自动升维（abs -> html 全文 -> pdf 解析）
    2. 原生 PDF 二进制流解析
    3. 通用 HTML 正文清洗与去噪
    """

    def __init__(self, timeout: int = 15):
        self.timeout = timeout
        self.headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            )
        }

    def _extract_pdf_text(self, pdf_bytes: bytes, max_pages: int = 20) -> str:
        """从 PDF 二进制流中提取纯文本。"""
        try:
            reader = pypdf.PdfReader(io.BytesIO(pdf_bytes))
            text_parts = []
            total_pages = min(len(reader.pages), max_pages)

            for idx in range(total_pages):
                page_text = reader.pages[idx].extract_text() or ""
                text_parts.append(page_text)

            full_text = "\n\n".join(text_parts).strip()
            return full_text
        except Exception as exc:
            print(f"  ⚠ PDF 解析异常: {exc}")
            return ""

    def _extract_html_text(self, html_content: str) -> str:
        """HTML 正文去噪与标签清理。"""
        soup = BeautifulSoup(html_content, "html.parser")

        # 剔除无意义节点
        for tag in soup(["script", "style", "nav", "footer", "header", "noscript"]):
            tag.decompose()

        # 优先提取特定学术主容器（如 arxiv html 的 ltx_page_main）
        main_content = (
            soup.find("article")
            or soup.find("main")
            or soup.find("div", class_="ltx_page_main")
            or soup.body
        )

        text = main_content.get_text(separator="\n") if main_content else soup.get_text(separator="\n")
        # 清理多余空行与空格
        cleaned_text = re.sub(r"\n\s*\n+", "\n\n", text).strip()
        return cleaned_text

    def _handle_arxiv(self, url: str) -> Optional[str]:
        """针对 arXiv 的三段式渐进增强提取：HTML 全文 -> 原始网页 -> PDF 流。"""
        arxiv_match = re.search(r"arxiv\.org/(?:abs|pdf)/(\d+\.\d+(?:v\d+)?)", url)
        if not arxiv_match:
            return None

        arxiv_id = arxiv_match.group(1)
        html_url = f"https://arxiv.org/html/{arxiv_id}"
        pdf_url = f"https://arxiv.org/pdf/{arxiv_id}.pdf"

        # 尝试 1：抓取官方 ar5iv HTML 全文
        try:
            resp = requests.get(html_url, headers=self.headers, timeout=self.timeout)
            if resp.status_code == 200 and "ltx_document" in resp.text:
                print(f"  ⚡ 命中 arXiv 实验性 HTML 全文: {arxiv_id}")
                return self._extract_html_text(resp.text)
        except Exception:
            pass

        # 尝试 2：抓取 PDF 原生文件提取全文
        try:
            resp = requests.get(pdf_url, headers=self.headers, timeout=self.timeout)
            if resp.status_code == 200 and resp.headers.get("content-type", "").startswith("application/pdf"):
                print(f"  ⚡ 正在解析 arXiv PDF 原文流: {arxiv_id}")
                pdf_text = self._extract_pdf_text(resp.content, max_pages=15)
                if len(pdf_text) > 1000:
                    return pdf_text
        except Exception:
            pass

        return None

    def read(self, url: str) -> str:
        """主入口：统一解析多源 URL。"""
        # 1. 优先走 arXiv 专用通道
        if "arxiv.org" in url:
            text = self._handle_arxiv(url)
            if text:
                return text

        # 2. 常规网络请求
        resp = requests.get(url, headers=self.headers, timeout=self.timeout)
        resp.raise_for_status()

        content_type = resp.headers.get("content-type", "").lower()

        # 3. 如果是 PDF 格式
        if "application/pdf" in content_type or url.lower().endswith(".pdf"):
            return self._extract_pdf_text(resp.content, max_pages=20)

        # 4. 常规 HTML
        return self._extract_html_text(resp.text)