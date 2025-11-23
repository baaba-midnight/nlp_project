import pytest
from app.core.rag_pipeline import RAGPipeline


def test_rag_pipeline_end_to_end():
    """
    Full integration test:
    1. Builds the RAG pipeline
    2. Sends a query
    3. Performs vector retrieval
    4. Builds the prompt
    5. Generates an LLM answer
    """

    pipeline = RAGPipeline(use_faiss=False)   # Set to True if testing FAISS fallback

    query = "What does the Data Protection Act say about personal data?"

    # ---- Run the pipeline ----
    result = pipeline.run(query, k=3)

    # ---- Assertions ----
    assert "answer" in result, "Pipeline must return an 'answer' field."
    assert "sources" in result, "Pipeline must return 'sources' (retrieved chunks)."

    # Retrieved chunks may be empty, but we want to ensure type correctness
    assert isinstance(result["sources"], list), "Sources must be a list."
    assert isinstance(result["answer"], str), "Answer must be a string."

    print("\n=== RAG PIPELINE OUTPUT ===")
    print("Query:", query)
    print("Answer:", result["answer"])
    print("Sources:")
    for s in result["sources"]:
        print("-", s)


if __name__ == "__main__":
    pytest.main([__file__])
