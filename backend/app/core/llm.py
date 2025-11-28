from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

class Llama2LLM:
    def __init__(self, model_name: str = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"):
        # TinyLlama/TinyLlama-1.1B-Chat-v1.0
        self.device = "cpu"
        
        # Load tokenizer
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        
        # Set pad_token if it doesn't exist (common issue with Llama)
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token
        
        # # Configure 4-bit quantization
        # bnb_config = BitsAndBytesConfig(
        #     load_in_4bit=True,
        #     bnb_4bit_compute_dtype=torch.float16,
        #     bnb_4bit_use_double_quant=False,
        #     bnb_4bit_quant_type="nf4"
        # )

        # Load 4-bit quantized model
        self.model = AutoModelForCausalLM.from_pretrained(
            model_name,
            torch_dtype=torch.float16,
            low_cpu_mem_usage=True,
            device_map=None,
            trust_remote_code=True
        ).to(self.device)

    def generate(self, prompt: str, max_new_tokens: int = 512) -> str:
        inputs = self.tokenizer(prompt, return_tensors="pt").to(self.device)

        output = self.model.generate(
            **inputs,
            max_new_tokens=max_new_tokens,
            pad_token_id=self.tokenizer.pad_token_id,
            temperature=0.2,
            do_sample=False  
        )

        # Remove the input prompt from the output
        generated_text = self.tokenizer.decode(output[0], skip_special_tokens=True)
        return generated_text[len(prompt):].strip()