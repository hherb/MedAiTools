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
    def __init__(self):
        try:
            print("loading ...")
            self.settings = self.load_settings()
            if not self.settings:
                self.settings = self.default_settings()
        except Exception as e:
            logging.error(f"Error loading settings: {e}")
            self.settings = self.default_settings()

    def load_settings(self):
        settings_path = os.path.join(os.path.expanduser('~'), '.medai.ini')
        try:
            with open(settings_path, 'r') as file:
                return json.load(file)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            logging.error(f"Error loading settings from {settings_path}: {e}")
            return self.default_settings()

    def save_settings(self, settings):
        settings_path = os.path.join(os.path.expanduser('~'), '.medai.ini')
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
            'LOCAL_LLM_API_BASE' : 'http://localhost:11434/v1',
            'LOCAL_DEFAULT_MODEL' : 'openai/MaziyarPanahi/Llama-3-8B-Instruct-32k-v0.1-GGUF',
            'LOCAL_32K_MODEL' : 'openai/MaziyarPanahi/Llama-3-8B-Instruct-32k-v0.1-GGUF',
            'LOCAL_128K_MODEL' : 'openai/Bartowski/Phi-3-medium-128k-Instruct-GGUF',
            'LOCAL_LLM_API_KEY' : 'lm_studio',
            'OPENAI_API_BASE' : 'https://api.openai.com/v1',
            'OPENAI_MULTIMODAL_MODEL' : 'gpt-4o',
            #EMBEDDING
            'EMBEDDING_MODEL' : 'BAAI/bge-m3',
            'EMBEDDING_DIMENSIONS' : 1024,
            #STORAGE
            'LOCAL_STORAGE_DIR' : '~/medai',
            'PUBLICATION_DIR' : '~/src/github/MedAiTools/library',
            'DBUSER' : 'medai',
            'DBPASS' : 'thisismedai',
            'DBNAME' : 'medai',
            'HOST' : 'localhost',
            'PORT' : 5432,
            'RAGTABLE' : 'RAGLibrarian',
        
        }
        return settings