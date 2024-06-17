import os
import os.path
import logging

from llama_index.core import (
    Settings,
    VectorStoreIndex,
    SimpleDirectoryReader,
    StorageContext,
    load_index_from_storage,
)

from llama_index.core import VectorStoreIndex, get_response_synthesizer
from llama_index.core.retrievers import VectorIndexRetriever
from llama_index.core.query_engine import RetrieverQueryEngine

from llama_index.core.vector_stores.types import (
    MetadataFilter,
    MetadataFilters,
)

# we use  one of the embedding models stored at HuggingFAce
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
#from llama_index.embeddings.fastembed import FastEmbedEmbedding
from llama_index.llms.litellm import LiteLLM
from medai.LLM import LOCAL_DEFAULT_MODEL, LOCAL_LLM_API_KEY, LOCAL_LLM_API_BASE



from PersistentStorage import PublicationStorage, VectorStorage
import PDFParser

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
        self.vdb = VectorStorage()


    def ingest(self, pdfpath, force=False):
        """
        Ingest a PDF file into the RAG. This wrapper function returns nothing - required for use ina UI callback
        :pdfpath (str): The path to the PDF file
        :force (bool): Whether to force re-ingestion of the file    
        """
        self.last_ingested = self.vdb.ingest(pdfpath, force=force)


    def query(self, question, pdfpath=None, top_k=5):
        """Query the RAG
        Args:
            question (str): The question to ask
            pdfpath (str): The path to the PDF file to filter metadata by
            top_k (int): The number of documents to retrieve
        Returns:
            str: The response to the question
        """
        print(f"-----> running query [{question}] with pdfpath=[{pdfpath}]")
        query_engine= self.vdb.get_query_engine(top_k=top_k, pdfpath=pdfpath)
        response = query_engine.query(question)
        return response



    
    


if __name__ == "__main__":
    pdfpath="/Users/hherb/src/github/MedAiTools/library/10.1101-2024.05.23.24307833.pdf"
    rag = RAG()
    rag.ingest(pdfpath)
    response = rag.query("How were building materials classified?")
    print(response.response.strip())