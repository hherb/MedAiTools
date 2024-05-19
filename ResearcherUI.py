import panel as pn   #! pip install panel
from time import sleep
import asyncio
from Researcher import research
pn.extension()

def get_response(contents, user, instance):
    response = asyncio.run(research(contents, output_fname="UItest.md") )
    return response

chat_bot = pn.chat.ChatInterface(callback=get_response, max_height=500)
chat_bot.send("Ask me a research question", user="Assistant", respond=False)
chat_bot.servable()