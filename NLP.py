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

    # Create phrase matcher for genres
    genre_matcher = PhraseMatcher(nlp.vocab, attr="LOWER")
    patterns = [nlp(genre) for genre in genres]
    genre_matcher.add("GENRE", patterns)

    # Find genres in text
    found_genres = []
    for match_id, start, end in genre_matcher(doc):
        span = doc[start:end]
        found_genre = span.text

        if found_genre in ["sci-fi", "sci fi"]:
            found_genre = "science fiction"

        found_genres.append(found_genre)

    if found_genres:
        result['genre'] = found_genres
        print(f"Found genre: {found_genres}") #debug output

    # Extract year preferences, updating pattern
    current_year = datetime.datetime.now().year

    # Pattern for decades
    decade_pattern = r'\b(?:(19|20)(\d0)s|(\d0)s)\b'
    decade_matches = re.finditer(decade_pattern, text.lower())

    if decade_matches:
        print(f"Found {len(decade_matches)} decade matches") # debug output
        for match in decade_matches:
            if match[0] and match[1]:
                decade_start = int(match[0] + match[1])
            elif match[2]:
                decade_num = int(match[2])
                if decade_num >= 50:
                    decade_start = 1900+ decade_num
                else:
                    decade_start = 2000+ decade_num

            result['years_range'] = (decade_start, decade_start + 9)
            print(f"Set year range for decade: {result['years_range']}") # debug output
            break

    # Pattern for "after year"
    if not result.get('years_range'):
        after_pattern = r'(?:after|since|from)\s+(19\d{2}|20\d{2})'
        after_match = re.search(after_pattern, text.lower())
        if after_match:
            year = int(after_match.group(1))
            result['years_range'] = (year, current_year)
            print(f"Set year range for year: {result['years_range']}")  # debug output

    # Pattern for "before year"
    if not result.get('years_range'):
        before_pattern = r'(?:before|until)\s+(19\d{2}|20\d{2})'
        before_match = re.search(before_pattern, text.lower())
        if before_match:
            year = int(before_match.group(1))
            result['years_range'] = (1900, current_year)
            print(f"Set year range for year: {result['years_range']}")  # debug output

    # Pattern for "last x years"




def extract_filters_from_query(text: str) -> dict:
    """
    Extract filters for database query from natural language text.
    Returns a dictionary suitable for passing to query_books() function.
    """
    parsed = parse_query(text)
    filters = {}

    # Adding debug output
    print("Parsed query result:", parsed)

    # Convert parsed data to database filter format
    if parsed.get('genre'):
        # Get the genres(s) from the parsed result
        genre = parsed['genre']
        print("Genre from parsed query:", genre) # Debug Output

        # Normalize genre to match database format (capitalize first letter of each word)
        if isinstance(genre, list):
            # If we have a list of genres, normalize each one
            normalized_genres = []
            for g in genre:
                # Title case for multi-word  genres like "Science Fiction"
                if ' ' in g:
                    normalized_genres.append(' '.join(word.capitalize() for word in g.split(' ')))
                else:
                    normalized_genres.append(g.capitalize())
            filters['genre'] = normalized_genres
        else:
            # If we have a single genre string
            if ' ' in genre:
                filters['genre'] = ' '.join(word.capitalize() for word in genre.split())
            else:
                filters['genre'] = genre.capitalize()

    if parsed.get('year_range'):
        filters['year_start'] = parsed['year_range'][0]
        filters['year_end'] = parsed['year_range'][1]

    # Add other filters as needed
    for attr in ['bestseller', 'award_winning', 'new_release', 'classic']:
        if parsed.get(attr):
            filters[attr] = True

    if parsed.get('author'):
        filters['author'] = parsed['author']

    print("Final filters:", filters) #Debug output

    return filters

# Adding function for test script
def process_natural_language_query(text: str) -> dict:
    """
    Main entry point function to process a natural language query
    and return a database filter dict ready for query_books()

    This is a wrapper around extract_filters_from_query for consistency
    with the test script.
    """
    return extract_filters_from_query(text)
