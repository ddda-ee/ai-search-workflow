from models.research import Document, DocumentChunk


class DocumentChunker:

    def __init__(
        self,
        chunk_size: int = 6000,
        overlap: int = 500
    ):
        self.chunk_size = chunk_size
        self.overlap = overlap

    def split(
        self,
        document: Document
    ) -> list[DocumentChunk]:

        content = document.content

        if not content.strip():
            return []

        chunks = []

        start = 0
        chunk_id = 1

        while start < len(content):

            end = start + self.chunk_size

            chunk_content = content[start:end]

            chunks.append(
                DocumentChunk(
                    document_title=document.title,
                    document_url=document.url,
                    chunk_id=chunk_id,
                    content=chunk_content
                )
            )

            if end >= len(content):
                break

            start = end - self.overlap
            chunk_id += 1

        return chunks