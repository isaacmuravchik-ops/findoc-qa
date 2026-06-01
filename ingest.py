import chromadb
from pypdf import PdfReader


def extract_text(pdf_path: str) -> list:
    reader = PdfReader(pdf_path)
    pages = []
    for i, page in enumerate(reader.pages):
        text = page.extract_text() or ""
        pages.append((i + 1, text))   # 1-indexed page number, kept for citations
    return pages


def chunk_text(pages, chunk_size: int = 1000, overlap: int = 150):
    """Split each page into ~chunk_size-character chunks that overlap by
    `overlap` chars, so a sentence straddling a boundary isn't lost.
    Returns a list of {text, page} dicts so we can cite the source page."""
    chunks = []
    for page_num, text in pages:
        start = 0
        while start < len(text):
            end = start + chunk_size
            chunk = text[start:end].strip()
            if chunk:
                chunks.append({"text": chunk, "page": page_num})
            start += chunk_size - overlap
    return chunks


def build_index(chunks, collection_name: str = "doc"):
    chroma = chromadb.Client()          # in-memory store; fine for a demo
    try:                                # wipe any existing collection so re-runs
        chroma.delete_collection(collection_name)   # don't pile up duplicates
    except Exception:
        pass
    collection = chroma.create_collection(collection_name)
    collection.add(
        documents=[c["text"] for c in chunks],
        metadatas=[{"page": c["page"]} for c in chunks],   # page rides with the vector
        ids=[f"chunk-{i}" for i in range(len(chunks))],
    )
    return collection


if __name__ == "__main__":
    pages = extract_text("sample_10k.pdf")
    chunks = chunk_text(pages)
    print(f"{len(chunks)} chunks; first chunk from page {chunks[0]['page']}:")
    print(chunks[0]["text"][:300])

    collection = build_index(chunks)
    print(f"\nIndexed {collection.count()} chunks (should equal {len(chunks)}).")