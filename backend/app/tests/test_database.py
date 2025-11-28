from app.core.rag_pipeline import RAGPipeline

pipeline = RAGPipeline(use_faiss=False, similarity_threshold=0.5)

# Run query
result = pipeline.run(
    "What is court act?", 
    k=5
)

# Access results
print(f"Answer: {result['answer']}")
print(f"Confidence: {result['confidence']:.2f}")
print(f"Sources used: {result['num_sources']}")
print(f"Avg similarity: {result['avg_similarity']:.3f}")

# # Evaluate on test set
# test_data = [
#     {"query": "What is...", "gold_answer": "..."},
#     # more test cases
# ]
# metrics = pipeline.evaluate_with_metrics(test_data)
# print(f"Exact Match: {metrics['exact_match']:.2%}")
# print(f"Average F1: {metrics['avg_f1']:.2%}")