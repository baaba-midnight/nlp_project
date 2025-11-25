"""
Simple RAG pipeline test script.
Run with:  python test_rag.py
"""

from app.core.rag_pipeline import RAGPipeline


def main():
    print("Starting RAG Pipeline Test...\n")

    # Initialize pipeline (use FAISS only if you want)
    pipeline = RAGPipeline(use_faiss=False)

    # Query to test
    query = "What does the Data Protection Act say about personal data?"

    print("Query:", query)
    print("\n Running RAG pipeline...\n")

    # Run pipeline
    result = pipeline.run(query, k=3)

    print("RAG Pipeline Ran Successfully!\n")

    # ------------------------------
    # Print the answer
    # ------------------------------
    print("ANSWER:")
    print(result["answer"])
    print("\n")

    # ------------------------------
    # Print retrieved chunks
    # ------------------------------
    print("RETRIEVED SOURCES:")
    sources = result.get("sources", [])

    if not sources:
        print("No matching documents found.")
    else:
        for i, src in enumerate(sources, start=1):
            print(f"\n--- Chunk {i} ---")

            # Handle both pgvector result and FAISS document
            if isinstance(src, dict):
                print(src.get("chunk") or src)
            else:
                print(src.page_content)


if __name__ == "__main__":
    main()
