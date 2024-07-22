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

import os
import panel as pn   #! pip install panel
from panel.widgets import Tqdm
from time import sleep
import asyncio
import sys

from Researcher import research, AVAILABLE_CONFIGS
from MedrXivPanel import MedrXivPanel 
from RAG_UI import PDFPanel
from medai.tools.apikeys import load_api_keys  
from medai.Settings import Settings
from PersistentStorage import PublicationStorage
#from EventDispatcher import EventDispatcher
from medai import LLM   

pn.extension('texteditor', loading_indicator=True, design="material")

#The API keys needed for this to work - they will be loaded from the os environment:

APIS=('OPENAI_API_KEY', 'TAVILY_API_KEY', 'LLAMA_CLOUD_API_KEY', 'GROQ_API_KEY', 'ANTHROPIC_API_KEY', 'HUGGINGFACE_API_KEY', 'GEMINI_API_KEY')
load_api_keys(APIS)

pn.extension('perspective', 'terminal', notifications=True, loading_indicator=True, design="material")

class APIKeySettings:
    def __init__(self, user=None):
        self.api={}
        self.api['user'] = user or os.getenv('USER', 'Anonymous')
        self.api['serper'] = os.getenv('SERPER_API_KEY', None)
        self.api['tavily'] = os.getenv('TAVILY_API_KEY', None)
        self.api['openai'] = os.getenv('OPENAI_API_KEY', None)
        self.api['groq'] = os.getenv('GROQ_API_KEY', None)
        self.api['huggingface'] = os.getenv('HUGGINGFACE_API_KEY', None)
        self.api['google'] = os.getenv('GEMINI_API_KEY', None)

        # API key settings UI
        self.widgets={}
        for api in self.api.keys():
            self.widgets[api] = pn.widgets.TextInput(name=api, value=self.api[api], sizing_mode='stretch_width')
            self.widgets[api].param.watch(self.on_change, 'value')

        self.api_column = pn.Column(name='API keys')
        for widget in self.widgets.values():
            self.api_column.append(widget)
        self.API_accordion = pn.Accordion(self.api_column, sizing_mode='stretch_width', name='API Keys')

    def on_change(self, event):
        #if the user has changed the API key, update the environment and the API key dictionary
        self.api[event.obj.name] = event.new
        os.environ[event.obj.name] = str(event.new)
        
    def get_UI_widget(self):
        return self.API_accordion
        
    def get_settings(self):
        return self.api
        
class LLMSettings:
    def __init__(self, user=None):
        self.widgets={}
        self.widgets['provider'] = pn.widgets.Select(name="LLM provider", options=LLM.get_providers(), value='ollama')
        self.widgets['provider'].param.watch(self.on_provider_change, 'value')
        models = LLM.get_models(self.widgets['provider'].value)
        self.widgets['models'] = pn.widgets.Select(name="LLM", options=models, value=models[0])
        self.widgets['models'].param.watch(self.on_model_change, 'value')
        self.widgets['baseurl'] = pn.widgets.TextInput(name='LLM base URL', value="http://localhost:11434", sizing_mode='stretch_width')
        self.widgets['temperature'] = pn.widgets.FloatSlider(name='Temperature', start=0.0, end=1.0, step=0.01, value=0.3)
        self.widgets['systemprompt'] = pn.widgets.TextAreaInput(name='System Prompt', 
                                                                placeholder="""You will answer the question truthfully to the best of your abilities. If you don't know for sure, just say 'I don't know'""", 
                                                                sizing_mode='stretch_width')
        
        self.LLM_accordion = pn.Accordion(sizing_mode='stretch_width', name='LLM Settings')
        self.api_column = pn.Column(name='LLM Settings')
        for widget in self.widgets.values():
            self.api_column.append(widget)
        self.LLM_accordion.append(self.api_column)

    def on_provider_change(self, event):
        provider = event.new
        print(f"selected provider: {provider}")
        models = LLM.get_models(provider)
        self.widgets['models'].options = models
        self.widgets['models'].value = models[0]

    def on_model_change(self, event):
        #the user has changed the model, update the relevant parameters
        self.modelname = event.new
        print(f"selected model: {self.modelname}")

    def get_UI_widget(self):
        return self.LLM_accordion
       
    def get_settings(self):
        params={}
        for key in self.widgets.keys():
            params[key] = self.widgets[key].value
        return params
    



class EmbeddingSettings:
    def __init__(self, user=None):
        self.widgets={}
        self.widgets['provider'] = pn.widgets.Select(name="Embedding provider", options=['openai', 'anthropic', 'groq',  'google',  'ollama'], value='ollama')
        self.widgets['model'] = pn.widgets.TextInput(name='Embedding model', value="mxbai-embed-large", sizing_mode='stretch_width')
        self.widgets['model'].param.watch(self.on_model_change, 'value')
        self.widgets['provider'].param.watch(self.on_provider_change, 'value')
        
        self.embedding_column = pn.Column(name='Embedding Settings')
        for widget in self.widgets.values():
            self.embedding_column.append(widget)
        self.embedding_accordion = pn.Accordion(self.embedding_column, sizing_mode='stretch_width', name='Embedding Settings')

    def on_provider_change(self, event):
        provider = event.new
        print(f"selected provider: {provider}")

    def on_model_change(self, event):
        #the user has changed the model, update the relevant parameters
        self.modelname = event.new
        
        
    def get_UI_widget(self):
        return self.embedding_accordion
       
    def get_settings(self):
        pass

class ResearcherSettings:
    def __init__(self):
        self.widgets={}
        self.widgets['RETRIEVER'] = pn.widgets.Select(name="Retriever", options=['tavily', 'serper',  'google',  'searxing', 'duckduckgo'], value='tavily')
        self.widgets['BROWSE_CHUNK_MAX_LENGTH'] = pn.widgets.IntInput(name='Browse chunk max length', value=8192, sizing_mode='stretch_width')
        self.widgets['SCRAPER'] = pn.widgets.TextInput(name='Scraper', value="bs", sizing_mode='stretch_width')
        self.widgets['LLM_PROVIDER'] = pn.widgets.Select(name="LLM provider", options=list(AVAILABLE_CONFIGS.keys()), value='ollama')
        self.widgets['LLM_PROVIDER'].param.watch(self.on_provider_change, 'value')
        models = LLM.get_models(self.widgets['LLM_PROVIDER'].value)
        self.widgets['OLLAMA_BASEURL'] = pn.widgets.TextInput(name='LLM base URL', value="http://localhost:11434", sizing_mode='stretch_width')
        self.widgets['FAST_LLM_MODEL'] = pn.widgets.Select(name="Fast LLM", options=models, value=models[0], sizing_mode='stretch_width')
        self.widgets['SMART_LLM_MODEL'] = pn.widgets.Select(name="Smart LLM", options=models, value=models[0], sizing_mode='stretch_width')
        self.widgets['TEMPERATURE'] = pn.widgets.FloatSlider(name='Temperature', start=0.0, end=1.0, step=0.01, value=0.3)
        self.widgets['FAST_TOKEN_LIMIT'] = pn.widgets.IntInput(name='Fast token limit', value=3000, sizing_mode='stretch_width')
        self.widgets['SMART_TOKEN_LIMIT'] = pn.widgets.IntInput(name='Smart token limit', value=4000, sizing_mode='stretch_width')       
        self.widgets['SUMMARY_TOKEN_LIMIT'] = pn.widgets.IntInput(name='Summary token limit', value=700, sizing_mode='stretch_width')    
        self.widgets['EMBEDDING_PROVIDER'] = pn.widgets.Select(name="Embedding provider", options=['openai', 'anthropic', 'groq',  'google',  'ollama'], value='ollama')
        self.widgets['EMBEDDING_MODEL'] = pn.widgets.TextInput(name='Embedding model', value="mxbai-embed-large", sizing_mode='stretch_width')
        self.widgets['MEMORY_BACKEND'] = pn.widgets.Select(name="Memory backend", options=['local'], value='local')
        self.widgets['TOTAL_WORDS'] = pn.widgets.IntInput(name='Total words', value=800, sizing_mode='stretch_width')
        self.widgets['REPORT_FORMAT'] = pn.widgets.TextInput(name='Report format', value="APA", sizing_mode='stretch_width')
        self.widgets['MAX_ITERATIONS'] = pn.widgets.IntInput(name='Max iterations', value=5, sizing_mode='stretch_width')
        self.widgets['AGENT_ROLE'] = pn.widgets.TextInput(name='Agent role', value=None, sizing_mode='stretch_width')
        self.widgets['MAX_SUBTOPICS'] = pn.widgets.IntInput(name='Max subtopics', value=3, sizing_mode='stretch_width')
        self.widgets['MAX_SEARCH_RESULTS_PER_QUERY'] = pn.widgets.IntInput(name='Max search results per query', value=10, sizing_mode='stretch_width')
        self.widgets['USER_AGENT'] = pn.widgets.TextInput(name='User agent', value="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/", sizing_mode='stretch_width')
        self.accordion = pn.Accordion(sizing_mode='stretch_width', name='Research Agent Settings')
        self.parameter_column = pn.Column(name='Researcher Settings')
        for widget in self.widgets.values():
            self.parameter_column.append(widget)
        self.accordion.append(self.parameter_column)

    def on_provider_change(self, event):
        provider = event.new
        print(f"selected provider for researcher: {provider}")
        models = LLM.get_models(provider)
        self.widgets['SMART_LLM_MODEL'].options = models
        self.widgets['SMART_LLM_MODEL'].value = models[0]
        self.widgets['FAST_LLM_MODEL'].options = models
        self.widgets['FAST_LLM_MODEL'].value = models[0]


    def get_UI_widget(self):
        return self.accordion
       
    def get_settings(self):
        params={}
        for key in self.widgets.keys():
            params[key] = self.widgets[key].value
        return params
    
    def activate(self):
        for key in self.widgets.keys():
            os.environ[key] = str(self.widgets[key].value)

currentApiKeySettings=APIKeySettings()
currentLLMSettings=LLMSettings()
currentEmbeddingSettings=EmbeddingSettings()
currenttResearcherSettings=ResearcherSettings()

async def get_response_async(contents, timeout=300):
    """
    Async function to get the AI agent's response.
    This function takes in some contents as input and then waits for
    the research coroutine to complete. If a timeout occurs, it returns
    a default error message.

    Parameters:
        contents (str): The text or other content to be processed by the AI agent.

    Returns:
        str: The response from the AI agent, either successfully obtained or an error message.
    """
    info = pn.state.notifications.info('Waiting for the AI agent\'s response ...', duration=0)
    notebook.active = 3  # debug tab
    try:
        # Set a timeout for the research coroutine
        response = await asyncio.wait_for(research(contents), timeout=timeout)  
    except asyncio.TimeoutError:
        response = "The request timed out. Please try again."
    finally:
        info.destroy()
        notebook.active = 0  # research assistant tab
    return response

def get_response(contents, user, instance):
    """
    This function determines the type of query and accordingly calls either a full research or a simple question answering routine.

    Parameters:
    contents (str): The content to be processed by the AI agent.
    user (object): The user object that initiated the request.
    instance (object): An instance of the class handling the request.

    Returns:
    response (str): The response from the AI agent, which can be a research result or an answer to a simple question.
    """
    if contents.startswith('@'):
        #do a full research
        currenttResearcherSettings.activate()
        return asyncio.run(get_response_async(contents))
    else:
        #just answer a simple question
        params = currentLLMSettings.get_settings()
        #pprint(params)
        provider = params['provider']
        modelname = params['models']
        temperature=params['temperature']
        print(f"model used:{modelname}")
        print(f"attempting to answer question using LLM: {modelname}")
        response = LLM.llm_response(contents[1:].strip(), 
                                    provider=provider,
                                    modelname=modelname,
                                    temperature=temperature,)
    return response
    



def pdf2RAG(pdf):
    """
    Converts a PDF to the Research Assistant's format.

    Parameters:
        pdf (str): The path to the PDF file.

    Returns:
        str: A success message indicating that the PDF has been loaded into the Research Assistant.
    """
    pdf_panel.set_pdf(pdf)
    notebook.active = 2 #interrogate tab
    return "PDF loaded into Research Assistant"

medrxiv_panel = MedrXivPanel(pdf2RAG=pdf2RAG)
critique_panel = pn.pane.HTML("<html>Critique of study:</html>", sizing_mode='stretch_both')

terminal = pn.widgets.Terminal(
    "Waiting for AI ...",
    options={"cursorBlink": True},
    sizing_mode='stretch_both'
)
#redirect all terminal output to our user unterface terminal
sys.stdout = terminal

def on_llm_selected(event):
    print(f"selected LLM: {event.new}")




chat_bot = pn.chat.ChatInterface(callback=get_response,
                                 callback_exception='verbose', 
                                 user='Horst', 
                                 show_rerun=False, 
                                 show_undo=False,
                                 sizing_mode='stretch_both')

chat_bot.send("""Ask me any question, and I'll try to get the selected LLM to answer it.
              If you want a comprehensive report, start the question with '@' and I will get my agents to research the literature 
              and the internet for you.
              """, 
              user="Assistant", 
              respond=False)

research_assistant_panel= pn.Row(
        chat_bot, 
        #terminal, 
        sizing_mode='stretch_both'
)

pdf_panel=PDFPanel()


notebook = pn.Tabs(('Research Assistant', research_assistant_panel),
                   ('MedrXiv News', medrxiv_panel), 
                   #('Chat', chat_panel), 
                   ('Interrogate', pdf_panel), 
                   ('Debug', terminal),
                   margin=8, sizing_mode='stretch_both'
)

ps = PublicationStorage()
publications_in_storage = ps.count_publications()

# Instantiate the template with widgets displayed in the sidebar
API_accordion = currentApiKeySettings.get_UI_widget()
LLM_accordion = currentLLMSettings.get_UI_widget()
Researcher_accordion = currenttResearcherSettings.get_UI_widget()
template = pn.template.FastListTemplate(
    title=f"My Research Assistant - {publications_in_storage} publications archived locally",
    sidebar=[API_accordion,
             LLM_accordion,
             Researcher_accordion]
)

# Append a layout to the main area, to demonstrate the list-like API
template.main.append(
    notebook
)

if __name__ == '__main__':
    template.servable()
    pn.serve(template)