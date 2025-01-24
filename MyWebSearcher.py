
from phi.assistant import Assistant
from phi.tools.duckduckgo import DuckDuckGo
from phi.tools.wikipedia import WikipediaTools
from phi.tools.pubmed import PubmedTools
from dotenv import load_dotenv, find_dotenv

query = "Effect of Doxycycline on scabies"
agents = []
load_dotenv()

Topassistant= Assistant(tools=[PubmedTools(), WikipediaTools(), DuckDuckGo()], show_tool_calls=True)
DDGAssistant= Assistant(tools=[DuckDuckGo()], show_tool_calls=True)
PMAssistant= Assistant(tools=[PubmedTools()], show_tool_calls=True)
WPAssistant= Assistant(tools=[WikipediaTools()], show_tool_calls=True)

agents.append(('DuckDuckGo', DDGAssistant))
agents.append(('PubMed', PMAssistant))
agents.append(('Wikipedia', WPAssistant))
agents.append(('Top', Topassistant))

for agent in agents:
    print(f"=========== {agent[0]} ===========")
    agent[1].print_response(query)
