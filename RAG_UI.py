import panel as pn
from panel.chat import ChatInterface
from RAG import RAG

# FAILED="""The study discussed in the provided context focuses on mapping the sub-national spatial variation in housing materials across low- and middle-income countries. It does not mention genetic subtypes in Alzheimer's disease."""

# class RAG:
#     def __init__(self):
#         pass

#     def ingest(self,filepath):
#         print(f"RAG ingesting {filepath}")
    
#     def query(self,contents):
#         print(f"RAG querying {contents}")
#         return FAILED
    
#     def get_response(self,contents):
#         return self.query(contents)

# pn.extension('perspective', loading_indicator=True, design="material") 


class PDFPanel(pn.viewable.Viewer):

    def __init__(self, dummypdf="pdf_sample.pdf"):       
        self.pdf=dummypdf
        self.RAG=RAG()
        self.setup_panels()

    def __panel__(self):
        return self.panel


    def setup_panels(self):
        self.pdf_pane = pn.pane.PDF(self.pdf, start_page=1, sizing_mode='stretch_both', embed=True)
        self.file_input = pn.widgets.FileInput(accept=".pdf", sizing_mode='stretch_width')
        self.file_input.param.watch(self.update_pdf, 'value') 

        self.pdf_panel=pn.Column(self.pdf_pane, self.file_input, margin=10, sizing_mode='stretch_both' )
        
        self.chat_bot = pn.chat.ChatInterface(callback=self.response, 
                                 user='Me', 
                                 show_rerun=False, 
                                 show_undo=False,
                                 sizing_mode='stretch_both')

        self.chat_bot.send("Ask me anything about this paper ...", user="Assistant", respond=False)
        self.panel=pn.Row(self.pdf_panel, self.chat_bot, sizing_mode='stretch_both')



    # Define a function to update the PDF widget based on the uploaded file       
    def update_pdf(self, event):                                                        
        if event.new:   
            print(f"PDF file name = {self.file_input.filename}")  
            filepath="./library/"+self.file_input.filename
            with open(filepath, "wb") as f:
                f.write(self.file_input.value) 
                self.set_pdf(filepath)                                                       
                

    def response(self, contents, user, instance):
      response = self.RAG.query(contents)
      print(f"[{response}]")
      return str(response).strip()
    
    def set_pdf(self,filepath):
        """
        Set the PDF file to display in the PDF viewer and ingest it into the vector database
        Args:
            pdf (str): The path to the PDF file
        """   
        self.pdf_pane.object = filepath
        info= pn.state.notifications.info(f"Ingesting [{filepath}]", duration=0)
        self.RAG.ingest(filepath)
        info.destroy()

if __name__ == "__main__":
    panel= PDFPanel()
    panel.servable()
    #panel.set_pdf("/Users/hherb/src/github/MedAiTools/library/10.1101-2024.05.09.24307138.pdf.md")
    pn.serve(panel)