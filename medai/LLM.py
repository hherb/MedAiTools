# LLM.py
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

"""This model provides a temporary abstraction for LLM services.
It is likely to still change over time"""

import os
import traceback
import asyncio
import litellm
from dotenv import load_dotenv
import logging
from medai.Settings import Settings
from llama_index.llms.litellm import LiteLLM    #! pip install litellm
import ollama #! pip install ollama

s = Settings()

# Set the logging level for litellm to ERROR to reduce output
logging.getLogger('LiteLLM').setLevel(logging.ERROR)
logging.getLogger('httpx').setLevel(logging.ERROR)

def get_providers():
    return(['ollama', 'huggingface', 'groq', 'anthropic', 'openai', 'google'])

def get_models(provider='ollama'):
        
    if provider=='ollama':
        return([model['model'] for model in list_local_models()])
    if provider=='huggingface':
        return(['enter manually'])
    if provider=='groq':
        return(['mixtral-8x7b-32768', 'llama3-70b-8192', 'Llama3-groq-70B-8192-tool-use', 'llama3-8b-8192', 'Llama3-groq-8B-8192-tool-use', 'Gemma2-9b-it'])
    if provider=='anthropic':
        return(litellm.anthropic_models)
    if provider=='openai':
        return([model for model in litellm.open_ai_chat_completion_models if model.startswith('gpt')])
    if provider=='google':
        return(['gemini/gemini-1.5-pro-latest'])
    
    raise ValueError(f"Provider {provider} not supported. Supported providers are {LLM_PROVIDERS}")    


class Model:
    def __init__(self, modelname=s.LOCAL_DEFAULT_MODEL, 
                api_key=s.LOCAL_LLM_API_KEY,
                api_base=s.LOCAL_LLM_API_BASE,
                system_prompt="You are a medical profesional answering fellow medical professionals. Be truthful, terse and concise. Just answer the question without further comments nor introductions.",
                temperature=0.3,
                max_tokens=4000,
                frequency_penalty=0.0,
                repeat_penalty=0.0,
                presence_penalty=0.0,
                stop=None, 
                ): 
        litellm.drop_params=True 
        self.settings= Settings()     
        self.modelname = modelname
        self.api_key = api_key
        self.api_base = api_base
        self.system_prompt = system_prompt
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.frequency_penalty = frequency_penalty
        self.presence_penalty = presence_penalty
        self.stop = stop

    def get_model(self):
        return self.modelname

    def get_api_key(self):
        return self.api_key

    def get_api_base(self):
        return self.api_base
    
    def get_system_prompt(self):
        return self.system_prompt
        
    def get_temperature(self):
        return self.temperature
    
    def get_max_tokens(self):
        return self.max_tokens
    
    def get_frequency_penalty(self):
        return self.frequency_penalty
    
    def get_presence_penalty(self):
        return self.presence_penalty
    

    def get_stop(self):
        return self.stop

    def set_model(self, modelname):
        self.modelname = modelname

    def set_api_key(self, api_key):
        self.api_key = api_key

    def set_api_base(self, api_base):
        self.api_base = api_base

    def set_system_prompt(self, system_prompt):
        self.system_prompt = system_prompt

    def set_temperature(self, temperature):
        self.temperature = temperature

    def set_max_tokens(self, max_tokens):
        self.max_tokens = max_tokens

    def set_frequency_penalty(self, frequency_penalty):
        self.frequency_penalty = frequency_penalty

    def set_presence_penalty(self, presence_penalty):
        self.presence_penalty = presence_penalty

    def set_stop(self, stop):
        self.stop = stop


class OllamaModel(Model):
    def __init__(self, modelname):   
        super().__init__(modelname='ollama/'+modelname)
        self.api_key = 'ollama'
        self.api_base = 'http://localhost:11434'
        #self.modelname=modelname               
        self.info=ollama.show(modelname)
        #Parameters in the returned list of dictionaries are unfortunately formatted as one single string, need to parse it
        # params = {param.split()[0]: param.split()[1] for param in self.info['parameters'].split('\n')}
        # self.parameter_size = self.info['details']['parameter_size']
        # self.quantization = self.info['details']['quantization_level']
        # self.family = self.info['details']['family']
        # try:
        #     self.temperature=params['temperature']
        # except:
        #     self.temperature=0.3
        # try:
        #     self.num_ctx=params['num_ctx']
        #     self.max_tokens=self.num_ctx/2
        # except:
        #     self.num_ctx=0
        #     self.max_tokens=512
        # try: 
        #     self.system_prompt=info['details']['system']
        # except:
        #     pass


def llm_response(prompt, 
                 provider = 'ollama',
                 modelname = 'Llama3_8b_Instruct_32k:latest',
                 api_key = 'ollama',
                 api_base = None, 
                 temperature=0.3):
    messages = [{"role": "user", "content": f"{prompt}"}]
    if provider in ['ollama', 'huggingface', 'groq']:
        modelname = f"{provider}/{modelname}"
    response = litellm.completion(model=modelname, messages=messages, temperature=temperature)
    return(response.choices[0].message.content)

async def llm_streaming_response(prompt, 
                 provider = 'ollama',
                 modelname = 'Llama3_8b_Instruct_32k:latest',
                 api_key = 'ollama',
                 api_base = None, 
                 temperature=0.3):
    messages = [{"role": "user", "content": f"{prompt}"}]
    if provider in ['ollama', 'huggingface', 'groq']:
        modelname = f"{provider}/{modelname}"
    response = await litellm.acompletion(model=modelname, messages=messages, temperature=temperature, stream=True)
    #print(f"response: {response}")
    #message = ""
    #async for chunk in response:
    #    message += chunk #["choices"][0]["delta"].get("content", "")
    #    yield message
    async for chunk in response:
            yield(chunk)
    #return(response.choices[0].message.content)

    
def answer_this(prompt : str, 
                modelname : str = 'ollama/Llama3_8b_Instruct_32k:latest', 
                api_base : str = 'http://localhost:11434', 
                api_key : str ='ollama',
                temperature : float=0.3,) -> str:
    """
    Asks an ollama model for text generation.

    Parameters
    ----------
    prompt : str
        The input prompt to generate text from.
    modelname : str, optional (default='ollama/Llama3_8b_Instruct_32k:latest')
        The name of the OLLAMA model to use. This determines which model's parameters are used for generation.
    api_base : str, optional (default='http://localhost:11434')
        The base URL of the API endpoint to send requests to.
    api_key : str, optional (default='ollama')
        The API key to use when sending requests.
    temperature : float, optional (default=0.3)
        A value controlling the randomness and diversity of generated text.

    Returns
    -------
    str
        The generated text in response to the input prompt.

    Raises
    ------
    Exception
        Any exceptions raised during the API request or processing the response.
    """
    response = litellm.completion(
        model=modelname, 
        messages=[{ "content": f"{prompt}","role": "user", "name" : modelname}], 
        api_base="http://localhost:11434",
        api_key=api_key,
        temperature=temperature,
    )
    return(response.choices[0].message.content)


def list_local_models():
    """
    Returns a list of available local models.

    This function uses the ollama library to retrieve a list of available local models. The returned list is then passed back as the result.

    Args:
        None

    Returns:
        A list of strings representing the names of available local models.
    """
    models=ollama.list()
    return(models['models'])

def local_model_properties(model_name : str):
    pass


def update_local_model_db():
    models=ollama.list()
    for model in models:
        if not in_local_model_db(model['name']): 
            print(f"Adding model {model['name']} to local model database")

def get_local_default_model():
    return Model(modelname=s.LOCAL_DEFAULT_MODEL, api_key=s.LOCAL_LLM_API_KEY, api_base=s.LOCAL_LLM_API_BASE, temperature=0.3, max_tokens=4096, frequency_penalty=0.0, presence_penalty=0.0, stop=None)

def get_local_32k_model():
    return Model(modelname=s.LOCAL_32K_MODEL, api_key=s.LOCAL_LLM_API_KEY, api_base=s.LOCAL_LLM_API_BASE, temperature=0.3, max_tokens=32000, frequency_penalty=0.0, presence_penalty=0.0, stop=None)

def get_local_128k_model():
    return Model(modelname=s.LOCAL_128K_MODEL, api_key=s.LOCAL_LLM_API_KEY, api_base=s.LOCAL_LLM_API_BASE, temperature=0.3, max_tokens=128000, frequency_penalty=0.0, presence_penalty=0.0, stop=None)

def get_openai_multimodal_model(apikey=None):
    api_key=apikey
    if not api_key:
        load_dotenv()  #load the environment variables
        api_key=os.getenv('OPENAI_API_KEY')
    return Model(modelname=s.OPENAI_MULTIMODAL_MODEL, api_key=api_key, api_base=s.OPENAI_API_BASE, temperature=0.3, max_tokens=4096, frequency_penalty=0.0, presence_penalty=0.0, stop=None)

class LLM: 
    def __init__(self, model,
                system_prompt="You are a medical profesional answering fellow medical professionals. Be truthful, terse and concise. Just answer the question without further comments nor introductions.",
                ):
        """
        :system_prompt: str, the system prompt to use
        :model: dict, the model to use
        """
        self.model=model
        self.system_prompt = system_prompt


    def generate(self, prompt, quickanswer=True) -> str or list[dict]:
        """
        :prompt: str, the prompt to generate from
        :model: str, the model to use
        :return: list[dict], the generated response in OpenAI API format if quickanswer is False, else the response as a string

        """
        #litellm.api_base = "http://localhost:11434/v1"
        #litellm.api_key="lm-studio"
        messages=[]
        if self.system_prompt is not None:
            messages.append({"role": "system", "content": self.system_prompt})
        messages.append({"role": "user", "content": f"{prompt}"})
        #print(f"Generating from model {model} with prompt {prompt}")
        response = litellm.completion(messages=messages, 
                                  model=self.model.get_model(), 
                                  api_key=self.model.get_api_key(), 
                                  api_base=self.model.get_api_base(),  
                                  temperature=self.model.get_temperature(), 
                                  max_tokens=self.model.get_max_tokens(),
                                  frequency_penalty=self.model.get_frequency_penalty(),
                                  presence_penalty=self.model.get_presence_penalty(),
                                  stop=self.model.get_stop()
                                  )     
        if quickanswer:
            return response.choices[0].message.content.strip()
        else:
            return response
        

    def generate_streaming(self, prompt) -> str:
        """
        :prompt: str, the prompt to generate from
        :model: str, the model to use
        :return: list[dict], the generated response in OpenAI API format if quickanswer is False, else the response as a string

        """
        #litellm.api_base = "http://localhost:11434/v1"
        #litellm.api_key="lm-studio"
        messages=[]
        if self.system_prompt is not None:
            messages.append({"role": "system", "content": self.system_prompt})
        messages.append({"role": "user", "content": f"{prompt}"})
        #print(f"Generating from model {model} with prompt {prompt}")
        response = litellm.acompletion(messages=messages, 
                                  model=self.model.get_model(), 
                                  api_key=self.model.get_api_key(), 
                                  api_base=self.model.get_api_base(),  
                                  temperature=self.model.get_temperature(), 
                                  max_tokens=self.model.get_max_tokens(),
                                  frequency_penalty=self.model.get_frequency_penalty(),
                                  presence_penalty=self.model.get_presence_penalty(),
                                  stop=self.model.get_stop(),
                                  stream=True
                                  )     
        return response 
    
    async def completion_call(self, prompt):
        messages=[]
        if self.system_prompt is not None:
            messages.append({"role": "system", "content": self.system_prompt})
        messages.append({"role": "user", "content": f"{prompt}"})
        try:
            #print("test acompletion + streaming")
            response = await litellm.acompletion(messages=messages, 
                                  model=self.model.get_model(), 
                                  api_key=self.model.get_api_key(), 
                                  api_base=self.model.get_api_base(),  
                                  temperature=self.model.get_temperature(), 
                                  #max_tokens=self.model.get_max_tokens(),
                                  #frequency_penalty=self.model.get_frequency_penalty(),
                                  #presence_penalty=self.model.get_presence_penalty(),
                                  #stop=self.model.get_stop(),
                                  stream=True
                                  ) 
            #print(f"response: {response}")
            async for chunk in response:
                yield(chunk)
        except:
            print(f"error occurred: {traceback.format_exc()}")
            pass

async def main():
    prompt = "Typical adverse effects of Doxycyline? Tell me in details of at least two paragraphs"
    model=OllamaModel("phi3.5:3.8b-mini-instruct-fp16")
    llm=LLM(model)
    #print(f"Response from {llm.model.get_model()}: {llm.generate(prompt)}")
    async for chunk in llm_streaming_response(prompt):  #llm.completion_call(prompt):
        if chunk is not None:
            print(chunk.choices[0].delta.content, end="") 

if __name__ == "__main__":
    #models = (LLM(get_openai_multimodal_model()), LLM(get_local_default_model()), LLM(get_local_32k_model()))
    #prompt = "Typical adverse effects of Doxycyline?"
    #for llm in models:
        #print(f"Response from {llm.model.get_model()}: {llm.generate(prompt)}")
    asyncio.run(main())
