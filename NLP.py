import spacy
from spacy.matcher import Matcher, PhraseMatcher
from spacy.tokens import Span
import re
from typing import Optional, List, Dict, Any, Tuple
import logging


nlp = None

def init_nlp(model_name: str = "en_core_web_sm"):
    global nlp
    try:
        nlp = spacy.load(model_name)
    except OSError:
        # Model not found, download and load
        from spacy.cli import download
        download(model_name)
        nlp = spacy.load(model_name)

def parse_query(text: str) -> dict:
    """
    Notes: Analyze user query and return a dict with:
      - 'genre': Optional[str]
      - 'years': Optional[int]
      - 'ago': bool
      - raw text, entities
    :param text:
    :return:
    """
    doc = nlp(text)
    # TODO: Implement rules for parsing
    return {}