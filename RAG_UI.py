import panel as pn
from panel.chat import ChatInterface
from RAG import RAG

pn.extension('texteditor', notifications=True, loading_indicator=True, design="material")

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
    """
    A panel for displaying PDF files and querying the RAG
    """

    def __init__(self, dummypdf="pdf_sample.pdf"):       
        self.pdf=dummypdf
        self.displayed_pdf=None #the currently displayed pdf file
        self.RAG=RAG()
        self.setup_panels()

    def __panel__(self):
        return self.panel


    def setup_panels(self):
        """
        Set up the user interface panels
        """

        self.pdf_pane = pn.pane.PDF(self.pdf, start_page=1, sizing_mode='stretch_both', embed=True)
        self.file_input = pn.widgets.FileInput(accept=".pdf", sizing_mode='stretch_width')
        self.file_input.param.watch(self.update_pdf, 'value') 
        self.check_all_documents=pn.widgets.Checkbox(name="Interrogate all documents", value=False)

        self.pdf_panel=pn.Column(self.pdf_pane, pn.Row(self.file_input, self.check_all_documents), margin=10, sizing_mode='stretch_both' )
        
        self.chat_bot = pn.chat.ChatInterface(callback=self.response, 
                                 user='Me', 
                                 show_rerun=False, 
                                 show_undo=False,
                                 sizing_mode='stretch_both')

        self.chat_bot.send("Ask me anything about this paper ...", user="Assistant", respond=False)
        self.panel=pn.Row(self.pdf_panel, self.chat_bot, sizing_mode='stretch_both')



    # Define a function to update the PDF widget based on the uploaded file       
    def update_pdf(self, event):  
        """
        Update the PDF viewer with the uploaded PDF file
        Args:
            event (param.Event): The event object
        """                                                      
        if event.new:   
            print(f"PDF file name = {self.file_input.filename}")  
            filepath="./library/"+self.file_input.filename
            #"""if the file does not exist, write the uploaded file to the library folder"""
            if not os.path.exists(filepath):
                with open(filepath, "wb") as f:
                    f.write(self.file_input.value)
                    #if the file didn't exist yet, it needs to be ingested ...
                    
                    self.RAG.ingest(filepath)
            #"""set the PDF viewer to display the uploaded file""" 
            self.set_pdf(filepath)  

                

    def response(self, contents, user, instance):
        """
        Respond to the user's query
        Args:
            contents (str): The user's query
            user (str): The user's name
            instance (ChatInterface): The chat interface instance
        """
        displayed_pdf=self.displayed_pdf
        if self.check_all_documents.value:
            displayed_pdf=None
        response = self.RAG.query(contents, pdfpath=displayed_pdf)
        print(f"[{response.response}]")
        sources=""
        #print(response.source_nodes[0].id_)
        # print(response.metadata[id]['file_name'])
        # print(response.metadata[id])
        # print(response.source_nodes[0].score)
        for source in response.source_nodes:
            id= source.id_
            sources+=f"{response.metadata[id].get('file_name')}, page {response.metadata[id].get('page_label')}, score: {source.score}<br>"
        display_response = f"{response.response.strip()}<hr>Source: {sources}"
        return display_response
    
    
    def set_pdf(self,filepath):
        """
        Set the PDF file to display in the PDF viewer and ingest it into the vector database
        Args:
            pdf (str): The path to the PDF file
        """   
        self.pdf_pane.object = filepath
        if not self.has_ben_ingested(filepath):
            info= pn.state.notifications.info(f"Ingesting [{filepath}]", duration=0)
            self.RAG.ingest(filepath)
             #record ingestion, so that we do not needlessly keep ingesting the same PDF
            self.displayed_pdf=filepath
            self.remember_ingestion(filepath)
            info.destroy()

    def remember_ingestion(self,filepath):
        """
        avoid duplicate ingestion of the same PDF file
        """
        pass

    def has_ben_ingested(self,filepath):
        """
        check if the PDF file has already been ingested
    
        Returns:
            bool: True if the PDF file has already been ingested, False otherwise
        """
        return False

if __name__ == "__main__":
    panel= PDFPanel()
    panel.servable()
    #panel.set_pdf("/Users/hherb/src/github/MedAiTools/library/10.1101-2024.05.09.24307138.pdf.md")
    pn.serve(panel)