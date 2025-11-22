import re

# pip install llama-index-readers-papers 
from llama_index.readers.papers import PubmedReader


def pubmed_search_string(text):
    """
    Replace all double and single quotes (case insensitive) with '+' sign.

    :param text: The input string.
    :return: The string with replaced quotes.
    """
    # Match one or more single or double quotes
    pattern = re.compile(r'[\'"]+')
    return re.sub(pattern, '+', text)


loader = PubmedReader()
documents = loader.load_data(search_query="amyloidosis")