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

"""Ths module provides a temprary abstraction for LLM services.
It will soon be deprecated in favour of something like liteLLM"""

import os
from openai import OpenAI

class LLM: 
    def __init__(self, 
                system_prompt="You are a medical profesional asnwering fellow medical professionals. Be terse and concise",
                #model="mradermacher/OpenBioLLM-Llama3-8B-GGUF", 
                #model="professorf/phi-3-mini-128k-f16-gguf",
                model="MaziyarPanahi/Llama-3-8B-Instruct-32k-v0.1-GGUF",
                ##model="NousResearch/Hermes-2-Pro-Mistral-7B-GGUF",
                ##model="Epiculous/Fett-uccine-Long-Noodle-7B-120k-Context-GGUF",
                #model="mradermacher/T3Q-Llama3-8B-dpo-v2.0-GGUF",
                #model="PrunaAI/Phi-3-mini-128k-instruct-GGUF-Imatrix-smashed",
                base_url= "http://localhost:11434/v1",
                api_key="lm-studio",
                #base_url="https://api.openai.com/v1",
                #api_key="env",
                #model="gpt-4o",
                temperature=0.1, 
                max_tokens=32000, 
                top_p=0.9, 
                frequency_penalty=0.0, 
                presence_penalty=0.0, 
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
        self.base_url = base_url
        self.api_key = api_key
        if api_key=='env': self.api_key = os.environ.get("OPENAI_API_KEY")
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.top_p = top_p
        self.frequency_penalty = frequency_penalty
        self.presence_penalty = presence_penalty
        self.stop = stop
        self.client = OpenAI(base_url=self.base_url, api_key=self.api_key)

        
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

    def generate(self, prompt) -> str:
        """
        :prompt: str, the prompt to generate from
        """
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "system", "content": self.system_prompt},
                      {"role": "user", "content": f"{prompt}"},
                       ],
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            #top_p=self.top_p,
            #frequency_penalty=self.frequency_penalty,
            #presence_penalty=self.presence_penalty,
            #stop=self.stop,
        )
        return response.choices[0].message.content.strip()


if __name__ == "__main__":
    llm = LLM()
    prompt = "Typical adverse effects of Doxycyline?"
    print(llm.generate(prompt))
