from fastapi import APIRouter, HTTPException

from ..core.translate import GhanaianTranslator
from ..models.translate import TranslationRequest

router = APIRouter(prefix="/translate", tags=["translate"])
translator = GhanaianTranslator()


@router.post("/to_english")
async def translate_to_english(request: TranslationRequest):
    """Translate from Ghanaian language to English"""
    try:
        source_lang = request.source_lang
        text = request.text
        translation = translator.translate_to_english(text, source_lang=source_lang)
        return {"translation": translation}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/from_english")
async def translate_from_english(request: TranslationRequest):
    """Translate from English to Ghanaian language"""
    try:
        target_lang = request.target_lang
        text = request.text
        translation = translator.translate_from_english(text, target_lang=target_lang)
        return {"translation": translation}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
