from app.core.rag_pipeline import RAGPipeline

pipeline = RAGPipeline(use_faiss=False)

# This SHOULD fail gracefully now
result = pipeline.run("What is love?", k=3)

print(f"Answer: {result['answer']}")
print(f"Error: {result.get('error', 'none')}")
if 'debug' in result:
    print(f"Debug: {result['debug']}")
