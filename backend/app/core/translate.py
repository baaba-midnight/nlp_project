from transformers import AutoModelForSeq2SeqLM, AutoTokenizer

class GhanaianTranslator:
    def __init__(self):
        model_name = "facebook/nllb-200-distilled-600M"
        self.model = AutoModelForSeq2SeqLM.from_pretrained(model_name)
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)

        # NLLB language codes for Ghanaian languages
        self.lang_codes = {
            'twi': 'aka_Latn',  # Akan/Twi
            'ewe': 'ewe_Latn',  # Ewe
            'english': 'eng_Latn'
        }

    def translate_to_english(self, text, source_lang='twi'):
        """Translate from Ghanaian language to English"""
        source_code = self.lang_codes[source_lang]
        target_code = self.lang_codes['english']

        self.tokenizer.src_lang = source_code
        inputs = self.tokenizer(text, return_tensors="pt")

        translated_tokens = self.model.generate(
            **inputs,
            forced_bos_token_id=self.tokenizer.convert_tokens_to_ids(target_code),
            max_length=512
        )

        translation = self.tokenizer.batch_decode(
            translated_tokens,
            skip_special_tokens=True
        )[0]

        return translation

    def translate_from_english(self, text, target_lang='twi'):
        """Translate from English to Ghanaian language"""
        source_code = self.lang_codes['english']
        target_code = self.lang_codes[target_lang]

        self.tokenizer.src_lang = source_code
        inputs = self.tokenizer(text, return_tensors="pt")

        translated_tokens = self.model.generate(
            **inputs,
            forced_bos_token_id=self.tokenizer.convert_tokens_to_ids(target_code),
            max_length=512
        )

        translation = self.tokenizer.batch_decode(
            translated_tokens,
            skip_special_tokens=True
        )[0]

        return translation