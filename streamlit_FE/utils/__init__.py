"""Utils package for the Climate Chat app.

Expose small utilities (chatbot, climate facts) at package level for convenience.
"""
from .climate_facts import get_random_fact, get_fact
from .chatbot import get_response

__all__ = ["get_random_fact", "get_fact", "get_response"]