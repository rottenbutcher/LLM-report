from src.rag import build_retriever, chunk_documents, load_documents


def test_rag_retrieval_returns_chunks():
    docs = load_documents('data/sample_rag_docs')
    chunks = chunk_documents(docs)
    retriever = build_retriever(chunks)
    out = retriever.retrieve('section modulus buckling optimization', top_k=3)
    assert len(out) >= 1
    assert 'source' in out[0] and 'text' in out[0]
