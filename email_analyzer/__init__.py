"""
Email Analyzer Package

A Python package for analyzing Gmail emails using local LLM via Ollama
to identify company records involving procurement, legal, and decision making.
"""

from .email_processor import EmailProcessor
from .gmail_client import GmailClient
from .llm_analyzer import LLMAnalyzer
from .config import config

__version__ = "1.0.0"
__author__ = "Email Analyzer"

__all__ = [
    'EmailProcessor',
    'GmailClient', 
    'LLMAnalyzer',
    'config'
]

