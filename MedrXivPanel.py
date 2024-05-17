import panel as pn
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

class MedrXivPanel(pn.viewable.Viewer):
    """A HTML panel displaying publications fetched from medrXiv"""

    def __init__(self):    
        
        self.keywordlist = ["GPT4", "machine learning", "deep learning", "large language model", "LLM", "Anthropic", "OpenAI", "Artifical Intelligence"]
        self.html_panel = pn.pane.HTML("<html>Hit 'Fetch' button ...", 
                                       styles=styles, 
                                       name='MedrXiv Publications', 
                                       sizing_mode='stretch_both')
        self.search_btn = pn.widgets.Button(name='Fetch', button_type='primary', width=60, margin=25)
        self.search_btn.on_click(self.fetch_publications)
        end_date = dt.datetime.now()	#today
        start_date = end_date-dt.timedelta(days=2)
        self.date_range_picker = pn.widgets.DateRangePicker(name='Date Range', value=(start_date, end_date))
        self.keywords= pn.widgets.TextInput(name='Keywords', value=', '.join(self.keywordlist), align=('center'), sizing_mode='stretch_width')
        self.panel = pn.Column(pn.Column(self.html_panel, scroll=True, sizing_mode='stretch_both'),
                               self.keywords, 
                               pn.Row(self.date_range_picker, self.search_btn),
                               sizing_mode='stretch_both')


    def fetch_publications(self, event):
        """Fetch publications from medrXiv and display them in the panel"""
        # Fetch publications
        start_date, end_date = self.date_range_picker.value

        scraper = MedrXivScraper(from_date=start_date.strftime("%Y-%m-%d"), end_date=end_date.strftime("%Y-%m-%d"), summarize=True)
        scraper.set_keywords([keyword.strip() for keyword in self.keywords.value.split(',')]) 
        #scraper.set_category(self, categories=["Emergency Medicine", ], priority=True)
        publications = scraper.fetch_medrxiv_publications(testing=False)
        
        # Update the panel 
        #escaped_html=html.escape(scraper.list_abstracts(publications, format="html"))
        #iframe_html = f'<iframe srcdoc="{escaped_html}" style="height:100%; width:100%" frameborder="0"></iframe>'
        #self.html_panel.object = iframe_html
        self.html_panel.object = scraper.list_abstracts(publications, format="html")

    def __panel__(self):
        return self.panel



if pn.state.served:
    pn.extension(sizing_mode="stretch_width")

    MedrXivPanel().servable()