import os.path
import logging

from PersistentStorage import PublicationStorage
class RAG:
    """
    A simple implementation of the RAG (Retrieval Augmented Generation) model
    using the LLAMA indexing library. This class provides methods to ingest
    PDF files into the index and query the index with a question. The index
    is stored on disk and can be reloaded later. The class uses the Qdrant's 
    FastEmbedding  library to encode the text in the PDF files into embeddings
    that are used to index the documents. The class can be used to build a simple
    question answering system that retrieves answers from a collection of
    PDF files.
    """
    def __init__(self):     
        self.db = PublicationStorage()
        self.last_ingested=None
        

    def ingest(self, pdfpath, force=False):
        """
        Ingest a PDF file into the RAG. This wrapper function returns nothing - required for use ina UI callback
        :pdfpath (str): The path to the PDF file
        :force (bool): Whether to force re-ingestion of the file    
        """
        self.last_ingested = self.db.ingest_pdf(pdfpath, force=force)

    def set_llm(self, provider='ollama', model='phi3:14b-medium-128k-instruct-q5_K_M', temperature=0.3):
        """
        Set the LLM model to be used by the RAG
        :llm (LLM): The LLM model to use
        """
        self.db.set_LLM(provider=provider, model=model, temperature=temperature)

    def query(self, question, pdfpath=None, top_k=5):
        """Query the RAG
        Args:
            question (str): The question to ask
            pdfpath (str): The path to the PDF file to filter metadata by
            top_k (int): The number of documents to retrieve
        Returns:
            str: The response to the question
        """
        #print(f"-----> running query [{question}] with pdfpath=[{pdfpath}]")
        query_engine= self.db.get_query_engine(top_k=top_k, pdfpath=pdfpath)
        response = query_engine.query(question)
        return response

    def has_been_ingested(self, pdfpath):
        """
        Check if a PDF file has been ingested into the RAG
        :pdfpath (str): The path to the PDF file
        :return (bool): True if the file has been ingested, False otherwise
        """
        return self.db.has_been_ingested(pdfpath)

    
    


if __name__ == "__main__":
    pdfpath="/Users/hherb/src/github/MedAiTools/library/10.1101-2024.05.23.24307833.pdf"
    rag = RAG()
    rag.ingest(pdfpath)
    response = rag.query("How were building materials classified?")
    print(response.response.strip())