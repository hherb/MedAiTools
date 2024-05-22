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

import panel as pn
from panel.widgets import Tqdm
import datetime as dt
import html
import json
from MedrXivScraper import MedrXivScraper

pn.extension('texteditor', loading_indicator=True, design="material")

styles = {
    'background-color': '#F6F6F6', 
    'border': '2px solid #007BFF',
    'border-radius': '5px', 'padding': '10px',
    'header': "background-color: #007BFF; color: #fff; padding: 20px; text-align: center;",
    '.publication-title' :  "color: #007BFF; font-size: 1.5em;"
}

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
	<meta charset="UTF-8">
	<meta name="viewport" content="width=device-width, initial-scale=1.0">
	<title>MedRxiv reading list</title>
</head>
<body>
	
	{html}
	
	<script>
		function toggleAbstract(button) {{
			var abstract = button.nextElementSibling;
			abstract.style.display = abstract.style.display === 'none' ? 'block' : 'none';
		}}
		function toggleCritique(button) {{
			var critique = button.nextElementSibling;
			critique.style.display = critique.style.display === 'none' ? 'block' : 'none';
		}}
	</script>
</body>
</html>
"""


class MedrXivPanel(pn.viewable.Viewer):
    """A HTML panel displaying publications fetched from medrXiv"""

    def __init__(self):    
        
        self.keywordlist = ["GPT4", "machine learning", "deep learning", "large language model", "LLM", "Anthropic", "OpenAI", "Artifical Intelligence"]
        self.html_panel = pn.pane.HTML("<html>Hit 'Fetch' button ...", 
                                       name='MedrXiv Publications', 
                                       sizing_mode='stretch_both')
        self.search_btn = pn.widgets.Button(name='Fetch', button_type='primary', width=60, margin=25)
        self.search_btn.on_click(self.fetch_publications)
        end_date = dt.datetime.now()	#today
        start_date = end_date-dt.timedelta(days=2)
        self.date_range_picker = pn.widgets.DateRangePicker(name='Date Range', value=(start_date, end_date))
        self.keywords= pn.widgets.TextInput(name='Keywords', value=', '.join(self.keywordlist), align=('center'), sizing_mode='stretch_width')
        self.heading= pn.pane.Markdown("## Your MedrXiv publications (not fetched yet)", sizing_mode='stretch_width')
        self.panel = pn.Column(self.heading, 
                                pn.Column(self.html_panel, scroll=True, sizing_mode='stretch_both'),
                                self.keywords, 
                                pn.Row(self.date_range_picker, self.search_btn),
                                sizing_mode='stretch_both')

    def set_heading(self, from_date, to_date, keywords="", domains=""):
        template= """<div style="background-color:#85a3e0; color:white; border-radius:10px; padding:10px;">
                <h2>Your MedrXiv reading list for {from_date} - {to_date}</h2>
                </div>"""       
        self.heading.object=(template.format(from_date=from_date, to_date=to_date, keywords=keywords, domains=domains))
        

    def fetch_publications(self, event):
        """
        The function fetches publications from medrXiv based on specified criteria, displays them in a
        panel with detailed information, and provides options to read abstracts, critiques, and access
        full PDFs.
        
        :param event: The `event` parameter in the `fetch_publications` method is not being used in the
        provided code snippet. It seems to be an unused parameter in this context. If you intended to
        use it for some specific purpose or functionality, you can modify the method to incorporate the
        `event` parameter as
        """
        """Fetch publications from medrXiv and display them in the panel"""
        # Fetch publications
        start_date, end_date = self.date_range_picker.value
        scraper = MedrXivScraper(from_date=start_date.strftime("%Y-%m-%d"), end_date=end_date.strftime("%Y-%m-%d"), summarize=True)
        scraper.set_keywords([keyword.strip() for keyword in self.keywords.value.split(',')]) 
        
        self.set_heading(from_date=start_date.strftime("%Y-%m-%d"), to_date=end_date.strftime("%Y-%m-%d"), keywords=self.keywords.value)
        self.html_panel.object = "<html><p>Fetching and analysing publications, this might take a while ...</p></html>"
        #scraper.set_category(self, categories=["Emergency Medicine", ], priority=True)
        publications = scraper.fetch_medrxiv_publications(testing=True)
        
        # Update the panel with the fetched publications
        #self.html_panel.object = scraper.list_abstracts(publications, format="html")
        html=""
        for publication in publications:
            pdfurl = scraper.get_pdf_URL(publication)
            html+="""<div style="border:1px solid black; border-radius: 10px; padding: 10px; background-color: #ebf0fa;">"""
            html+=f"""<h3>{publication['title']}</h3>"""
            html+=f"""<b>{publication['authors']}</b> {publication['date']}"""
            html+="<hr>"
            html+=f"""<p>{publication['summary']}</p>"""
            html+=f"""<button onclick="toggleAbstract(this)"> Read Abstract </button>
					<div class="abstract" style="display:none;"><p>{publication['abstract']}</p></div>
					<button onclick="toggleCritique(this)"> Read Critique </button>
					<div class="abstract" style="display:none;"><p>{publication['critique']}</p></div>
				    <a href="{pdfurl}" target="_blank"> <button> Full PDF </button></a>"""
            html+="</div>"
            html+="<br>"
        htmlpage = HTML_TEMPLATE.format(html=html)
        self.html_panel.object = htmlpage

    def __panel__(self):
        return self.panel



if pn.state.served:
    pn.extension(sizing_mode="stretch_width")

    MedrXivPanel().servable()