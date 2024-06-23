import panel as pn


pn.extension()

newsitem_format ="""
<h3>{title}</h3>
{authors} - {date}
<hr />
{summary}
"""

def full_paper(news):
      print(f"Full paper clicked: {news['title']}")

class NewsPanel(pn.viewable.Viewer):
    _callback = None
    def __init__(self, news=None, callback=full_paper, set_heading_callback=None):
        NewsPanel._callback = callback
        self.set_heading=set_heading_callback
        self.newsfeed_panel = pn.Feed(load_buffer=20, scroll=True,sizing_mode='stretch_both')
        if not news:
            from PGMedrXivScraper import MedrXivScraper
            self.scraper = MedrXivScraper()
            self.news = self.scraper.fetch_latest_publications()
        else:
            self.news=news
        i=0
        for n in self.news:
            self.newsfeed_panel.append( HeadlinePanel(n, self.on_paper_click).get_panel()) 
            i+=1
        self.panel = pn.panel(self.newsfeed_panel, sizing_mode='stretch_both')
        self.set_heading(title_str=f"{i} matching publications found in archive")

    def __panel__(self):
        return self.panel

    @classmethod
    def on_paper_click(cls, event, news):
        if cls._callback:
            cls._callback(news)  
        else:
            print(f"Full paper clicked: {news['title']}")



class HeadlinePanel:
    def __init__(self, news, callback):
        self.outer_style = {
            'background': '#E0F7FA',
            'border-radius': '10px',
            'border': '1px solid black',
            'padding': '10px',
            'box-shadow': '5px 5px 5px #bcbcbc',
            'margin': "10px",
        }
        # Format the display text using Markdown with an HTML anchor tag for the link
        display_text = newsitem_format.format(**news)
        # Create a Markdown pane with the formatted text
        fullpaper_btn = pn.widgets.Button(name="Full paper", button_type="primary", width=100)
        fullpaper_btn.on_click(lambda event: callback(event, news=news))
        buttonrow = pn.Row(fullpaper_btn, width=100)
        content_panel = pn.Column(pn.pane.HTML(display_text, sizing_mode='stretch_width'), 
                                  buttonrow, 
                                  sizing_mode='stretch_width',
                                  styles=self.outer_style,)
        self.panel = content_panel

    def get_panel(self):
        # Return the panel for integration into a pn.Feed or other layouts
        return self.panel




if __name__ == "__main__":
    # try:
    #     #testing with cached data
    #     import json
    #     with open('news_data.json', 'r') as file:
    #         news = json.load(file)
    # except:
    #     #cached data not available, fetch from server
    #     from PGMedrXivScraper import MedrXivScraper
    #     scraper = MedrXivScraper()
    #     news = scraper.fetch_latest_publications()
    #     with open('news_data.json', 'w') as file:
    #         json.dump(news, file)
    news_panel = NewsPanel()
    news_column = pn.Column(news_panel)
    #news_panel.servable()
    pn.serve(news_column)
