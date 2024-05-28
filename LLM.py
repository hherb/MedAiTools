# MetaAnalysisAppraiser.py
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

"""Ths model provides a temprary abstraction for LLM services.
It will soon be deprecated in favour of something like liteLLM"""

import os
import litellm

LOCAL_LLM_API_BASE="http://localhost:11434/v1"
LOCAL_32K_LLM_MODEL="openai/MaziyarPanahi/Llama-3-8B-Instruct-32k-v0.1-GGUF"
LOCAL_LLM_API_KEY="lm_studio"


from openai import OpenAI

class LLM: 
    def __init__(self, 
                system_prompt="You are a medical profesional answering fellow medical professionals. Be truthful, terse and concise. Just answer the question without further comments nor introductions.",
                model=LOCAL_32K_LLM_MODEL,
                base_url= LOCAL_LLM_API_BASE,
                api_key=LOCAL_LLM_API_BASE,
                temperature=0.2, 
                max_tokens=32000, 
                top_p=0.9, 
                frequency_penalty=0.0, 
                presence_penalty=0.0,
                repeat_penalty=0.0, 
                stop=None,):
        """
        :system_prompt: str, the system prompt to use
        :model: str, the large language model to use
        :temperature: float, the temperature of the model
        :max_tokens: int, the maximum number of tokens to generate
        :top_p: float, the nucleus sampling parameter
        :frequency_penalty: float, the frequency penalty
        :presence_penalty: float, the presence penalty
        :stop: str, the stopping token
        """
        self.system_prompt = system_prompt
        self.api_base = base_url
        self.api_key = api_key
        if api_key=='env': self.api_key = os.environ.get("OPENAI_API_KEY")
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.top_p = top_p
        self.frequency_penalty = frequency_penalty
        self.presence_penalty = presence_penalty
        self
        self.stop = stop
        #self.client = OpenAI(base_url=self.base_url, api_key=self.api_key)

        
    def set_system_prompt(self, system_prompt):
        """
        :system_prompt: str, the system prompt to use
        """
        self.system_prompt = system_prompt

    def set_temperature(self, temperature):
        """
        :temperature: float, the temperature of the model
        """
        self.temperature = temperature

    def set_max_tokens(self, max_tokens):
        """
        :max_tokens: int, the maximum number of tokens to generate
        """
        self.max_tokens = max_tokens


    def get_model(self):
        return self.model

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
        model=self.model
        #print(f"Generating from model {model} with prompt {prompt}")
        response = litellm.completion(messages=messages, 
                                  model=model, 
                                  api_key=self.api_key, 
                                  api_base=self.api_base,  
                                  temperature=self.temperature, 
                                  max_tokens=self.max_tokens)
        
        if quickanswer:
            return response.choices[0].message.content.strip()
        else:
            return response


if __name__ == "__main__":
    llm = LLM()
    prompt = "Typical adverse effects of Doxycyline?"
    print(llm.generate(prompt))
