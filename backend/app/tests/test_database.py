# test_database.py
from ..core.rag_pipeline import RAGPipeline


COLAB_URL = "https://miquel-nonintersecting-pachydermatously.ngrok-free.dev/"

pipeline = RAGPipeline(
    similarity_threshold=0.5,
    embedder_model="sentence-transformers/all-MiniLM-L6-v2",
    language_model="alotanna/llama2-7b-ghana-NLP",
    use_colab_api=True,  
    colab_url=COLAB_URL 
)

test_questions = [
    "how does Ghana address sexual harassment"
]

for question in test_questions:
    print(f"\nQ: {question}")
    result = pipeline.run(
        query=question,
        k=10
    )
    print(f"A: {result['answer']}")
    print(f"Confidence: {result['has_chunks']} | Sources: {result['num_sources']}")
    print("-" * 70)
