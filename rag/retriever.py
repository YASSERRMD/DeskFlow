"""
rag/retriever.py — TF-IDF based local knowledge base retrieval.

Loads .md, .txt, and .pdf files from a directory, chunks them, builds a
TF-IDF index, and retrieves the most relevant chunks for a given query
derived from a barq_chat_form FormResult.
"""

from __future__ import annotations

import logging
import os
import re
from typing import Any

logger = logging.getLogger(__name__)

# In-memory index cache: (vectorizer, matrix, chunks)
_INDEX_CACHE: tuple | None = None


# ------------------------------------------------------------------ #
# Document loading                                                     #
# ------------------------------------------------------------------ #

def _chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> list[str]:
    """Split text into word-based chunks with overlap."""
    words = text.split()
    chunks: list[str] = []
    start = 0
    while start < len(words):
        end = min(start + chunk_size, len(words))
        chunks.append(" ".join(words[start:end]))
        if end == len(words):
            break
        start += chunk_size - overlap
    return chunks


def _load_pdf(path: str) -> str:
    """Extract text from a PDF file using pypdf."""
    try:
        from pypdf import PdfReader
        reader = PdfReader(path)
        return "\n".join(page.extract_text() or "" for page in reader.pages)
    except Exception as exc:
        logger.warning("Failed to read PDF %s: %s", path, exc)
        return ""


def load_knowledge_base(directory: str) -> list[dict[str, Any]]:
    """
    Recursively load all .md, .txt, and .pdf files from directory.

    Returns a flat list of chunk dicts:
        {"filename": str, "content": str, "chunk_index": int}
    """
    if not os.path.isdir(directory):
        logger.warning("Knowledge directory not found: %s", directory)
        return []

    all_chunks: list[dict[str, Any]] = []
    for root, _, files in os.walk(directory):
        for fname in sorted(files):
            ext = os.path.splitext(fname)[1].lower()
            if ext not in (".md", ".txt", ".pdf"):
                continue
            fpath = os.path.join(root, fname)
            if ext == ".pdf":
                content = _load_pdf(fpath)
            else:
                try:
                    with open(fpath, "r", encoding="utf-8", errors="replace") as f:
                        content = f.read()
                except OSError as exc:
                    logger.warning("Cannot read %s: %s", fpath, exc)
                    continue

            if not content.strip():
                continue

            chunks = _chunk_text(content)
            for i, chunk in enumerate(chunks):
                all_chunks.append({
                    "filename": fname,
                    "content": chunk,
                    "chunk_index": i,
                })

    logger.info("Loaded %d chunks from %d files in %s", len(all_chunks), _unique_files(all_chunks), directory)
    return all_chunks


def _unique_files(chunks: list[dict]) -> int:
    return len({c["filename"] for c in chunks})


# ------------------------------------------------------------------ #
# Index                                                                #
# ------------------------------------------------------------------ #

def build_index(chunks: list[dict[str, Any]]) -> tuple:
    """
    Build a TF-IDF index over chunk content.

    Returns (TfidfVectorizer, tfidf_matrix, chunks).
    """
    from sklearn.feature_extraction.text import TfidfVectorizer

    texts = [c["content"] for c in chunks]
    vectorizer = TfidfVectorizer(
        ngram_range=(1, 2),
        max_features=20_000,
        sublinear_tf=True,
        stop_words="english",
    )
    matrix = vectorizer.fit_transform(texts)
    logger.info("Built TF-IDF index: %d chunks, %d features", len(chunks), len(vectorizer.vocabulary_))
    return vectorizer, matrix, chunks


def _get_or_build_index(directory: str) -> tuple:
    """Return the cached index, building and caching it if necessary."""
    global _INDEX_CACHE
    if _INDEX_CACHE is None:
        chunks = load_knowledge_base(directory)
        if not chunks:
            # Return empty index
            from sklearn.feature_extraction.text import TfidfVectorizer
            import numpy as np
            v = TfidfVectorizer()
            v.fit(["placeholder"])
            _INDEX_CACHE = (v, None, [])
        else:
            _INDEX_CACHE = build_index(chunks)
    return _INDEX_CACHE


def invalidate_index() -> None:
    """Clear the in-memory index cache (useful for testing)."""
    global _INDEX_CACHE
    _INDEX_CACHE = None


# ------------------------------------------------------------------ #
# Retrieval                                                            #
# ------------------------------------------------------------------ #

def retrieve_context(form_result: Any, top_k: int = 5, knowledge_dir: str | None = None) -> str:
    """
    Retrieve the top_k most relevant knowledge-base chunks for a form result.

    Accepts a barq_chat_form FormResult object, a plain dict with keys
    ``form_id`` and ``typed_data``, or any object with those attributes.
    Returns concatenated chunk content as a single string.
    """
    import numpy as np

    # Resolve knowledge directory
    if knowledge_dir is None:
        knowledge_dir = os.environ.get("KNOWLEDGE_DIR", "./knowledge/runbooks")

    vectorizer, matrix, chunks = _get_or_build_index(knowledge_dir)

    if matrix is None or len(chunks) == 0:
        logger.warning("Knowledge base is empty — returning empty context")
        return ""

    # Build query from form data — support FormResult objects and plain dicts
    if isinstance(form_result, dict):
        form_id = form_result.get("form_id", "")
        typed_data = form_result.get("typed_data", form_result.get("data", {}))
    else:
        form_id = getattr(form_result, "form_id", "")
        typed_data = getattr(form_result, "typed_data", {}) or {}

    query_parts = [form_id.replace("_", " ")]
    for v in typed_data.values():
        if v and not isinstance(v, bool):
            query_parts.append(str(v).replace("_", " "))

    query = " ".join(query_parts)
    logger.debug("RAG query: %s", query)

    query_vec = vectorizer.transform([query])
    # Cosine similarity
    scores = (matrix @ query_vec.T).toarray().flatten()
    top_indices = np.argsort(scores)[::-1][:top_k]

    retrieved = []
    for idx in top_indices:
        if scores[idx] > 0:
            c = chunks[idx]
            retrieved.append(f"[{c['filename']}]\n{c['content']}")

    context = "\n\n---\n\n".join(retrieved)
    logger.info("Retrieved %d relevant chunks (top score: %.3f)", len(retrieved), float(scores[top_indices[0]]) if len(top_indices) > 0 else 0)
    return context
