# Copyright (C) 2024  Dr Horst Herb
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import asyncio
import os
import json
from gpt_researcher import GPTResearcher
from medai.tools.apikeys import load_api_keys  


QUERY_TEMPLATE = """Write a detailed and well referenced report about the following: >>> {query} <<< 
                Take your time to consider all aspects, and use primarily the most recent pubmed or 
                peer reviewed biomedical journals for references. """

#The API keys needed for this to work - they will be loaded from the os environment:
APIS=('OPENAI_API_KEY', 'TAVILY_API_KEY', 'LLAMA_CLOUD_API_KEY')
load_api_keys(APIS)


def get_config(filename=None) -> dict:
    """Get the current configuration for the Researcher from the environment variables
       and retun them as a dictionary list. 
       If a filename is provided, obtain the configuration form that file instead"""

    if filename is not None: 
        with open(filename, 'r') as f:
            config= json.load(config, f)
            return config 

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
        "max_subtopics": int(os.getenv("MAX_SUBTOPICS", 3))
    }  

    return config

async def research(query: str, output_fname : str =None, output_path : str = './reports') -> str: 
    """Conduct research on the given query and write a report on it. 
       The report is returned as a string. 
       If output_fname is provided, the report is written to that file."""

    load_api_keys()
    
    # Report Type
    report_type = "research_report"
    
    # Initialize the researcher QUERY_TEMPLATE.format(query=query)
    researcher = GPTResearcher(query=query, report_type=report_type, config_path="./config.json")
    
    # Conduct research on the given query
    await researcher.conduct_research()
    
    # Write the report
    if not os.path.exists(output_path):
        os.makedirs(output_path)

    report = await researcher.write_report()

    #save the report in a file
    if output_fname is not None:
        fname=output_fname
    else:
        #default: take the first line of the report (the title) as the filename, after removing the leading '# '
        fname= report.split('\n', 1)[0].replace('#', '').strip().replace(' ', '_').lower() + '.md'
    fname = os.path.join(output_path, fname)
    try:
        with open(fname, 'w') as f:
            f.write(report)
    except Exception as e:
        print(f"Error writing report to file: {e}")
   
    return report


if __name__ == "__main__":
    # Create the parser
    import argparse
    parser = argparse.ArgumentParser(description="Conduct research on a given query and write a report.")

    # Add the arguments
    parser.add_argument("query", type=str, help="The query to research.")
    parser.add_argument("output_fname", type=str, help="The name of the file to write the report to.")

    # Parse the arguments
    args = parser.parse_args()

    # Conduct the research
    load_api_keys()
    report = asyncio.run(research(args.query, output_fname=args.output_fname))

# if __name__ == "__main__":
#     get_api_keys()
#     query = """Write a detailed and well referenced report about the role of Toxoplasma in human behaviour. 
#             Take your time to consider all aspects, and use primarily the most recent pubmed or peer reviewed 
#              biomedical journals for references. """
#     report = asyncio.run(research(query, output_fname="gptresearcher_toxoplasma_report.md") )
    