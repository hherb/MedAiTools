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

from Researcher import research
from MedrXivPanel import MedrXivPanel 
from RAG_UI import PDFPanel
from medai.tools.apikeys import load_api_keys  

pn.extension('texteditor', loading_indicator=True, design="material")

#The API keys needed for this to work - they will be loaded from the os environment:

APIS=('OPENAI_API_KEY', 'TAVILY_API_KEY', 'LLAMA_CLOUD_API_KEY')
load_api_keys(APIS)

pn.extension('perspective', 'terminal', notifications=True, loading_indicator=True, design="material")


def get_response(contents, user, instance):
    info= pn.state.notifications.info('Waiting for the AI agents response ...', duration=0)
    notebook.active = 3 #debug tab
    response = asyncio.run(research(contents) )
    info.destroy()
    notebook.active = 0 #research assistant tab
    return response

def pdf2RAG(pdf):
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

user_setter = pn.widgets.TextInput(name='User', placeholder='Enter your name here', sizing_mode='stretch_width')
openai_api_setter = pn.widgets.TextInput(name='OpenAI API Key', placeholder='Enter your OpenAI API key here', sizing_mode='stretch_width')
tavily_api_setter = pn.widgets.TextInput(name='Tavily API Key', placeholder='Enter your Tavily API key here', sizing_mode='stretch_width')

chat_bot = pn.chat.ChatInterface(callback=get_response, 
                                 user='Horst', 
                                 show_rerun=False, 
                                 show_undo=False,
                                 sizing_mode='stretch_both')

chat_bot.send("Ask me a research question", user="Assistant", respond=False)

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


# Instantiate the template with widgets displayed in the sidebar
template = pn.template.FastListTemplate(
    title="My Research Assistant",
    sidebar=[user_setter, 
             openai_api_setter, 
             tavily_api_setter],
)

# Append a layout to the main area, to demonstrate the list-like API
template.main.append(
    notebook
)

if __name__ == '__main__':
    template.servable()
    pn.serve(template)