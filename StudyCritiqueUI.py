import StudyCritique as sc
import panel as pn
from panel.chat import ChatInterface

pn.extension('texteditor','terminal', loading_indicator=True)


def echofunc(contents, user, instance):
    return(f"Contents: {contents}")

class InterrogateUI():
    def __init__(self):
        self.setup_panels()

    def update_pdf(self, event):
        if event.new:    
            #pdf_pane.object = file_input.value #event.new                                                       
            print(f"PDF file name = {self.file_input.filename}")  
            filepath="./library/"+self.file_input.filename
            with open(filepath, "wb") as f:
                f.write(self.file_input.value)   
            self.pdf_pane.object = filepath
            #pdf_pane.object = event.new                                                       
            study_critique = sc.StudyCritique()
            text = study_critique.pdf2document(filepath)
            summary=study_critique.summary(text)
            critique=study_critique.critique(text)
            print(summary)
            print(critique)
            #pdf_pane.object = event.new 
            self.summary_panel.object=f"<html>{summary}</html>"
            self.critique_panel.object=f"<html>{critique}</html>"

    def setup_panels(self):
        self.pdf_pane = pn.pane.PDF("pdf_sample.pdf", sizing_mode='stretch_both', embed=True)
        self.file_input = pn.widgets.FileInput(accept=".pdf", sizing_mode='stretch_width')
        self.file_input.param.watch(self.update_pdf, 'value') 

        self.pdf_panel=pn.Column(self.pdf_pane, self.file_input, margin=10, sizing_mode='stretch_both' )

        self.summary_panel = pn.pane.HTML("<html>PDF summary</html>", sizing_mode='stretch_both')

        self.critique_panel = pn.pane.HTML("<html>Critique of study:</html>", sizing_mode='stretch_both')

        self.chat_panel = ChatInterface(callback=echofunc,
                widgets=pn.widgets.TextAreaInput(
                placeholder="Interrogate the document ...", auto_grow=True, max_rows=3
            ),
            show_rerun=False, show_undo=False, sizing_mode='stretch_both')

        self.notebook = pn.Tabs(('Summary', self.summary_panel), 
                                ('Critique', self.critique_panel), 
                                ('Interrogate', self.chat_panel), 
                                margin=10, sizing_mode='stretch_both')

        self.librarian_panel = pn.Row(self.pdf_panel, self.notebook, margin = 10, sizing_mode='stretch_both' )

    def get_panel(self):
        return self.librarian_panel


if __name__ == "__main__":
    UI = InterrogateUI()
    panel= UI.get_panel()
    panel.servable()
    pn.serve(panel)