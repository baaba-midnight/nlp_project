"""
Language Model for answer generation in RAG pipeline.
Now supports Google Colab API!
"""
from transformers import AutoTokenizer
import torch
import requests

class Llama2LLM:
    """
    Language Model for answer generation in RAG pipeline.
    Supports: Local, HuggingFace API, and Google Colab API
    """
    def __init__(self, language_model,use_colab_api, colab_url):
        """
        Initialize the language model.

        Args:
            language_model: Model name or path
            use_hf_api: If True, use HuggingFace Inference API
            hf_token: Your HuggingFace token
            use_colab_api: If True, use Google Colab API
            colab_url: Your Colab ngrok URL (e.g., "https://xxxx.ngrok.io")
        """
        self.language_model = language_model
        self.use_colab_api = use_colab_api
        self.colab_url = colab_url
        
        # Always load tokenizer (needed for token counting)
        print(f"Loading tokenizer: {language_model}")
        self.tokenizer = AutoTokenizer.from_pretrained(language_model)
        
        if use_colab_api:
            # Use Google Colab API
            if not colab_url:
                raise ValueError("Must provide colab_url when use_colab_api=True")
            
            print(f"Using Google Colab API: {colab_url}")
            
            # Test connection
            try:
                response = requests.get(f"{colab_url}/health", timeout=10)
                if response.status_code == 200:
                    print(" Connected to Colab API successfully!")
                    print(f"   Model: {response.json().get('model', 'Unknown')}")
                else:
                    print(f"Colab API returned status {response.status_code}")
            except Exception as e:
                print(f"Could not connect to Colab API: {e}")
            
            self.device = "colab_api"
            
        else:
            # Load model locally
            print(f"Loading model locally: {language_model}")
            
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
            dtype = torch.float16 if self.device == "cuda" else torch.float32
            
            if self.device == "cpu":
                print("Running on CPU")
            
            from transformers import AutoModelForCausalLM
            self.model = AutoModelForCausalLM.from_pretrained(
                language_model,
                torch_dtype=dtype,
                low_cpu_mem_usage=True,
                device_map=None,
                trust_remote_code=True
            ).to(self.device)
            
            self.model.eval()
            print(f"Model loaded on: {self.device}")
    
    def generate(self, prompt, max_new_tokens):
        """
        Generate answer using retrieval-augmented generation.
        
        Args:
            prompt: Input prompt with context and question
            max_new_tokens: Maximum tokens to generate

        Returns:
            Generated text answer
        """
        if self.use_colab_api:
            # Use Google Colab API
            try:
                response = requests.post(
                    f"{self.colab_url}/generate",
                    json={
                        "prompt": prompt,
                        "max_new_tokens": max_new_tokens,
                        "temperature": 0.3,
                        "top_p": 0.85,
                        "repetition_penalty": 1.15
                    },
                    timeout=120  # 2 minutes timeout
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return data.get("generated_text", "").strip()
                else:
                    error_msg = f"Colab API error (status {response.status_code})"
                    print(f"{error_msg}")
                    return f"Error: {error_msg}"
                    
            except requests.Timeout:
                print("Colab API timeout - request took too long")
                return "Error: Request timeout. The prompt might be too long."
            except requests.ConnectionError:
                print("Could not connect to Colab API")
                return "Error: Could not connect to Colab. Is the notebook still running?"
            except Exception as e:
                print(f"Colab API Error: {str(e)}")
                return f"Error: {str(e)}"
        
        else:
            # Use local model
            inputs = self.tokenizer(prompt, return_tensors="pt").to(self.device)
            input_length = inputs['input_ids'].shape[1]
            
            with torch.no_grad():
                output = self.model.generate(
                    **inputs,
                    max_new_tokens=max_new_tokens,
                    pad_token_id=self.tokenizer.pad_token_id,
                    temperature=0.3,
                    do_sample=True,
                    top_p=0.85,
                    repetition_penalty=1.15,
                    no_repeat_ngram_size=3
                )
            
            generated_ids = output[0][input_length:]
            generated_text = self.tokenizer.decode(generated_ids, skip_special_tokens=True)
            return generated_text.strip()