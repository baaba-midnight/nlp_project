import random

CLIMATE_FACTS = [
    "Global average surface temperature has increased about 1.1°C since the pre-industrial period.",
    "Atmospheric CO2 levels are over 410 parts per million — higher than at any time in the last 800,000 years.",
    "The last decade (2010–2019) was the warmest decade on record.",
    "Sea level has risen by about 20–25 cm since 1880; the rate is accelerating.",
    "Ocean acidification is increasing because the ocean absorbs CO2 from the atmosphere.",
    "Arctic sea ice extent has declined roughly 12% per decade since satellite records began.",
    "Permafrost thaw releases methane and CO2, which are potent greenhouse gases.",
    "Coral reefs are bleaching more frequently due to warmer and more acidic waters.",
    "Extreme weather events (storms, heatwaves, floods) have become more frequent and intense.",
    "Renewable energy costs (solar and wind) have dropped dramatically over the past decade.",
    "Deforestation contributes to carbon emissions and reduces biodiversity.",
    "Methane is about 25 times more potent than CO2 over a 100-year period.",
    "The Paris Agreement aims to limit global warming to well below 2°C, preferably 1.5°C.",
    "Agriculture contributes to greenhouse gas emissions, particularly methane from ruminants and nitrous oxide from fertilizer.",
    "Replacing just a fraction of fossil-fuel vehicles with electric vehicles reduces transport emissions."
]

def get_random_fact() -> str:
    """Return a randomized climate fact."""
    if not CLIMATE_FACTS:
        return "No facts available."
    return random.choice(CLIMATE_FACTS)

def get_fact(index: int) -> str:
    """Return a fact by index; wraps around if out of range."""
    if not CLIMATE_FACTS:
        return "No facts available."
    return CLIMATE_FACTS[index % len(CLIMATE_FACTS)]
