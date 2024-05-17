import panel as pn
from panel.chat import ChatInterface

from MedrXivPanel import MedrXivPanel

def echofunc(contents, user, instance):
    return(f"Contents: {contents}")

pn.extension('texteditor','terminal', loading_indicator=True, design="material")

pdf_pane = pn.pane.PDF("pdf_sample.pdf", sizing_mode='stretch_both', embed=True)
file_input = pn.widgets.FileInput(accept=".pdf", sizing_mode='stretch_width')
#file_input.param.watch(update_pdf, 'value') 

pdf_panel=pn.Column(pdf_pane, file_input,sizing_mode='stretch_both' )
summary_panel = pn.pane.HTML("<html>PDF summary</html>", sizing_mode='stretch_both')
critique_panel = pn.pane.HTML("<html>Critique of study:</html>", sizing_mode='stretch_both')

chat_panel = ChatInterface(callback=echofunc,
    widgets=pn.widgets.TextAreaInput(
        placeholder="Enter some text to start the chat!", auto_grow=True, max_rows=3
    ),
    show_rerun=False, show_undo=False
)

medrxiv_panel = MedrXivPanel()

notebook = pn.Tabs(('MedrXiv News', medrxiv_panel), 
                   ('Chat', chat_panel), 
                   ('Summary', summary_panel), 
                   ('Critique', critique_panel), 
                   margin=20, sizing_mode='stretch_both')

settings = pn.widgets.TextInput(name='Settings')
search = pn.widgets.TextInput(name='Search')
summaries = pn.Row(pdf_panel, notebook)

# Create the accordion
accordion = pn.Accordion(('Settings', settings), ('Search', search),width=350, sizing_mode='stretch_height', active=[0])  
#panel=pn.Row(pdf_panel, notebook)
interactive_row= pn.Row(accordion, notebook, sizing_mode='stretch_both',)
panel= pn.Column('# My Research Assistant', interactive_row, sizing_mode='stretch_both',)
panel.servable()
