
import os
from dotenv import load_dotenv
APIS=('OPENAI_API_KEY', 'TAVILY_API_KEY', 'LLAMA_CLOUD_API_KEY')

def load_api_keys(APIS : list[str] =APIS) -> None:
    """load all needed API keys from the os environment"""
    load_dotenv()
    for key in APIS:
        value = os.getenv(key)
        if value is None:
            raise ValueError(f'Missing environment variable {key}')
        os.environ[key] = value