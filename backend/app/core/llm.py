"""
Language Model for answer generation in RAG pipeline.
Supports Colab API with TinyLlama fallback.
"""
from transformers import AutoTokenizer
import torch
import requests

class Llama2LLM:
    """
    Language Model with automatic fallback.
    Primary: Colab API (fast)
    Fallback: TinyLlama local (if Colab fails)
    """
    def __init__(self, language_model, use_colab_api=False, colab_url=None, 
                 fallback_model="TinyLlama/TinyLlama-1.1B-Chat-v1.0"):
        """
        Initialize the language model with fallback support.
        
        Args:
            language_model: Primary model name (for Colab API)
            use_colab_api: If True, use Google Colab API as primary
            colab_url: Colab ngrok URL
            fallback_model: Local model to use if Colab fails (default: TinyLlama)
        """
        self.language_model = language_model
        self.use_colab_api = use_colab_api
        self.colab_url = colab_url
        self.fallback_model = fallback_model
        self.colab_available = False
        self.local_model = None
        self.local_tokenizer = None
        
        # Set token limits based on model type
        self.max_input_length = 2048  # Default for llama2
        self.max_output_length = 2048  # Default for llama2
        # Load tokenizer for Colab API usage
        self.tokenizer = AutoTokenizer.from_pretrained(language_model)
        
        if use_colab_api:
            if not colab_url:
                raise ValueError("Must provide colab_url when use_colab_api=True")
            # Check Colab API availability
            try:
                response = requests.get(f"{colab_url}/health", timeout=10)
                if response.status_code == 200:
                    self.colab_available = True
                else:
                    print(f"Colab API returned status {response.status_code}")
            except Exception as e:
                print(f"Cannot connect to Colab API: {e}, loading local fallback model")
            # Load fallback model if Colab is not available
            if not self.colab_available:
                self._load_fallback_model()
            
            self.device = "colab_api" if self.colab_available else "local_fallback"
        else:
            print("Loading local model directly (no Colab API)")
            self._load_fallback_model()
            self.device = "local"
    
    def _load_fallback_model(self):
        """Load TinyLlama as fallback model"""
        from transformers import AutoModelForCausalLM
        
        # Update token limits for TinyLlama
        self.max_input_length = 1024
        self.max_output_length = 1024        
        
        # Load tokenizer and model
        self.local_tokenizer = AutoTokenizer.from_pretrained(self.fallback_model)
        # Determine device and dtype
        device = "cuda" if torch.cuda.is_available() else "cpu"
        dtype = torch.float16 if device == "cuda" else torch.float32
        # Load model
        self.local_model = AutoModelForCausalLM.from_pretrained(
            self.fallback_model,
            torch_dtype=dtype,
            low_cpu_mem_usage=True,
            device_map=None,
            trust_remote_code=True
        ).to(device)
        # Set model to eval mode
        self.local_model.eval()
        self.local_device = device
    
    def get_max_input_length(self):
        """Get the maximum input length for the current model"""
        return self.max_input_length
    
    def generate(self, prompt):
        """
        Generate answer with automatic fallback.
        Tries Colab API first, falls back to local TinyLlama if it fails.
        
        Args:
            prompt: Input prompt with context and question
            
        Returns:
            Generated text answer
        """
        # Try Colab API first
        if self.use_colab_api and self.colab_available:
            try:
                response = requests.post(
                    f"{self.colab_url}/generate",
                    json={
                        "prompt": prompt,
                        "max_new_tokens": self.max_output_length,
                        "temperature": 0.2,
                        "top_p": 0.9,
                        "repetition_penalty": 1.05
                    },
                    timeout=120
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return data.get("generated_text", "").strip()
            # Handle Colab API errors and fall back        
            except requests.Timeout:
                print("Colab API timeout")
                print("Falling back to local TinyLlama")
            except requests.ConnectionError:
                print("Cannot connect to Colab API")
                print("Falling back to local TinyLlama")
            except Exception as e:
                print(f"Colab API Error: {str(e)}")
                print("Falling back to local TinyLlama")
            
            if self.local_model is None:
                print("Loading fallback model now")
                self._load_fallback_model()
        # Fallback to local TinyLlama
        if self.local_model is None:
            return "Error: No model available (Colab failed and fallback not loaded)"
        
        inputs = self.local_tokenizer(prompt, return_tensors="pt").to(self.local_device)
        input_length = inputs['input_ids'].shape[1]
        
        with torch.no_grad():
            output = self.local_model.generate(
                **inputs,
                max_new_tokens=self.max_output_length,
                pad_token_id=self.local_tokenizer.pad_token_id,
                temperature=0.3,
                do_sample=True,
                top_p=0.9,
                repetition_penalty=1.05,
                no_repeat_ngram_size=3
            )
        
        generated_ids = output[0][input_length:]
        generated_text = self.local_tokenizer.decode(generated_ids, skip_special_tokens=True)
        
        return generated_text.strip()