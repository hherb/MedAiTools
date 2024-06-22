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
import os, os.path
import panel as pn
from panel.widgets import Tqdm
import datetime as dt
#import html
#import json
from functools import partial
from PGMedrXivScraper import MedrXivScraper, MedrXivAssistant
from DailyNews import NewsPanel

pn.extension('texteditor', notifications=True, loading_indicator=True, design="material")

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

    def __init__(self, pdf2RAG=None, db=None):
        """
        The `MedrXivPanel` class provides a Panel app (web GUI) to fetch and display publications from
        medrXiv. The app allows users to specify date ranges and keywords for fetching publications and
        provides options to read abstracts, critiques, and download and access full PDFs.

        :param pdf2RAG: The `pdf2RAG` parameter in the `MedrXivPanel` class is a UI callback
        """    
        
        self.pdf2RAG=pdf2RAG
        self.scraper = MedrXivScraper(tqdm=Tqdm()) 
        self.keywordlist = ["GPT4", "machine learning", "deep learning", "large language model", "LLM", "Anthropic", "OpenAI", "Artifical Intelligence"]
        self.html_panel = pn.panel("<html>Hit 'Fetch' button ...", 
                                       name='MedrXiv Publications', 
                                       sizing_mode='stretch_both')
        
        self.fetch_btn = pn.widgets.Button(name='Fetch', button_type='primary', width=60, margin=25)
        self.fetch_btn.on_click(self.find_publications)

        self.search_btn = pn.widgets.Button(name='Search', button_type='primary', width=60, margin=25)
        self.search_btn.on_click(self.find_publications)

        end_date = dt.datetime.now()	#today
        start_date = end_date-dt.timedelta(days=2)
        self.date_range_picker = pn.widgets.DateRangePicker(name='Date Range', value=(start_date, end_date))
        self.use_dates_for_search_tickbox = pn.widgets.Checkbox(name='Use dates for search', value=False)
        self.keywords= pn.widgets.TextInput(name='Keywords', value=', '.join(self.keywordlist), align=('center'), sizing_mode='stretch_width')
        self.any_or_all= pn.widgets.RadioButtonGroup(name='Any or all keywords', options=['Any', 'All'], value='Any', align=('center'), sizing_mode='stretch_width')    
        self.heading= pn.pane.Markdown("## Your MedrXiv publications (not fetched yet)", sizing_mode='stretch_width')
        self.display_column=pn.Column()
        #self.display_panel = pn.panel(self.display_column, sizing_mode='stretch_both')
        self.panel = pn.Column(self.heading, 
                                pn.Column(self.display_column, scroll=True, sizing_mode='stretch_both'),
                                pn.Row(self.keywords, self.any_or_all, self.search_btn),
                                pn.Row(self.use_dates_for_search_tickbox , self.date_range_picker, self.fetch_btn),
                                sizing_mode='stretch_both')

    def __panel__(self):
        return self.panel

    def set_heading(self, title_str= None, from_date=None, to_date=None, keywords="", domains=""):
        """Sets the heading of the panel to display the search criteria and results.
        :param title_str: The title of the panel
        :param from_date: The start date for the search
        :param to_date: The end date for the search
        :param keywords: The keywords used for the search
        :param domains: The domains to search for
        """
        template= """<div style="background-color:#85a3e0; color:white; border-radius:10px; padding:10px;">
                <h2>Your MedrXiv reading list: {title_str} </h2>
                </div>"""
        if title_str is not None:
            title= template.format(title_str=title_str)
            self.heading.object= title
        elif from_date is not None and to_date is not None:
            title_str =  f"for {from_date} - {to_date}"
            self.heading.object=template.format(title_str=title_str)
        else:
            template= """<div style="background-color:#85a3e0; color:white; border-radius:10px; padding:10px;">
                <h2>Publications found in local archive:</h2>
                </div>"""       
            self.heading.object=(template)


    def find_publications(self, event):
        """
        The function finds publications from medrXiv based on specified criteria, displays them in a
        panel with detailed information, and provides options to read abstracts, critiques, and access
        full PDFs.
        
        :param event: The `event` parameter in the `fetch_publications` method is not being used in the
        provided code snippet. It is passed by a UI element and not required in the function.
        """
        # Fetch publications
        if self.use_dates_for_search_tickbox.value:
            from_date, to_date = self.date_range_picker.value
            from_date=from_date.strftime("%Y-%m-%d")
            to_date=to_date.strftime("%Y-%m-%d")
        else:
            from_date = None
            to_date = None
        print(f"Searching for publications from {from_date} to {to_date}")
        publications = self.scraper.db.search_for(keywords=self.keywords.value.split(','), any_or_all = self.any_or_all.value, from_date=from_date, to_date=to_date)

        print(f"Found publications")
        self.display_publications(publications)

    def open_pdf(self, publication,  event=None ):
        """
        This function opens a PDF file, ingests it into the vector store (if not ingested already) 
        and displays it in the Research Assistant GUI for interrogation.
        :param pdf_path: The path to the PDF file to open
        """
        info=pn.state.notifications.info('Retrieving PDF...', duration=0)
        pdf_path = self.scraper.pdf_path(publication)
        pdf_path = os.path.expanduser(pdf_path)
        info.destroy()
        if not pdf_path:
            info=pn.state.notifications.info('Failed to locate PDF, attempting to retrieve it from the internet', duration=0)
            try:         
                pdf_path = self.scraper.fetch_pdf_from_publication(publication)
                pdf_path = os.path.expanduser(pdf_path)
                info.destroy()
            except:
                info.destroy()
                info= pn.state.notifications.info('Failed to locate PDF, and failed to retrieve it from the internet', duration=10)
                pdf_path=""
       
        if pdf_path and self.pdf2RAG is not None:
            self.pdf2RAG(pdf_path)
        #print(f"Opening PDF: {pdf_path}")   
        # 
    

    def display_publications(self, publications: list[dict]):
        self.display_column.clear()
        self.newspanel=NewsPanel(news=publications, callback=self.open_pdf)
        self.display_column.append(self.newspanel)

    def display_publications_old(self, publications: list[dict]):
        """
        The function displays the publications in a panel with detailed information and provides
        options to read abstracts, critiques, and access full PDFs.
        If the PDF is not available locally, the function attempts to fetch it from the internet.
        :param publications:   a list of medrXiv publication dictionaries
        """
        # Update the panel with the fetched publications
        #self.html_panel.object = scraper.list_abstracts(publications, format="html")
        display_widgets=[]
        self.display_column.clear()
        counter=0
        for publication in publications:
            counter+=1
            html=""
            #pdfurl = scraper.get_pdf_URL(publication)
            html+="""<div style="border:1px solid black; border-radius: 10px; padding: 10px; background-color: #ebf0fa;">"""
            html+=f"""<h3>{publication['title']}</h3>"""
            html+=f"""{publication['authors']} {publication['date']}"""
            html+="<hr>"
            counter+=1

            try:
                html+=f"""<p>{publication['summary']}</p>"""
            except KeyError:
                assistant = MedrXivAssistant(tqdm=Tqdm())
                publication=assistant.summarize_publication(publication, commit=True) 
                html+=f"""<p>{publication['abstract']}</p>"""

            html+=f"""<button onclick="toggleAbstract(this)"> Read Abstract </button>
                    <div class="abstract" style="display:none;"><p>{publication['abstract']}</p></div>"""
                    #<button onclick="toggleCritique(this)"> Read Critique </button>
                    #<div class="abstract" style="display:none;"><p>{publication['abstract_critique']}</p></div>"""
            html+="</div>"
            html+="<br>"
            htmlpage = HTML_TEMPLATE.format(html=html)
            htmlpane = pn.pane.HTML(htmlpage)
                    
            pdf_path = self.scraper.pdf_path(publication, fetch=True) #Will attempt to fetch it if not already available
            pdf_path = os.path.expanduser(pdf_path)
             # Define a callback function that takes the pdf_path as a parameter    
            btn = pn.widgets.Button(name=f"Read full paper", button_type='primary', width=60, margin=10)
            btn.on_click(partial(self.open_pdf, publication))
            if not pdf_path:
                btn.disabled=True
            btn_critique = pn.widgets.Button(name=f"Critique", button_type='primary', width=60, margin=10)
            display_widgets.append(pn.Column(htmlpane, btn, btn_critique))
        self.set_heading(title_str = f"{counter} publications found", keywords=self.keywords.value)
        scrollable_panel = pn.Column(*display_widgets, scroll=True) 
        self.display_column.append(scrollable_panel)
        


    # def fetch_publications(self, event):
    #     """
    #     The function fetches publications from medrXiv based on specified criteria, displays them in a
    #     panel with detailed information, and provides options to read abstracts, critiques, and access
    #     full PDFs.
        
    #     :param event: The `event` parameter in the `fetch_publications` method is not being used in the
    #     provided code snippet. It seems to be an unused parameter in this context. If you intended to
    #     use it for some specific purpose or functionality, you can modify the method to incorporate the
    #     `event` parameter as
    #     """
    #     """Fetch publications from medrXiv and display them in the panel"""
    #     # Fetch publications
        
    #     from_date = None
    #     to_date = None
    #     if self.use_dates_for_search.value:
    #         start_date, end_date = self.date_range_picker.value
    #         from_date=start_date.strftime("%Y-%m-%d")
    #         to_date=end_date.strftime("%Y-%m-%d")
        
        
    #     self.set_heading(from_date=from_date, to_date=to_date, keywords=self.keywords.value)
        
    #     self.html_panel.object = "<html><p>Fetching and analysing publications, this might take a while ...</p></html>"
    #     #scraper.set_category(self, categories=["Emergency Medicine", ], priority=True)
    #     publications = self.scraper.fetch_publications(from_date=from_date, to_date=to_date, keywords=self.keywords.value.split(',') )
    #     #publications=assistant.analyze_publications(publications)
    #     self.display_publications(publications)  

        




if __name__ == "__main__":    
    panel= MedrXivPanel()
    panel.servable()
    pn.serve(panel)