"""
Language Model for answer generation in RAG pipeline.
Based on Jurafsky & Martin (2025) - Chapter 14: Question Answering and RAG
"""
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch
from typing import Optional


class Llama2LLM:
    """
    Language Model for answer generation in RAG pipeline.
    Implements retrieval-augmented generation as described in Section 14.3.1
    """
    
    def __init__(self, model_name: str = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"):
        """
        Initialize the language model.
        
        Args:
            model_name: HuggingFace model identifier
        """
        # Detect device and set appropriate dtype
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        dtype = torch.float16 if self.device == "cuda" else torch.float32
        
        # Load tokenizer
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        
        # Set pad_token if it doesn't exist
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token
        
        # Load model
        self.model = AutoModelForCausalLM.from_pretrained(
            model_name,
            torch_dtype=dtype,
            low_cpu_mem_usage=True,
            device_map=None,
            trust_remote_code=True
        ).to(self.device)
        
        self.model.eval()
    
    def generate(self, prompt: str, max_new_tokens: int = 512) -> str:
        """
        Generate answer using retrieval-augmented generation.
        Implements conditional generation: p(x_i | R(q); prompt; [Q:]; q; [A:]; x_<i)
        
        Args:
            prompt: Input prompt with context and question
            max_new_tokens: Maximum tokens to generate
            
        Returns:
            Generated text answer
        """
        # Tokenize input
        inputs = self.tokenizer(
            prompt, 
            return_tensors="pt", 
            truncation=True, 
            max_length=2048
        ).to(self.device)
        
        input_length = inputs['input_ids'].shape[1]
        
        # Generate with appropriate parameters for factual QA
        with torch.no_grad():
            output = self.model.generate(
                **inputs,
                max_new_tokens=max_new_tokens,
                pad_token_id=self.tokenizer.pad_token_id,
                temperature=0.3,  # Lower temperature for more factual answers
                do_sample=True,
                top_p=0.85,
                repetition_penalty=1.15,
                no_repeat_ngram_size=3  # Avoid repeating trigrams
            )
        
        # Decode only the generated tokens
        generated_ids = output[0][input_length:]
        generated_text = self.tokenizer.decode(generated_ids, skip_special_tokens=True)
        
        return generated_text.strip()