"""
embed.py

Embeds chunks with all-MiniLM-L6-v2 and stores them in a local ChromaDB collection.
Run once to build the index; subsequent queries reuse the persisted collection.

Usage:
    python embed.py            # build index
    from embed import query
    results = query("how early should I apply for internships?", k=5)
"""

import os
import chromadb
from sentence_transformers import SentenceTransformer
from ingest import load_chunks

CHROMA_PATH = "chroma_db"
COLLECTION_NAME = "unofficial_guide"
MODEL_NAME = "all-MiniLM-L6-v2"


def build_index():
    print("Loading chunks...")
    chunks = load_chunks()
    print(f"  {len(chunks)} chunks loaded")

    print(f"Loading embedding model '{MODEL_NAME}'...")
    model = SentenceTransformer(MODEL_NAME)

    print("Embedding chunks (this takes ~30s the first time)...")
    texts = [c["text"] for c in chunks]
    embeddings = model.encode(texts, show_progress_bar=True, convert_to_list=True)

    print(f"Storing in ChromaDB at '{CHROMA_PATH}'...")
    client = chromadb.PersistentClient(path=CHROMA_PATH)
    # Drop and recreate so re-runs start fresh
    try:
        client.delete_collection(COLLECTION_NAME)
    except Exception:
        pass
    # Use cosine distance (standard for sentence-transformer embeddings).
    # ChromaDB defaults to L2, which gives much larger, less interpretable scores.
    collection = client.create_collection(
        COLLECTION_NAME, metadata={"hnsw:space": "cosine"}
    )

    ids = [f"chunk_{i}" for i in range(len(chunks))]
    metadatas = [
        {
            "source": c["source"],
            "title": c["title"],
            "filename": c["filename"],
            "chunk_index": c["chunk_index"],
        }
        for c in chunks
    ]
    collection.add(ids=ids, embeddings=embeddings, documents=texts, metadatas=metadatas)
    print(f"  Indexed {len(chunks)} chunks. Done.")


def get_collection():
    client = chromadb.PersistentClient(path=CHROMA_PATH)
    return client.get_collection(COLLECTION_NAME)


_model = None


def _get_model():
    global _model
    if _model is None:
        _model = SentenceTransformer(MODEL_NAME)
    return _model


def query(text: str, k: int = 5) -> list[dict]:
    """
    Return top-k chunks relevant to `text`.
    Each result: {text, source, title, filename, chunk_index, distance}
    """
    model = _get_model()
    embedding = model.encode(text, convert_to_list=True)
    collection = get_collection()
    results = collection.query(query_embeddings=[embedding], n_results=k)
    output = []
    for i in range(len(results["documents"][0])):
        output.append(
            {
                "text": results["documents"][0][i],
                "source": results["metadatas"][0][i]["source"],
                "title": results["metadatas"][0][i]["title"],
                "filename": results["metadatas"][0][i]["filename"],
                "chunk_index": results["metadatas"][0][i]["chunk_index"],
                "distance": results["distances"][0][i],
            }
        )
    return output


if __name__ == "__main__":
    if not os.path.exists(CHROMA_PATH):
        build_index()
    else:
        ans = input("Index already exists. Rebuild? [y/N] ").strip().lower()
        if ans == "y":
            build_index()

    print("\nTest query: 'how early should I apply for summer internships?'")
    for r in query("how early should I apply for summer internships?"):
        print(f"  [{r['distance']:.3f}] {r['filename']} — {r['text'][:80]}")
