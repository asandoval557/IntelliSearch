import spacy
from spacy.matcher import Matcher, PhraseMatcher
from spacy.tokens import Span
import re
from typing import Optional, List, Dict, Any, Tuple
import logging
import datetime

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
    logging.info(f"Loaded NLP model: {model_name}")

def parse_query(text: str) -> dict:
    """
    Notes: Analyze user query and return a dict with:
      - 'genre': Optional[str] or List[str]
      - 'years': Optional[Tuple[int, int]]
      - 'ago': bool - Whether the query references time relative to now
      - 'entities': List of recognized entities
      - raw text: Original query text

    Examples:
      - "Show me science fiction books from the 1990s"
      - "I want to read romance novels published after 2010"
      - "Find books about dragons written in the last 5 years"
    """

    if nlp is None:
        init_nlp()

    result = {
        'genre': None,
        'years_range': None,
        'ago': False,
        'entities': [],
        'raw': text
    }

    doc = nlp(text.lower())
    # TODO: Implement rules for parsing
    # Extract genres
    genres = ["science fiction", "sci-fi", "fantasy", "mystery", "thriller", "romance",
              "historical fiction", "non-fiction", "biography", "self-help",
              "horror", "adventure", "children's", "young adult", "poetry",
              "drama", "classic", "dystopian", "memoir", "philosophy", "science"]

    # Create phase mather for genres
    genre_matcher = PhraseMatcher(nlp.vocab, attr="LOWER")
    patterns = [nlp(genre) for genre in genres]
    genre_matcher.add("GENRE", patterns)

    # Find genres in text
    found_genres = []
    for match_id, start, end in genre_matcher(doc):
        span = doc[start:end]
        found_genres.append(span.text)

    if found_genres:
        result['genre'] = found_genres

    # Extract year preferences
    year_pattern = r'\b(19\d{2}|20\d{2})\b'  # Match years from 1900-2099
    years = re.findall(year_pattern, text)

    # Extract relative time reference
    ago_pattern = r'\b(\d+)\s+years?\s+ago\b'
    ago_matches = re.findall(ago_pattern, text)

    last_pattern = r'\b(?:in the |during the |from the |within the |over the |throughout the )?(?:last|past)\s+(\d+)\s+(years?|decades?)\b'
    last_matches = re.findall(last_pattern, text)

    current_year =- datetime.datetime.now().year

    if ago_matches:
        result['ago'] = True
        years_ago = int(ago_matches[0])
        result['year_range'] = (current_year - current_year, current_year)





    return result