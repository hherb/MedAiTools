# MedrXivPanel.py
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

"""This module provides a Panel app (web GUI) to fetch and display publications from medrXiv. 
The app allows users to specify date ranges and keywords for fetching publications and 
provides options to read abstracts, critiques, and download and access full PDFs.
"""

import panel as pn
from panel.widgets import Tqdm
import datetime as dt
import html
import json
from functools import partial
from MedrXivScraper import MedrXivScraper, MedrXivAssistant

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

    def __init__(self, pdf2RAG=None):
        """
        The `MedrXivPanel` class provides a Panel app (web GUI) to fetch and display publications from
        medrXiv. The app allows users to specify date ranges and keywords for fetching publications and
        provides options to read abstracts, critiques, and download and access full PDFs.

        :param pdf2RAG: The `pdf2RAG` parameter in the `MedrXivPanel` class is a UI callback
        """    
        
        self.pdf2RAG=pdf2RAG
        self.keywordlist = ["GPT4", "machine learning", "deep learning", "large language model", "LLM", "Anthropic", "OpenAI", "Artifical Intelligence"]
        self.html_panel = pn.panel("<html>Hit 'Fetch' button ...", 
                                       name='MedrXiv Publications', 
                                       sizing_mode='stretch_both')
        
        self.fetch_btn = pn.widgets.Button(name='Fetch', button_type='primary', width=60, margin=25)
        self.fetch_btn.on_click(self.fetch_publications)

        self.search_btn = pn.widgets.Button(name='Search', button_type='primary', width=60, margin=25)
        self.search_btn.on_click(self.find_publications)

        end_date = dt.datetime.now()	#today
        start_date = end_date-dt.timedelta(days=2)
        self.date_range_picker = pn.widgets.DateRangePicker(name='Date Range', value=(start_date, end_date))
        self.keywords= pn.widgets.TextInput(name='Keywords', value=', '.join(self.keywordlist), align=('center'), sizing_mode='stretch_width')
        self.heading= pn.pane.Markdown("## Your MedrXiv publications (not fetched yet)", sizing_mode='stretch_width')
        self.display_column=pn.Column()
        #self.display_panel = pn.panel(self.display_column, sizing_mode='stretch_both')
        self.panel = pn.Column(self.heading, 
                                pn.Column(self.display_column, scroll=True, sizing_mode='stretch_both'),
                                pn.Row(self.keywords, self.search_btn),
                                pn.Row(self.date_range_picker, self.fetch_btn),
                                sizing_mode='stretch_both')



    def set_heading(self, from_date=None, to_date=None, keywords="", domains=""):
        if from_date is not None and to_date is not None:
            template= """<div style="background-color:#85a3e0; color:white; border-radius:10px; padding:10px;">
                <h2>Your MedrXiv reading list for {from_date} - {to_date}</h2>
                </div>"""
            self.heading.object=(template.format(from_date=from_date, to_date=to_date, keywords=keywords, domains=domains))
        else:
            template= """<div style="background-color:#85a3e0; color:white; border-radius:10px; padding:10px;">
                <h2>Publications found in local archive:</h2>
                </div>"""       
        self.heading.object=(template)



    def find_publications(self, event):
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
        scraper = MedrXivScraper(tqdm=Tqdm()) 
        
        self.set_heading(from_date="not specified", to_date="", keywords=self.keywords.value)
        #self.html_panel.object = "<html><p>Fetching and analysing publications, this might take a while ...</p></html>"
        #scraper.set_category(self, categories=["Emergency Medicine", ], priority=True)
        publications = scraper.fetch_publications_by_keywords(keywords=self.keywords.value.split(',') )
        self.display_publications(publications)

    def open_pdf(self, pdf_path, event):
        if self.pdf2RAG is not None:
            self.pdf2RAG(pdf_path)
        print(f"Opening PDF: {pdf_path}")    

    def display_publications(self, publications: dict):
        """
        The function displays the fetched publications in a panel with detailed information and provides
        options to read abstracts, critiques, and access full PDFs.
        :param publications:   a medrXiv publication dictionary
        """
        # Update the panel with the fetched publications
        #self.html_panel.object = scraper.list_abstracts(publications, format="html")
        display_widgets=[]
        self.display_column.clear()
        for publication in publications:
            html=""
            #pdfurl = scraper.get_pdf_URL(publication)
            html+="""<div style="border:1px solid black; border-radius: 10px; padding: 10px; background-color: #ebf0fa;">"""
            html+=f"""<h3>{publication['title']}</h3>"""
            html+=f"""{publication['authors']} {publication['date']}"""
            html+="<hr>"
            html+=f"""<p>{publication['summary']}</p>"""
            html+=f"""<button onclick="toggleAbstract(this)"> Read Abstract </button>
                    <div class="abstract" style="display:none;"><p>{publication['abstract']}</p></div>
                    <button onclick="toggleCritique(this)"> Read Critique </button>
                    <div class="abstract" style="display:none;"><p>{publication['abstract_critique']}</p></div>"""
            html+="</div>"
            html+="<br>"
            htmlpage = HTML_TEMPLATE.format(html=html)
            htmlpane = pn.pane.HTML(htmlpage)
                    
            if 'pdf_path' in publication:
                pdf_path=publication['pdf_path']
            else:
                try:
                    info=pn.state.notifications.info('Attempting to fetch the PDF from the internet...', duration=0)
                    pdf_path = scraper.fetch_pdf_from_publication(publication)
                    info.destroy()
                except:
                    info.destroy()
                    info= pn.state.notifications.info('Failed to locate PDF, and failed to retrieve it from the internet', duration=10)
                    pdf_path=""
             # Define a callback function that takes the pdf_path as a parameter
            btn = pn.widgets.Button(name=f"Read full paper", button_type='primary', width=60, margin=25)
            btn.on_click(partial(self.open_pdf, pdf_path))
            display_widgets.append(pn.Column(htmlpane, btn))
        scrollable_panel = pn.Column(*display_widgets, scroll=True) 
        self.display_column.append(scrollable_panel)
        


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
        scraper = MedrXivScraper()
        assistant = MedrXivAssistant()
        from_date=start_date.strftime("%Y-%m-%d")
        to_date=end_date.strftime("%Y-%m-%d")
        self.set_heading(from_date=from_date, to_date=to_date, keywords=self.keywords.value)
        self.html_panel.object = "<html><p>Fetching and analysing publications, this might take a while ...</p></html>"
        #scraper.set_category(self, categories=["Emergency Medicine", ], priority=True)
        publications = scraper.fetch_medrxiv_publications(from_date=from_date, to_date=to_date, keywords=self.keywords.value.split(',') )
        publications=assistant.analyze_publications(publications)
        self.display_publications(publications)  

        

    def __panel__(self):
        return self.panel




if __name__ == "__main__":    
    panel= MedrXivPanel()
    panel.servable()
    pn.serve(panel)