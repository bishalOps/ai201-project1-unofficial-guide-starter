"""
rag.py

End-to-end retrieval-augmented generation: retrieve chunks, ground an LLM
answer in them, and attach source attribution programmatically.

Usage:
    from rag import ask
    result = ask("What do I do if I fail a coding interview?")
    print(result["answer"])
    print(result["sources"])   # real retrieved filenames, not LLM-claimed
"""

import os
from dotenv import load_dotenv
from groq import Groq
from embed import query

load_dotenv()

MODEL = "llama-3.3-70b-versatile"

# Exact sentence the model must use when the context can't answer the question.
REFUSAL = "I don't have enough information on that in my documents."

SYSTEM_PROMPT = f"""You are an assistant for "The Unofficial CS Career Guide".
Answer the user's question using ONLY the information in the numbered context
passages provided below.

Rules:
- Use only facts stated in the context passages. Do NOT use outside knowledge,
  and do NOT guess or infer beyond what the passages actually say.
- If the passages do not contain enough information to answer the question,
  reply with EXACTLY this sentence and nothing else:
  "{REFUSAL}"
- Do not invent statistics, names, companies, or sources.
- Be concise and practical.
- Do NOT write your own "Sources" section — sources are attached automatically."""


def format_context(chunks: list[dict]) -> str:
    """Render retrieved chunks as a numbered, source-tagged context block."""
    parts = []
    for i, chunk in enumerate(chunks, 1):
        parts.append(f"[{i}] (from: {chunk['filename']})\n{chunk['text']}")
    return "\n\n".join(parts)


def _retrieved_sources(chunks: list[dict]) -> list[str]:
    """Unique filenames in retrieval order (best match first)."""
    seen = []
    for c in chunks:
        if c["filename"] not in seen:
            seen.append(c["filename"])
    return seen


def ask(question: str, k: int = 5) -> dict:
    """
    Retrieve top-k chunks, generate a grounded answer, and attach the real
    retrieved source filenames.

    Returns: {"answer": str, "sources": list[str], "chunks": list[dict]}
    `sources` is empty when the model declines for lack of grounding.
    """
    chunks = query(question, k=k)
    context = format_context(chunks)

    client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {question}"},
        ],
        temperature=0.2,
        max_tokens=700,
    )
    answer = response.choices[0].message.content.strip()

    # Source attribution is computed in code, not trusted to the LLM.
    # If the model declined, attach no sources (it used none).
    declined = "don't have enough information" in answer.lower()
    sources = [] if declined else _retrieved_sources(chunks)

    return {"answer": answer, "sources": sources, "chunks": chunks}


if __name__ == "__main__":
    for q in [
        "What do I do if I fail a coding interview?",
        "How do I get a referral if I don't know anyone at the company?",
        "What is the best recipe for chocolate chip cookies?",  # out of domain
    ]:
        print("=" * 80)
        print("Q:", q)
        r = ask(q)
        print("\nANSWER:\n", r["answer"])
        print("\nSOURCES:", r["sources"])
        print()
