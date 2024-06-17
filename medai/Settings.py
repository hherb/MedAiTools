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

import threading
import logging
import configparser

class SingletonMeta(type):
    _instances = {}
    _lock: threading.Lock = threading.Lock()

    def __call__(cls, *args, **kwargs):
        with cls._lock:
            if cls not in cls._instances:
                instance = super().__call__(*args, **kwargs)
                cls._instances[cls] = instance
            return cls._instances[cls]

class Section:
    def __init__(self, options):
        for option, value in options.items():
            setattr(self, option, value)

class Settings(metaclass=SingletonMeta):
    def __init__(self):
        try:
            loaded_settings = self.load_settings()
            if not loaded_settings:
                loaded_settings = self.default_settings()
            self.settings = {section: Section(options) for section, options in loaded_settings.items()}
        except Exception as e:
            logging.error(f"Error loading settings: {e}")
            self.settings = self.default_settings()

    @staticmethod
    def save_settings(settings, filename='medai.ini'):
        config = configparser.ConfigParser()
        for section, options in settings.items():
            config[section] = {}
            for option, value in options.items():
                config[section][option] = str(value)    
        with open(filename, 'w') as configfile:
            config.write(configfile)
            
    @staticmethod
    def load_settings(filename='medai.ini'):
        config = configparser.ConfigParser()
        config.read(filename)
        settings = {section: dict(config.items(section)) for section in config.sections()}
        return settings

    def __getattr__(self, name):
        # This method is called if there isn't an attribute with the name
        try:
            return self.settings[name]
        except KeyError:
            raise AttributeError(f"'Settings' object has no attribute '{name}'")

    @staticmethod
    def default_settings():
        # Define your default settings here
        settings= {  
            'APIKEYS' : {
                'LOCAL_LLM_API_KEY' : 'lm_studio',
                'OPENAI_API_KEY' : '',
                'HUGGINGFACE_API_KEY' : '',
                'GROQ_API_KEY' : '',
                'SERPER_API_KEY' : '',
                'TAVILY_API_KEY' : '',
                'TAVILY_API_SECRET' : '',
            },

            'LLM' : {
                'LOCAL_LLM_API_BASE' : 'http://localhost:11434/v1',
                'LOCAL_DEFAULT_MODEL' : 'openai/MaziyarPanahi/Llama-3-8B-Instruct-32k-v0.1-GGUF',
                'LOCAL_32K_MODEL' : 'openai/MaziyarPanahi/Llama-3-8B-Instruct-32k-v0.1-GGUF',
                'LOCAL_128K_MODEL' : 'openai/Bartowski/Phi-3-medium-128k-Instruct-GGUF',
                'LOCAL_LLM_API_KEY' : 'lm_studio',
                'OPENAI_API_BASE' : 'https://api.openai.com/v1',
                'OPENAI_MULTIMODAL_MODEL' : 'gpt-4o',
            },

            'EMBEDDING' : {
                'EMBEDDING_MODEL' : 'BAAI/bge-m3',
                'EMBEDDING_DIMENSIONS' : 1024,
            },
            
            'STORAGE' : {
                'LOCAL_STORAGE_DIR' : '~/medai',
                'PUBLICATION_DIR' : '~/medai/publications',
                'DBUSER' : 'medai',
                'DBPASS' : 'thisismedai',
                'DBNAME' : 'medai',
                'HOST' : 'localhost',
                'PORT' : 5432,
                'RAGTABLE' : 'RAGLibrarian',
            }
        }
        return settings