from dotenv import load_dotenv
from anthropic import Anthropic
from ingest import extract_text, chunk_text, build_index

load_dotenv()                 # loads ANTHROPIC_API_KEY from .env into the environment
client = Anthropic()          # reads that key automatically

SYSTEM = """You are a financial-document analyst. Answer the user's question
using ONLY the provided context excerpts. Cite the page number(s) you used in
the form (p. N). If the answer is not in the context, say so plainly — do not
guess. Be concise and precise with numbers."""

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

def answer_question(collection, question: str, model: str = "claude-sonnet-4-6"):
    hits = retrieve(collection, question, k=5)
    context = "\n\n".join(f"[page {h['page']}]\n{h['text']}" for h in hits)
    prompt = f"Context:\n{context}\n\nQuestion: {question}"
    message = client.messages.create(
        model=model,
        max_tokens=1024,
        system=SYSTEM,
        messages=[{"role": "user", "content": prompt}],
    )
    pages = sorted({h["page"] for h in hits})
    return message.content[0].text, pages

if __name__ == "__main__":
    pages = extract_text("sample_10k.pdf")
    chunks = chunk_text(pages)
    collection = build_index(chunks)

    questions = [
        "What were total revenues, and how did they change year over year?",
        "What was the operating income?",
        "What percentage of revenue came from customers outside the United States?",
    ]
    for q in questions:
        answer, src = answer_question(collection, q)
        print(f"Q: {q}\n{answer}\nSources: pages {src}\n{'-' * 60}")