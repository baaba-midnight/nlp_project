from pydantic import BaseModel


class TranslationRequest(BaseModel):
    text: str
    source_lang: str = "twi"  # Default source language
    target_lang: str = "twi"  # Default target language
