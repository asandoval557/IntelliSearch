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
      - 'has_searchable_content': bool - Whether query has actionable search terms

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
        'raw': text,
        'has_searchable_content': False
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
        result['has_searchable_content'] = True
        print(f"Found genre: {found_genres}")  # debug output

    # Extract year preferences, updating pattern
    current_year = datetime.datetime.now().year

    # Pattern for decades
    decade_pattern = r'\b(?:(19|20)(\d0)s|(\d0)s)\b'
    decade_matches = list(re.finditer(decade_pattern, text.lower()))

    if decade_matches:
        print(f"Found {len(decade_matches)} decade matches")  # debug output
        result['has_searchable_content'] = True
        for match in decade_matches:
            groups = match.groups()
            print(f"Decade match groups: {groups}")  # debug output

            if groups[0] and groups[1]:
                decade_start = int(groups[0] + groups[1])
            elif groups[2]:
                decade_num = int(groups[2])
                if decade_num >= 50:
                    decade_start = 1900 + decade_num
                else:
                    decade_start = 2000 + decade_num
            else:
                continue

                result['year_range'] = (decade_start, decade_start + 9)
                print(f"Set year range for decade: {result['year_range']}")  # debug output
                break

    # Pattern for "after year"
    if not result.get('year_range'):
        after_pattern = r'(?:after|since|from)\s+(19\d{2}|20\d{2})'
        after_match = re.search(after_pattern, text.lower())
        if after_match:
            year = int(after_match.group(1))
            result['year_range'] = (year, current_year)
            result['has_searchable_content'] = True
            print(f"Set year range for year: {result['year_range']}")  # debug output

    # Pattern for "before year"
    if not result.get('year_range'):
        before_pattern = r'(?:before|until)\s+(19\d{2}|20\d{2})'
        before_match = re.search(before_pattern, text.lower())
        if before_match:
            year = int(before_match.group(1))
            result['year_range'] = (1900, current_year)
            result['has_searchable_content'] = True
            print(f"Set year range for year: {result['year_range']}")  # debug output

    # Pattern for "last x years"
    if not result.get('year_range'):
        last_years_pattern = r'(?:last|past)\s+(\d+)\s+years?'
        last_match = re.search(last_years_pattern, text.lower())
        if last_match:
            years_back = int(last_match.group(1))
            result['year_range'] = (current_year - years_back, current_year)
            result['ago'] = True
            result['has_searchable_content'] = True
            print(f"Set year range for 'last X years': {result['year_range']}")  # Debug

        # Pattern for specific years
    if not result.get('year_range'):
        year_pattern = r'\b(19\d{2}|20\d{2})\b'
        years = re.findall(year_pattern, text)
        if years:
            years = [int(y) for y in years]
            if len(years) == 1:
                result['year_range'] = (years[0], years[0])
            else:
                result['year_range'] = (min(years), max(years))
            result['has_searchable_content'] = True
            print(f"Set year range for specific years: {result['year_range']}")  # Debug

        # Extract named entities
    for ent in doc.ents:
        result['entities'].append({
            'text': ent.text,
            'label': ent.label_,
            'start': ent.start_char,
            'end': ent.end_char
        })

    return result


def extract_filters_from_query(text: str) -> dict:
    """
    Extract filters for database query from natural language text.
    Returns a dictionary suitable for passing to query_books() function.

    Returns:
    - dict with actual filters if searchable content found
    - {'no_results': True} if query has no searchable content
    - {'help_request': True} if user is asking for help/instructions
    - {'clear_request': True} if user wants to clear results
    - {'exit_request': True} if user wants to exit the program
    """

    # Check for clear command first
    if is_clear_request(text):
        return {'clear_request': True}

    # Check for exit command
    if is_exit_request(text):
        return {'exit_request': True}

    # Check for help requests
    if is_help_request(text):
        return {'help_request': True}

    parsed = parse_query(text)
    filters = {}

    # Adding debug output
    print("Parsed query result:", parsed)

    # Convert parsed data to database filter format
    if parsed.get('genre'):
        # Get the genres(s) from the parsed result
        genres = parsed['genre']
        print("Genre from parsed query:", genres)  # Debug Output

        # Normalize genres to match database format exactly
        normalized_genres = []

        if isinstance(genres, list):
            for genre in genres:
                normalized = normalize_genre(genre)
                if normalized:
                    normalized_genres.append(normalized)
        else:
            normalized = normalize_genre(genres)
            if normalized:
                normalized_genres.append(normalized)

        if normalized_genres:
            filters['genre'] = normalized_genres
            print("Normalized genres for database:", normalized_genres)  # Debug

        # Handle year ranges
    if parsed.get('year_range'):
        filters['year_start'] = parsed['year_range'][0]
        filters['year_end'] = parsed['year_range'][1]
        print(f"Year range filter: {filters['year_start']}-{filters['year_end']}")  # Debug

    # Check if we found any searchable content
    if not parsed.get('has_searchable_content'):
        # No recognizable search terms found
        print("No searchable content found in query")
        return {'no_results': True}

    print("Final filters for database:", filters)  # Debug
    return filters


def normalize_genre(genre_text: str) -> str:
    """
    Normalize genre text to match database format exactly.
    Based on your database genres: Science Fiction, Fantasy, Mystery, etc.
    """
    # Convert to lowercase for matching
    genre_lower = genre_text.lower().strip()

    # Map variations to exact database format
    genre_mapping = {
        'science fiction': 'Science Fiction',
        'sci-fi': 'Science Fiction',
        'sci fi': 'Science Fiction',
        'fantasy': 'Fantasy',
        'mystery': 'Mystery',
        'thriller': 'Thriller',
        'romance': 'Romance',
        'historical fiction': 'Historical Fiction',
        'non-fiction': 'Non-Fiction',
        'biography': 'Biography',
        'self-help': 'Self-Help',
        'self help': 'Self-Help',
        'horror': 'Horror',
        'adventure': 'Adventure',
        'children\'s': 'Children\'s',
        'childrens': 'Children\'s',
        'young adult': 'Young Adult',
        'poetry': 'Poetry',
        'drama': 'Drama',
        'classic': 'Classic',
        'dystopian': 'Dystopian',
        'memoir': 'Memoir',
        'philosophy': 'Philosophy',
        'science': 'Science'
    }

    return genre_mapping.get(genre_lower, None)


# Adding function for test script
def process_natural_language_query(text: str) -> dict:
    """
    Main entry point function to process a natural language query
    and return a database filter dict ready for query_books()

    This is a wrapper around extract_filters_from_query for consistency
    with the test script.
    """
    return extract_filters_from_query(text)


def has_book_related_keywords(text: str) -> bool:
    """
    Check if the query contains book-related keywords that might indicate
    a legitimate search even if no specific genre/year filters are found.
    """
    book_keywords = [
        'book', 'books', 'novel', 'novels', 'read', 'reading',
        'author', 'story', 'stories', 'literature', 'fiction',
        'recommend', 'recommendation', 'suggest', 'find'
    ]

    text_lower = text.lower()
    return any(keyword in text_lower for keyword in book_keywords)


def is_help_request(text: str) -> bool:
    """
    Check if the user is asking for help or instructions about what the system can do.
    """
    help_patterns = [
        r'\bwhat can you do\b',
        r'\bwhat do you do\b',
        r'\bhow do you work\b',
        r'\bwhat are your capabilities\b',
        r'\bwhat can I ask\b',
        r'\bwhat can I search for\b',
        r'\bhelp\b',
        r'\bcommands\b',
        r'\binstructions\b',
        r'\bhow to use\b',
        r'\bhow does this work\b',
        r'\bwhat questions can I ask\b',
        r'\bwhat kind of search\b',
        r'\bwhat formats\b'
    ]

    text_lower = text.lower().strip()

    # Check for exact matches or pattern matches
    for pattern in help_patterns:
        if re.search(pattern, text_lower):
            return True

    return False


def is_clear_request(text: str) -> bool:
    """
    Check if the user wants to clear the chat results.
    """
    clear_patterns = [
        r'\bclear my results\b',
        r'\bclear results\b',
        r'\bclear chat\b',
        r'\bclear screen\b',
        r'\bclear all\b',
        r'\breset chat\b',
        r'\bstart over\b',
        r'\bclear everything\b'
    ]

    text_lower = text.lower().strip()

    # Check for exact matches or pattern matches
    for pattern in clear_patterns:
        if re.search(pattern, text_lower):
            return True

    return False


def is_exit_request(text: str) -> bool:
    """
    Check if the user wants to exit the program.
    """
    exit_patterns = [
        r'\bexit\b',
        r'\bquit\b',
        r'\bclose\b',
        r'\bbye\b',
        r'\bgoodbye\b',
        r'\bstop\b',
        r'\bend\b',
        r'\bleave\b'
    ]

    text_lower = text.lower().strip()

    # Check for exact matches or pattern matches
    for pattern in exit_patterns:
        if re.search(pattern, text_lower):
            return True

    return False


def get_help_message() -> str:
    """
    Return a comprehensive help message explaining what the system can do.
    """
    help_text = """I can help you search for books in our database! Here's what I can do:

📚 SEARCH BY GENRE:
• "Show me fantasy books"
• "Find science fiction novels"
• "I want to read mystery books"

📅 SEARCH BY TIME PERIOD:
• "Books from the 1990s"
• "Novels published after 2010"
• "Show me books from the last 5 years"

🔍 COMBINE SEARCHES:
• "Fantasy books from the 1980s"
• "Science fiction novels after 2000"

📖 SUPPORTED GENRES:
Science Fiction, Fantasy, Mystery, Thriller, Romance, Historical Fiction, Non-Fiction, Biography, Self-Help, Horror, Adventure, Children's, Young Adult, Poetry, Drama, Classic, Dystopian, Memoir, Philosophy, Science

💬 CHAT COMMANDS:
• "clear my results" - Clear all messages from the chat
• "exit" - Close the program
• "help" - Show this message

Just ask me naturally like "Find me some fantasy books" or "What mystery novels do you have from the 2000s?" and I'll search our database for you!"""

    return help_text