from __future__ import annotations

from pathlib import Path



try:
    from sklearn.feature_extraction.text import TfidfVectorizer
except Exception:
    TfidfVectorizer = None


def load_documents(folder_path: str) -> list[dict]:
    docs = []
    for p in sorted(Path(folder_path).glob("*.txt")):
        docs.append({"source": p.name, "text": p.read_text(encoding="utf-8")})
    return docs


def chunk_documents(documents: list[dict], chunk_size: int = 500, overlap: int = 100) -> list[dict]:
    chunks = []
    step = max(1, chunk_size - overlap)
    for doc in documents:
        text = doc["text"]
        for i, start in enumerate(range(0, len(text), step)):
            c = text[start : start + chunk_size]
            if c.strip():
                chunks.append({"source": doc["source"], "chunk_id": i, "text": c})
    return chunks


class SimpleRetriever:
    def __init__(self, chunks: list[dict]):
        self.chunks = chunks
        self.texts = [c["text"] for c in chunks]
        self.vectorizer = None
        self.mat = None
        if TfidfVectorizer is not None and self.texts:
            self.vectorizer = TfidfVectorizer(stop_words="english")
            self.mat = self.vectorizer.fit_transform(self.texts)

    def retrieve(self, query: str, top_k: int = 5) -> list[dict]:
        if not self.chunks:
            return []
        if self.vectorizer is not None and self.mat is not None:
            qv = self.vectorizer.transform([query])
            scores = (self.mat @ qv.T).toarray().ravel()
        else:
            q_terms = set(query.lower().split())
            scores = [float(sum(1 for w in c["text"].lower().split() if w in q_terms)) for c in self.chunks]
        ranked = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:top_k]
        return [{**self.chunks[i], "score": float(scores[i])} for i in ranked]


def build_retriever(chunks: list[dict]) -> SimpleRetriever:
    return SimpleRetriever(chunks)
