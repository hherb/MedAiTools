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
APIS=('OPENAI_API_KEY', 'TAVILY_API_KEY', 'LLAMA_CLOUD_API_KEY', 'GEMINI_API_KEY', 'ANTHROPIC_API_KEY', 'HUGGINGFACE_API_KEY', 'GROQ_API_KEY')
load_api_keys(APIS)


class Configuration:
    """
    Configuration class for GPT Researcher.

    This class is responsible for configuring the GPT Researcher. It provides a way to set and retrieve various parameters
    that control the behavior of the researcher.

    Attributes:
        config (dict): A dictionary containing all the configuration parameters.
    """
    def __init__(self, config_file=None, **kwargs):
        """
        Initialize the Configuration object.
        
        Args:
            **kwargs: A dictionary containing the configuration parameters.

        """
        self.config = {}
        self.config['FAST_TOKEN_LIMIT'] = 2000
        self.config['SMART_TOKEN_LIMIT'] = 4000
        self.config['SUMMARY_TOKEN_LIMIT'] = 700
        self.config['BROWSE_CHUNK_MAX_LENGTH'] = 8192
        self.config['MEMORY_BACKEND'] = 'local'
        self.config['TOTAL_WORDS'] = 800
        self.config['REPORT_FORMAT'] = 'APA'
        self.config['MAX_ITERATIONS'] = 3
        self.config['AGENT_ROLE'] = None
        self.config['SCRAPER'] = 'bs'
        self.config['MAX_SUBTOPICS'] = 3
        self.config['TEMPERATURE'] = 0.55
    
        if config_file is not None:
            try:
                with open(config_file, 'r') as f:
                    self.config = json.load(f)
            except Exception as e:
                print(f"Error loading configuration from file: {e}")
                #save the new configuration to the file
            if config_file is not None:
                self.save(config_file)
        for key in kwargs:
            self.config[key] = kwargs[key]
        

    def __getitem__(self, key):
        return self.config[key]
    
    def __setitem__(self, key, value):
        self.config[key] = value

    def activate(self):
        """
        Activate the configuration.
        """
        for key in self.config:
            os.environ[key] = str(self.config[key])

    def save(self, path="./researcher_config.json"):
        with open(path, 'w') as f:
            json.dump(self.config, f)

    def load(self, path="./researcher_config.json"):
        try:
            with open(path, 'r') as f:
                self.config = json.load(f)
        except Exception as e: 
            print(f"Error loading configuration from file: {e}")
            #save defaults into new config file
            self.save()



class OpenAI_Config(Configuration):
    def __init__(self, config_file="openai.json", **kwargs):
        super().__init__(config_file=config_file, **kwargs)
        self.config['OPENAI_API_KEY'] = os.getenv('OPENAI_API_KEY', None)
        self.config['LLM_PROVIDER']='openai'
        self.config['FAST_LLM_MODEL'] = 'gpt-4o-mini'
        self.config['SMART_LLM_MODEL'] = 'gpt-4o'
        

class Ollama_Config(Configuration):
    def __init__(self, config_file="ollama.json", **kwargs):
        super().__init__(config_file=config_file, **kwargs)
        self.config['LLM_PROVIDER']='ollama'
        self.config["OLLAMA_BASE_URL"] = "http://localhost:11434" 
        self.config["EMBEDDING_PROVIDER"] = "ollama"
        self.config["OLLAMA_EMBEDDING_MODEL"] : "mxbai-embed-large"
        self.config['FAST_LLM_MODEL'] = 'llama3-groq-tool-use:8b-q8_0'
        self.config['SMART_LLM_MODEL'] = 'nous-hermes2:34b-yi-q8_0'
        

class Groq_config(Configuration):
    def __init__(self, config_file="groq.json", **kwargs):
        super().__init__(config_file=config_file, **kwargs)
        self.config['LLM_PROVIDER']='groq'
        self.config['GROQ_API_KEY'] = os.getenv('GROQ_API_KEY', None)
        self.config['FAST_LLM_MODEL'] = 'Mixtral-8x7b-32768'
        self.config['SMART_LLM_MODEL'] = 'Mixtral-8x7b-32768'
        

     
class Anthropic_Config(Configuration):
    def __init__(self, config_file="anthropic.json", **kwargs):
        super().__init__(config_file=config_file, **kwargs)
        self.config['LLM_PROVIDER']='anthropic'
        self.config['ANTHROPIC_API_KEY'] = os.getenv('ANTHROPIC_API_KEY', None)
        self.config['FAST_LLM_MODEL'] = 'claude-3-haiku-20240307'
        self.config['SMART_LLM_MODEL'] = 'claude-3-5-sonnet-20240620'
        

class Huggingface_Config(Configuration):
    def __init__(self, config_file="huggingface.json", **kwargs):
        super().__init__(config_file=config_file, **kwargs)
        self.config['LLM_PROVIDER']='huggingface'
        self.config['HUGGINGFACE_API_KEY'] = os.getenv('HUGGINGFACE_API_KEY', None)
        self.config['FAST_LLM_MODEL'] = 'HuggingFaceH4/zephyr-7b-beta'
        self.config['SMART_LLM_MODEL'] = 'HuggingFaceH4/zephyr-7b-beta'

class Google_Config(Configuration):
    def __init__(self, config_file="google.json", **kwargs):
        super().__init__(config_file=config_file, **kwargs)
        self.config['LLM_PROVIDER']='google'
        self.config['GOOGLE_API_KEY'] = os.getenv('GOOGLE_API_KEY', None)
        self.config['FAST_LLM_MODEL'] = 'gemini-1.5-flash'
        self.config['SMART_LLM_MODEL'] = 'gemini-1.5-flash'
        
        
AVAILABLE_CONFIGS={'openai':OpenAI_Config, 
                   'ollama':Ollama_Config, 
                   'groq':Groq_config, 
                   'anthropic':Anthropic_Config, 
                   'huggingface':Huggingface_Config, 
                   'google':Google_Config}

async def research(query: str, report_type = "research_report", output_fname : str = None, output_path : str = './reports', research_params=None) -> str: 
    """Conduct research on the given query and write a report on it. 
       The report is returned as a string. 
       If output_fname is provided, the report is written to that file."""

    load_api_keys()
    
    # Initialize the researcher QUERY_TEMPLATE.format(query=query)
    print("Initialising researcher")
    researcher = GPTResearcher(query=query, report_type=report_type, config_path=None) 
    # Conduct research on the given query
    await researcher.conduct_research()
    
    # Write the report
    if not os.path.exists(output_path):
        os.makedirs(output_path)

    report = await researcher.write_report()

    if output_fname:
        fname=output_fname
    else:
        #default: take the first line of the report (the title) as the filename, after removing the leading '# '
        # This line of code is extracting the title of the report from the generated report string and
        # using it to create a filename for the report. 
        fname= report.split('\n', 1)[0].replace('#', '').strip().replace(' ', '_').lower() + '.md'
        
    fname = os.path.join(output_path, fname)
    # Check if the file exists and append a number if it does
    base, ext = os.path.splitext(fname)
    counter = 1
    while os.path.exists(fname):
        fname = f"{base}_{counter}{ext}"
        counter += 1
    try:
        with open(fname, 'w') as f:
            f.write(report)
            if research_params:
                with open(fname + '_params.json', 'w') as pf:
                    pf.write(json.dumps(research_params))
    except Exception as e:
        print(f"An error occurred while writing the report: {e}")
   
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
    config=Anthropic_Config()
    config.activate()
    report = asyncio.run(research(args.query, output_fname=args.output_fname))


    