from models.research import Document
from workflow.chunker import DocumentChunker


def main():

    document = Document(
        title="NeRF Test",
        url="https://example.com",
        source="test",
        published_at=None,
        content="A" * 15000
    )

    chunker = DocumentChunker(
        chunk_size=6000,
        overlap=500
    )

    chunks = chunker.split(document)

    print("=" * 60)
    print("Chunker 测试")
    print("=" * 60)

    print(f"\n原文长度：{len(document.content)}")
    print(f"切片数量：{len(chunks)}")

    for chunk in chunks:

        print(
            f"\nChunk {chunk.chunk_id}"
        )

        print(
            f"长度：{len(chunk.content)}"
        )

        print(
            f"前20字符：{chunk.content[:20]}"
        )


if __name__ == "__main__":
    main()