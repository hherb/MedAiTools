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

import panel as pn   #! pip install panel
from panel.widgets import Tqdm
from time import sleep
import asyncio
import sys

from Researcher import research, AVAILABLE_CONFIGS
from MedrXivPanel import MedrXivPanel 
from RAG_UI import PDFPanel
from medai.tools.apikeys import load_api_keys  
from PersistentStorage import PublicationStorage
#from EventDispatcher import EventDispatcher
from medai import LLM   

pn.extension('texteditor', loading_indicator=True, design="material")

#The API keys needed for this to work - they will be loaded from the os environment:

APIS=('OPENAI_API_KEY', 'TAVILY_API_KEY', 'LLAMA_CLOUD_API_KEY')
load_api_keys(APIS)

pn.extension('perspective', 'terminal', notifications=True, loading_indicator=True, design="material")


async def get_response_async(contents):
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
        response = await asyncio.wait_for(research(contents), timeout=240)  # 4 minutes timeout
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
         return asyncio.run(get_response_async(contents))
    else:
        #just answer a simple question
        modelname = f"ollama/{llm_setter.value}"
        print(f"model used:{modelname}")
        print(f"attempting to answer question using LLM: {modelname}")
        response = LLM.answer_this(contents[1:].strip(), 
                                   modelname=modelname,
                                   temperature=setter_llm_temperature.value,)
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

# API key settings
user_setter = pn.widgets.TextInput(name='User', placeholder='Enter your name here', sizing_mode='stretch_width')
serper_api_setter = pn.widgets.TextInput(name='Serper API Key', placeholder='Enter your Serper API key here', sizing_mode='stretch_width')
tavily_api_setter = pn.widgets.TextInput(name='Tavily API Key', placeholder='Enter your Tavily API key here', sizing_mode='stretch_width')
openai_api_setter = pn.widgets.TextInput(name='OpenAI API Key', placeholder='Enter your OpenAI API key here', sizing_mode='stretch_width')
groq_api_setter = pn.widgets.TextInput(name='Groq API Key', placeholder='Enter your Groq API key here', sizing_mode='stretch_width')
huggingface_api_setter = pn.widgets.TextInput(name='Huggingface API Key', placeholder='Enter your Huggingface API key here', sizing_mode='stretch_width')
google_api_setter = pn.widgets.TextInput(name='Google API Key', placeholder='Enter your Google API key here', sizing_mode='stretch_width')
API_accordion=pn.Accordion(name='API keys', sizing_mode='stretch_width')
API_accordion.append(pn.Column(user_setter, openai_api_setter, tavily_api_setter, name='API Keys'))

#our local LLMs - user selectable
llm_setter = pn.widgets.Select(name="LLM", options=[model['name'] for model in LLM.list_local_models()])
llm_setter.param.watch(on_llm_selected, 'value')
LLM_accordion = pn.Accordion(name='local LLMs', sizing_mode='stretch_width')
LLM_accordion.append(llm_setter)

setter_llm_temperature = pn.widgets.FloatSlider(name='Temperature', start=0.0, end=1.0, step=0.01, value=0.3)
setter_llm_systemprompt = pn.widgets.TextAreaInput(name='System Prompt', placeholder='Enter your system prompt here', sizing_mode='stretch_width')
llm_params = pn.Column(setter_llm_temperature, setter_llm_systemprompt, name='LLM Parameters')
LLM_accordion.append(llm_params)

setter_gptr_retriever = pn.widgets.Select(name="Retriever", options=['tavily', 'serper',  'google',  'searxing', 'duckduckgo'], value='tavily')
setter_gptr_provider = pn.widgets.Select(name="LLM provider", options=list(AVAILABLE_CONFIGS.keys()), value='ollama')
setter_gptr_baseurl = pn.widgets.TextInput(name='LLM base URL', value="http://localhost:11434", sizing_mode='stretch_width')
setter_gptr_fastllm = pn.widgets.TextInput(name='Fast LLM model', value="llama3-groq-tool-use:8b-q8_0", sizing_mode='stretch_width')
setter_gptr_smartllm = pn.widgets.TextInput(name='Smart LLM model', value="nous-hermes2:34b-yi-q8_0", sizing_mode='stretch_width')
setter_gptr_fast_token_limit = pn.widgets.IntInput(name='Fast token limit', value=3000, sizing_mode='stretch_width')
setter_gptr_smart_token_limit = pn.widgets.IntInput(name='Smart token limit', value=4000, sizing_mode='stretch_width')
setter_gptr_browse_chunk_max_length = pn.widgets.IntInput(name='Browse chunk max length', value=8192, sizing_mode='stretch_width')
setter_gptr_summary_token_limit = pn.widgets.IntInput(name='Summary token limit', value=700, sizing_mode='stretch_width')
setter_gptr_temperature = pn.widgets.FloatSlider(name='Temperature', start=0.0, end=1.0, step=0.01, value=0.3)
setter_gptr_memory_backend= pn.widgets.Select(name="Memory backend", options=['local', 'remote'], value='local')
setter_gptr_total_words = pn.widgets.IntInput(name='Total words', value=800, sizing_mode='stretch_width')
setter_gptr_report_format = pn.widgets.TextInput(name='Report format', value="APA", sizing_mode='stretch_width')
setter_gptr_max_iterations = pn.widgets.IntInput(name='Max iterations', value=5, sizing_mode='stretch_width')
setter_gptr_agent_role = pn.widgets.TextInput(name='Agent role', value=None, sizing_mode='stretch_width')
setter_gptr_scraper = pn.widgets.TextInput(name='Scraper', value="bs", sizing_mode='stretch_width')
setter_gptr_max_subtopics = pn.widgets.IntInput(name='Max subtopics', value=3, sizing_mode='stretch_width')
setter_gptr_max_search_results_per_query = pn.widgets.IntInput(name='Max search results per query', value=10, sizing_mode='stretch_width')
setter_gptr_user_agent = pn.widgets.TextInput(name='User agent', value="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/")
setter_gptr_embedding_provider = pn.widgets.Select(name="Embedding provider", options=['openai', 'anthropic', 'groq',  'google',  'ollama'], value='ollama')    
setter_gptr_embedding_model= pn.widgets.TextInput(name='Embedding model', value="mxbai-embed-large", sizing_mode='stretch_width')
gptr_params = pn.Column(setter_gptr_retriever, setter_gptr_provider, setter_gptr_baseurl, setter_gptr_fastllm, setter_gptr_smartllm, setter_gptr_fast_token_limit, setter_gptr_smart_token_limit, setter_gptr_browse_chunk_max_length, setter_gptr_summary_token_limit, setter_gptr_temperature, setter_gptr_memory_backend, setter_gptr_total_words, setter_gptr_report_format, setter_gptr_max_iterations, setter_gptr_agent_role, setter_gptr_scraper, setter_gptr_max_subtopics, setter_gptr_max_search_results_per_query, setter_gptr_user_agent, setter_gptr_embedding_provider, setter_gptr_embedding_model, name='GPT Researcher Parameters')
LLM_accordion.append(gptr_params)

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
template = pn.template.FastListTemplate(
    title=f"My Research Assistant - {publications_in_storage} publications archived locally",
    sidebar=[API_accordion,
             LLM_accordion],
)

# Append a layout to the main area, to demonstrate the list-like API
template.main.append(
    notebook
)

if __name__ == '__main__':
    template.servable()
    pn.serve(template)