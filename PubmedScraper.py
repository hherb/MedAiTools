import re

# pip install llama-index-readers-papers 
from llama_index.readers.papers import PubmedReader


def pubmed_search_string(text):
    """
    Replace all double and single quotes (case insensitive) with '+' sign.

    :param text: The input string.
    :return: The string with replaced quotes.
    """
    pattern = re.compile(r'[\'\"]+|[\"'](?!\w)[\'"]+')
    return re.sub(pattern, r'+', text, flags=re.IGNORECASE)


loader = PubmedReader()
documents = loader.load_data(search_query="amyloidosis")