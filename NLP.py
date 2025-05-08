import spacy

nlp = None

def init_nlp(model_name: str = "en_core_web_sm"):
    global nlp
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