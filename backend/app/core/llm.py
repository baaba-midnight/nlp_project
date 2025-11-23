"""
Llama-2 LLM wrapper for RAG generation
"""
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch


class Llama2LLM:
    def __init__(self, model_name: str = "meta-llama/Llama-2-7b-chat-hf"):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"

        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForCausalLM.from_pretrained(
            model_name,
            torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
            device_map="auto"
        )

    def generate(self, prompt: str, max_new_tokens: int = 512) -> str:
        inputs = self.tokenizer(prompt, return_tensors="pt").to(self.device)

        output = self.model.generate(
            **inputs,
            max_new_tokens=max_new_tokens,
            pad_token_id=self.tokenizer.eos_token_id,
            temperature=0.2,
            do_sample=False
        )

        return self.tokenizer.decode(output[0], skip_special_tokens=True)
