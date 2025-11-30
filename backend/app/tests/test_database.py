from app.core.rag_pipeline import RAGPipeline

pipeline = RAGPipeline(similarity_threshold=0.5,embedder_model="sentence-transformers/all-MiniLM-L6-v2",language_model="TinyLlama/TinyLlama-1.1B-Chat-v1.0")

# Run query
result = pipeline.run(query="What is court act?", k= 10,max_input_length=2048, max_new_tokens=1500)
# max_input_length + max_new_tokens should be within model limits

# Access results
print(f"Answer: {result['answer']}")
print(f"Confidence: {result['confidence']:.2f}")
print(f"Sources used: {result['num_sources']}")
print(f"Avg similarity: {result['avg_similarity']:.3f}")