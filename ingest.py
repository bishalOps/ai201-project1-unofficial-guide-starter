"""
ingest.py

Loads documents from documents/, cleans them, and splits them into chunks.
Chunk size: 400 characters, overlap: 80 characters (per planning.md).

Usage:
    from ingest import load_chunks
    chunks = load_chunks()   # list of dicts: {text, source, title}
"""

import os
import re

DOCS_DIR = "documents"
CHUNK_SIZE = 400
OVERLAP = 80
MIN_CHUNK_LEN = 50

# Lines like "--- POST ---" / "--- COMMENTS ---" that mark structure, not content.
MARKER_RE = re.compile(r"^\s*---\s*(POST|COMMENTS)\s*---\s*$", re.IGNORECASE)
# Structured header lines at the top of every cleaned document.
HEADER_RE = re.compile(r"^(SOURCE|TITLE|URL):\s*(.*)$")


def parse_document(raw: str) -> tuple[dict, str]:
    """
    Split a cleaned document into its structured header and its body.

    Cleaned docs start with:
        SOURCE: r/...
        TITLE: ...
        URL: ...

        --- POST ---
        ...body...

    Returns (metadata, body) where metadata holds source/title/url and body
    is everything after the header (post + comments), markers still present.
    """
    meta = {"source": "unknown", "title": "unknown", "url": ""}
    lines = raw.splitlines()
    body_start = 0
    for i, line in enumerate(lines):
        stripped = line.strip()
        if not stripped:
            continue  # blank line between header and body
        m = HEADER_RE.match(stripped)
        if m:
            key, val = m.group(1).upper(), m.group(2).strip()
            if key == "SOURCE":
                meta["source"] = val
            elif key == "TITLE":
                meta["title"] = val
            elif key == "URL":
                meta["url"] = val
            body_start = i + 1
        else:
            break  # first real content line — header is done
    return meta, "\n".join(lines[body_start:])


def clean_text(text: str) -> str:
    """
    Light cleanup of an already-cleaned document body: drop the structural
    --- POST --- / --- COMMENTS --- marker lines and collapse extra blank
    lines. (Heavy Reddit-chrome stripping happens in the document files
    themselves; this is a safety net.)
    """
    cleaned = [ln for ln in text.splitlines() if not MARKER_RE.match(ln.strip())]
    body = "\n".join(cleaned)
    body = re.sub(r"\n{3,}", "\n\n", body)  # collapse 3+ blank lines to 2
    return body.strip()


def chunk_text(text: str) -> list[str]:
    """Split text into overlapping fixed-size character chunks."""
    chunks = []
    start = 0
    while start < len(text):
        end = start + CHUNK_SIZE
        chunks.append(text[start:end].strip())
        start += CHUNK_SIZE - OVERLAP
    return [c for c in chunks if len(c) >= MIN_CHUNK_LEN]


def load_chunks() -> list[dict]:
    """Return all chunks across all documents as a list of dicts."""
    all_chunks = []
    for filename in sorted(os.listdir(DOCS_DIR)):
        if not filename.endswith(".txt"):
            continue
        path = os.path.join(DOCS_DIR, filename)
        with open(path, encoding="utf-8") as f:
            raw = f.read()
        meta, body = parse_document(raw)
        meta["filename"] = filename
        body = clean_text(body)
        for position, chunk in enumerate(chunk_text(body)):
            # chunk_index = position of this chunk within its own document
            all_chunks.append({"text": chunk, "chunk_index": position, **meta})
    return all_chunks


if __name__ == "__main__":
    import random

    chunks = load_chunks()
    print(f"Total chunks: {len(chunks)}")

    lengths = [len(c["text"]) for c in chunks]
    print(f"Chunk length: min={min(lengths)}  max={max(lengths)}  "
          f"avg={sum(lengths) // len(lengths)}")
    print(f"Documents covered: {len({c['filename'] for c in chunks})}")

    print("\n" + "=" * 72)
    print("5 RANDOM CHUNKS (inspect: readable, substantive, self-contained?)")
    print("=" * 72)
    random.seed(42)
    for c in random.sample(chunks, 5):
        print(f"\n--- {c['filename']}  |  source={c['source']}  |  "
              f"title={c['title'][:40]!r}")
        print(c["text"])
