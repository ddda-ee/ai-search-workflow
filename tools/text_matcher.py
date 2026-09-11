import re
from typing import List, Tuple


class SimpleSnippetMatcher:
    """轻量正文切片与词重合相关性检索器。"""

    @staticmethod
    def chunk_document(text: str, chunk_size: int = 600, overlap: int = 100) -> List[str]:
        """按段落与字符切分文本。"""
        paragraphs = [p.strip() for p in text.split("\n") if p.strip()]
        chunks = []
        current_chunk = []
        current_len = 0

        for p in paragraphs:
            current_chunk.append(p)
            current_len += len(p)
            if current_len >= chunk_size:
                chunks.append("\n".join(current_chunk))
                # 保留尾部做重叠
                current_chunk = current_chunk[-1:] if overlap > 0 else []
                current_len = sum(len(x) for x in current_chunk)

        if current_chunk:
            chunks.append("\n".join(current_chunk))

        return chunks if chunks else [text]

    @staticmethod
    def _tokenize(text: str) -> set[str]:
        """分词：提取中文双字词与英文单字。"""
        words = re.findall(r"[a-zA-Z0-9_\-\.]+|[\u4e00-\u9fa5]{2}", text.lower())
        return set(words)

    @classmethod
    def find_relevant_snippets(
        cls,
        claim: str,
        chunks: List[str],
        top_k: int = 2
    ) -> List[str]:
        """根据待核查主张，检索最相关的正文切片。"""
        claim_tokens = cls._tokenize(claim)
        if not claim_tokens:
            return chunks[:top_k]

        scored_chunks: List[Tuple[float, str]] = []
        for chunk in chunks:
            chunk_tokens = cls._tokenize(chunk)
            if not chunk_tokens:
                continue
            intersection = claim_tokens & chunk_tokens
            # Jaccard 相似度打分
            score = len(intersection) / float(len(claim_tokens | chunk_tokens))
            scored_chunks.append((score, chunk))

        scored_chunks.sort(key=lambda x: x[0], reverse=True)
        return [chunk for score, chunk in scored_chunks[:top_k] if score > 0]