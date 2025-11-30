import random

_REPLY_TEMPLATES = {
    "greeting": [
        "Hello! I can help with climate facts, drivers, impacts, and solutions. Ask me anything.",
        "Hi there! Ask me about climate change, impacts, or how to reduce emissions."
    ],
    "climate": [
        "Climate change refers to long-term shifts in temperatures and weather patterns, often driven by greenhouse gas emissions.",
        "Rising CO2 and other greenhouse gases trap heat in the atmosphere, causing global temperatures to increase."
    ],
    "sea_level": [
        "Sea level rise is caused by melting ice and expansion of warming ocean water. Coastal communities are at risk."
    ],
    "renewable": [
        "Renewable energy (solar, wind, hydro) can replace fossil fuels and help reduce emissions."
    ],
    "co2": [
        "CO2 is the primary greenhouse gas emitted by human activities, mostly from burning fossil fuels and deforestation."
    ],
    "default": [
        "I can provide quick climate facts and simple help. Try asking about impacts, greenhouse gases, sea-level rise, or renewables.",
        "If you want more detailed information, I can provide references or you can connect a model backend."
    ]
}

def get_response(message: str) -> str:
    """Return a short rule-based response for quick front-end testing."""
    if not message:
        return "Please enter a message."
    msg = message.lower()
    if any(w in msg for w in ("hi", "hello", "hey")):
        return random.choice(_REPLY_TEMPLATES["greeting"])
    if any(w in msg for w in ("climate", "climate change", "warming")):
        return random.choice(_REPLY_TEMPLATES["climate"])
    if "sea" in msg and "level" in msg:
        return random.choice(_REPLY_TEMPLATES["sea_level"])
    if any(w in msg for w in ("renewable", "solar", "wind", "hydro")):
        return random.choice(_REPLY_TEMPLATES["renewable"])
    if any(w in msg for w in ("co2", "carbon dioxide", "carbon")):
        return random.choice(_REPLY_TEMPLATES["co2"])
    # fallback
    return random.choice(_REPLY_TEMPLATES["default"])
