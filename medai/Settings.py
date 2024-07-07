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

import json
import os
import threading
import logging

class SingletonMeta(type):
    _instances = {}
    _lock: threading.Lock = threading.Lock()

    def __call__(cls, *args, **kwargs):
        with cls._lock:
            if cls not in cls._instances:
                instance = super().__call__(*args, **kwargs)
                cls._instances[cls] = instance
            return cls._instances[cls]

class Settings(metaclass=SingletonMeta):
    """
    Singleton class to manage settings for the MedAi tools. All tools share the same settings that way.
    Settings will be stored in a json file '.medai.json' in the user's home directory.
    """
    def __init__(self, from_defaults=False):
        """
        Load settings from file
        :param from_defaults: If True, load default settings & do NOT override saved settings
        """
        if from_defaults:
            self.settings = self.default_settings()
            return 
        
        self.settings = self.load_settings()
        if not self.settings:
            self.settings = self.default_settings()
        

    def load_settings(self):
        settings_path = os.path.join(os.path.expanduser('~'), '.medai.json')
        try:
            with open(settings_path, 'r') as file:
                return json.load(file)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            logging.error(f"Error loading settings: {e}, using defaults")
            self.settings = self.default_settings()
            logging.info(f"saving default settings as {settings_path}")
            self.save_settings(self.settings)
            return(self.settings)

    def save_settings(self, settings):
        settings_path = os.path.join(os.path.expanduser('~'), '.medai.json')
        logging.error(f"saving settings in [{settings_path}]")
        try:
            with open(settings_path, 'w') as file:
                json.dump(settings, file, indent=4)
        except Exception as e:
            logging.error(f"Error saving settings to {settings_path}: {e}")

    def __getattr__(self, name):
        try:
            return self.settings[name]
        except KeyError:
            raise AttributeError(f"'Settings' object has no attribute '{name}'")
    
    def default_settings(self):
        # Define your default settings here
        settings= {  
            #APIKEYS
            'LOCAL_LLM_API_KEY' : 'lm_studio',
            'OPENAI_API_KEY' : '',
            'HUGGINGFACE_API_KEY' : '',
            'GROQ_API_KEY' : '',
            'SERPER_API_KEY' : '',
            'TAVILY_API_KEY' : '',
            'TAVILY_API_SECRET' : '',

            #LLM
            'LOCAL_LLM_API_BASE' : 'http://localhost:11434',
            'LOCAL_DEFAULT_MODEL' : 'ollama/iLlama3_8b_Instruct_32k:latest',
            'LOCAL_32K_MODEL' : 'ollama/Llama3_8b_Instruct_32k:latest',
            #'LOCAL_128K_MODEL' : 'openai/Bartowski/Phi-3-medium-128k-Instruct-GGUF',
            'LOCAL_128K_MODEL' : "ollama/phi3:14b-medium-128k-instruct-q5_K_M",
            'LOCAL_LLM_API_KEY' : 'ollama',
            'OPENAI_API_BASE' : 'https://api.openai.com/v1',
            'OPENAI_MULTIMODAL_MODEL' : 'gpt-4o',

            #EMBEDDING
            'EMBEDDING_BASE_URL' : 'http://localhost:11434',
            'EMBEDDING_MODEL' : 'rjmalagon/gte-qwen2-1.5b-instruct-embed-f16', 
            'EMBEDDING_DIMENSIONS' : 1536,

            #STORAGE
            'LOCAL_STORAGE_DIR' : '~/medai',
            'PUBLICATION_DIR' : '/Users/hherb/medai/library',
            'DBUSER' : 'medai',
            'DBPASS' : 'thisismedai',
            'DBNAME' : 'medai',
            'HOST' : 'localhost',
            'PORT' : 5432,
            'RAGTABLE' : 'raglibrarian',
        
        }
        return settings
    

if __name__ == "__main__":
    settings = Settings()
    print(settings.LOCAL_STORAGE_DIR)