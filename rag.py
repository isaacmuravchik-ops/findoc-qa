from dotenv import load_dotenv
from anthropic import Anthropic
from ingest import extract_text, chunk_text, build_index

load_dotenv()                 # loads ANTHROPIC_API_KEY from .env into the environment
client = Anthropic()          # reads that key automatically

def ask_claude(prompt: str, model: str = "claude-sonnet-4-6") -> str:
    message = client.messages.create(
        model=model,
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt}],
    )
    return message.content[0].text

def retrieve(collection, question: str, k: int = 5):
    results = collection.query(query_texts=[question], n_results=k)
    docs = results["documents"][0]
    metas = results["metadatas"][0]
    return [{"text": d, "page": m["page"]} for d, m in zip(docs, metas)]

if __name__ == "__main__":
    pages = extract_text("sample_10k.pdf")
    chunks = chunk_text(pages)
    collection = build_index(chunks)

    hits = retrieve(collection, "What were total revenues?")
    for h in hits:
        print(f"[page {h['page']}]  {h['text'][:200]}\n")