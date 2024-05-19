import asyncio
from dotenv import load_dotenv
import os
from gpt_researcher import GPTResearcher

APIS=('OPENAI_API_KEY', 'TAVILY_API_KEY')

def get_api_keys():
    load_dotenv()
    for key in APIS:
        os.environ[key] = os.getenv(key)


import json
import os

def extract_config_to_json(filename):
    config = {
        "retriever": os.getenv('RETRIEVER', "tavily"),
        "embedding_provider": os.getenv('EMBEDDING_PROVIDER', 'openai'),
        "llm_provider": os.getenv('LLM_PROVIDER', "openai"),
        "fast_llm_model": os.getenv('FAST_LLM_MODEL', "gpt-3.5-turbo-16k"),
        "smart_llm_model": os.getenv('SMART_LLM_MODEL', "gpt-4o"),
        "fast_token_limit": int(os.getenv('FAST_TOKEN_LIMIT', 2000)),
        "smart_token_limit": int(os.getenv('SMART_TOKEN_LIMIT', 4000)),
        "browse_chunk_max_length": int(os.getenv('BROWSE_CHUNK_MAX_LENGTH', 8192)),
        "summary_token_limit": int(os.getenv('SUMMARY_TOKEN_LIMIT', 700)),
        "temperature": float(os.getenv('TEMPERATURE', 0.55)),
        "user_agent": os.getenv('USER_AGENT', "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36 Edg/119.0.0.0"),
        "max_search_results_per_query": int(os.getenv('MAX_SEARCH_RESULTS_PER_QUERY', 5)),
        "memory_backend": os.getenv('MEMORY_BACKEND', "local"),
        "total_words": int(os.getenv('TOTAL_WORDS', 800)),
        "report_format": os.getenv('REPORT_FORMAT', "APA"),
        "max_iterations": int(os.getenv('MAX_ITERATIONS', 3)),
        "agent_role": os.getenv('AGENT_ROLE', None),
        "scraper": os.getenv("SCRAPER", "bs"),
        "max_subtopics": os.getenv("MAX_SUBTOPICS", 3)
    }

    with open(filename, 'w') as f:
        json.dump(config, f)

async def research(query, output_fname=None):
    get_api_keys()
    # Report Type
    report_type = "research_report"
    # Initialize the researcher
    researcher = GPTResearcher(query=query, report_type=report_type, config_path="./config.json")
    #extract_config_to_json('config.json')
    # Conduct research on the given query
    await researcher.conduct_research()
    # Write the report
    report = await researcher.write_report()
    if output_fname is not None:
        with open(output_fname, 'w') as f:
            f.write(report) 
    
    return report


if __name__ == "__main__":
    get_api_keys()
    query = "Write a detailed and well referenced report about the role of Toxoplasma in human behaviour. Take your time to consider all aspects, and use primarily pubmed for references. "
    report = asyncio.run(research(query, output_fname="gptresearcher_toxoplasma_report.md") )
    