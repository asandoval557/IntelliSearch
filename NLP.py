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

    current_year = datetime.datetime.now().year

    if ago_matches:
        result['ago'] = True
        years_ago = int(ago_matches[0])
        result['year_range'] = (current_year - years_ago, current_year)

    elif last_matches and last_matches[0]:
        result['ago'] = True
        amount = int(last_matches[0][0])
        unit = last_matches[0][1].lower()

        if 'decade' in unit:
            # Convert decades to years
            amount *= 10

        result['year_range'] = (current_year - amount, current_year)
    # Extract decade references ( "90s", "1900s")
    decade_pattern = r'\b(?:(?:19|20)(\d0)s|\b(\d0)s)\b'
    decade_matches = re.findall(decade_pattern, text)

    if decade_matches and not result.get('year_range'):
        decades = []
        for match in decade_matches:
            # Handle both "90s" and "1900s" formats
            if match[0]:
                decade = int("19" + match[0])
            else:
                prefix = "19" if int(match[1]) < 30 else "20"
                decade = int(prefix + match[1])

            decades.append(decade)

        if decades:
            min_decade = min(decades)
            max_decade = max(decades)
            result['year_range'] = (min_decade, min_decade + 9)
            if min_decade != max_decade:
                result['year_range'] = (min_decade, max_decade + 9)

    # Extract year ranges like "between 1990 and 2000" or "from 1990 to 2000"
    range_pattern = r'(?:between|from)\s+(19\d{2}|20\d{2})(?:\s+(?:to|and|until|through)\s+(19\d{2}|20\d{2}))?'
    range_matches = re.findall(range_pattern, text)

    if range_matches and not result.get('year_range'):
        match = range_matches[0]
        # Check if we have both start and end years (second group is not empty)
        if len(match) == 2 and match[1]:
            start_year, end_year = int(match[0]), int(match[1])
            result['year_range'] = (start_year, end_year)
        elif len(match) >= 1 and match[0]:
            start_year = int(match[0])
            # Treat "from 1990" as "from 1990 to present"
            result['year_range'] = (start_year, current_year)

    # Extract "after YEAR" or "before YEAR" patterns
    after_pattern = r'\b(?:after|since|following)\s+(19\d{2}|20\d{2})\b'
    after_matches = re.findall(after_pattern, text)

    before_pattern = r'\b(?:before|prior to|earlier than|until)\s+(19\d{2}|20\d{2})\b'
    before_matches = re.findall(before_pattern, text)

    if after_matches and not result.get('year_range'):
        year = int(after_matches[0])
        result['year_range'] = (year + 1, current_year)

    elif before_matches and not result.get('year_range'):
        year = int(before_matches[0])
        result['year_range'] = (1900, year - 1)  # Assuming 1900 as earliest possible year

    # If we just have individual years mentioned and no other year patterns matched
    elif years and not result.get('year_range'):
        years = [int(y) for y in years]
        if len(years) == 1:
            # Single year mentioned
            result['year_range'] = (years[0], years[0])
        elif len(years) >= 2:
            # Multiple years - use min and max as range
            result['year_range'] = (min(years), max(years))

    # Extract named entities
    for ent in doc.ents:
        result['entities'].append({
            'text': ent.text,
            'label': ent.label_,
            'start': ent.start_char,
            'end': ent.end_char
        })

     # Look for specific keywords that might indicate book attributes
    attribute_patterns = {
        'bestseller': r'\b(?:bestseller|best[\s-]seller|popular|top[\s-]selling)\b',
        'award_winning': r'\b(?:award[\s-]winning|prize[\s-]winning|acclaimed)\b',
        'new_release': r'\b(?:new[\s-]release|recently[\s-]published|latest|new)\b',
        'classic': r'\b(?:classic|timeless|iconic)\b'
    }

    for attr, pattern in attribute_patterns.items():
        if re.search(pattern, text.lower()):
            result[attr] = True

    # Check for author mentions
    author_pattern = r'\b(?:by|written by|author)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\b'
    author_matches = re.findall(author_pattern, text)

    if author_matches:
        result['author'] = author_matches[0]

    return result

def extract_filters_from_query(text: str) -> dict:
    """
    Extract filters for database query from natural language text.
    Returns a dictionary suitable for passing to query_books() function.
    """
    parsed = parse_query(text)
    filters = {}

    # Convert parsed data to database filter format
    if parsed.get('genre'):
        filters['genre'] = parsed['genre'][0] if isinstance(parsed['genre'], list) else parsed['genre']

    if parsed.get('year_range'):
        filters['year_start'] = parsed['year_range'][0]
        filters['year_end'] = parsed['year_range'][1]

    # Add other filters as needed
    for attr in ['bestseller', 'award_winning', 'new_release', 'classic']:
        if parsed.get(attr):
            filters[attr] = True

    if parsed.get('author'):
        filters['author'] = parsed['author']

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
