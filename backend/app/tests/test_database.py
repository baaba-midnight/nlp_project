# test_database.py
from app.core.rag_pipeline import RAGPipeline


COLAB_URL = "https://miquel-nonintersecting-pachydermatously.ngrok-free.dev/"

pipeline = RAGPipeline(
    similarity_threshold=0.5,
    embedder_model="sentence-transformers/all-MiniLM-L6-v2",
    language_model="alotanna/llama2-7b-ghana-climate",
    use_colab_api=True,  
    colab_url=COLAB_URL 
)

test_questions = [
    "What is Ghana doing about climate change?",
    "What are Ghana's renewable energy targets?",
    "What laws protect Ghana's forests?",
    "How can farmers adapt to climate change in Ghana?",
    "What are the penalties for illegal mining in Ghana?",
    "What is the Bank of Ghana's role in the economy?",
    "How does Ghana's Environmental Protection Act work?"
]

for question in test_questions:
    print(f"\nQ: {question}")
    result = pipeline.run(
        query=question,
        k=10,
        max_input_length=2048,
        max_new_tokens=512
    )
    print(f"A: {result['answer']}")
    print(f"Confidence: {result['confidence']:.2f} | Sources: {result['num_sources']}")
    print("-" * 70)
