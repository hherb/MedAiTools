import panel as pn
from panel.chat import ChatInterface
from RAG import RAG
import os, os.path
from functools import partial
from EventDispatcher import EventDispatcher
from medai.Settings import Logger

logger = Logger()

pn.extension('texteditor', notifications=True, loading_indicator=True, design="material")

class PDFPanel(pn.viewable.Viewer):
    """
    A panel for displaying PDF files and querying the RAG
    """

    def __init__(self, dummypdf="pdf_sample.pdf"):       
        self.pdf=dummypdf
        self.displayed_pdf=None #the currently displayed pdf file
        self.RAG=RAG()
        self.setup_panels()
        #our global event handling system - we use it to communicate events between modules
        print("creating PDFPanel & registering event dispatcher)")
        self.eventdispatcher = EventDispatcher()
        self.eventdispatcher.register_listener("LLM_MODEL_CHANGED", self.on_llm_model_changed)

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

        self.pdf_panel=pn.Column(self.pdf_pane, pn.Row(self.file_input, self.check_all_documents), margin=10, sizing_mode='stretch_both')
        
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
                    #self.RAG.ingest(filepath)
            #"""set the PDF viewer to display the uploaded file""" 
            self.set_pdf(filepath)  

    def on_llm_model_changed(self, event, *args, **kwargs):
        print(f"LLM model for RAG system changed to: {event['settings']}")
        model=event['settings']['models']
        temperature=event['settings']['temperature']
        self.set_LLM(provider=event['settings']['provider'], model=model, temperature=temperature)
        self.chat_bot.send(f"I am going to answer your questions using LLM {model} with temperature={temperature}", user="Assistant", respond=False)

    def set_LLM(self, provider='ollama', model='phi3:14b-medium-128k-instruct-q5_K_M', temperature=0.3):
        """
        Set the LLM model to be used by the RAG
        Args:
            provider (str): The provider of the LLM model
            model (str): The model to use
            temperature (float): The temperature to use
        """
        self.RAG.set_llm(provider=provider, model=model, temperature=temperature)

    def response(self, contents, user, instance):
        """
        Respond to the user's query
        Args:
            contents (str): The user's query
            user (str): The user's name
            instance (ChatInterface): The chat interface instance
        """
        print(f"displayed_pdf: {self.displayed_pdf}")
        displayed_pdf=self.displayed_pdf
        if self.check_all_documents.value:
            print("No metadata filter applied")
            displayed_pdf=None
        else:
            print(f"Metadata filter applied: {displayed_pdf}")
        response = self.RAG.query(contents, pdfpath=displayed_pdf)
        print(f"[{response.response}]")
        sources=""
        #print(response.source_nodes[0].id_)
        # print(response.metadata[id]['file_name'])
        # print(response.metadata[id])
        # print(response.source_nodes[0].score)
        for source in response.source_nodes:
            id= source.id_
            sources+=f"{response.metadata[id].get('filename')}, page {response.metadata[id].get('page')}, score: {source.score}<br>"
        display_response = f"{response.response.strip()}<hr>Source: {sources}"
        return display_response
    
    
    def set_pdf(self,filepath):
        """
        Set the PDF file to display in the PDF viewer and ingest it into the vector database
        Args:
            pdf (str): The path to the PDF file
        """   
        absfilepath = os.path.abspath(filepath)
        if not os.path.exists(absfilepath):
            print(f"File {absfilepath} does not exist")
            self.chat_bot.send("Unfortunately, the file {absfilepath} seems to have been deleted - I can't find it!", user="Assistant", respond=False)
            return
        print(f"Setting PDF file to {absfilepath}")
        self.pdf_pane.object = absfilepath
        if not self.RAG.has_been_ingested(absfilepath):
            info= pn.state.notifications.info(f"Ingesting [{absfilepath}]", duration=0)
            self.RAG.ingest(absfilepath)
            self.displayed_pdf=absfilepath
            info.destroy()
        else:
            self.displayed_pdf=absfilepath

if __name__ == "__main__":
    panel= PDFPanel()
    panel.servable()
    panel.set_pdf('/Users/hherb/medai/library/10.1101-2024.06.21.24309328.pdf')
    pn.serve(panel)