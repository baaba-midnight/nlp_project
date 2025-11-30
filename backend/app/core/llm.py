"""
Language Model for answer generation in RAG pipeline.
"""
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

class Llama2LLM:
    """
    Language Model for answer generation in RAG pipeline.
    Implements retrieval-augmented generation 
    """
    def __init__(self, language_model):
        """
        Initialize the language model.
        
        Args:
            language_model: Model name or path for LLM in string format
        """
        # Detect device and set appropriate dtype
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.language_model = language_model
        dtype = torch.float16 if self.device == "cuda" else torch.float32
        
        # Load tokenizer
        self.tokenizer = AutoTokenizer.from_pretrained(language_model)
        
        # Load model
        self.model = AutoModelForCausalLM.from_pretrained(language_model, torch_dtype=dtype,low_cpu_mem_usage=True,device_map=None,trust_remote_code=True).to(self.device)
        
        self.model.eval()
    
    def generate(self, prompt, max_new_tokens):
        """
        Generate answer using retrieval-augmented generation.
        Implements conditional generation with context from retrieved passages.
        
        Args:
            prompt: Input prompt with context and question
            max_new_tokens: Maximum tokens to generate
            
        Returns:
            Generated text answer
        """
        # Tokenize input
        inputs = self.tokenizer(prompt, return_tensors="pt").to(self.device)
        
        input_length = inputs['input_ids'].shape[1]
        
        # Generate answer
        with torch.no_grad():
            output = self.model.generate(**inputs,max_new_tokens=max_new_tokens,pad_token_id=self.tokenizer.pad_token_id,temperature=0.3, do_sample=True,top_p=0.85,repetition_penalty=1.15,no_repeat_ngram_size=3)
        # Decode only the generated tokens
        generated_ids = output[0][input_length:]
        generated_text = self.tokenizer.decode(generated_ids, skip_special_tokens=True)

        return generated_text.strip()