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

from llama_index.vector_stores.postgres import PGVectorStore

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
    def __init__(self, 
                 EMBEDDING_MODEL="BAAI/bge-m3",
                 #EMBEDDING_MODEL="mixedbread-ai/mxbai-embed-large-v1",
                 #EMBEDDING_MODEL="snowflake/snowflake-arctic-embed-l",
                 EMBEDDING_DIMENSIONS=1024,
                 LLM_NAME=LOCAL_DEFAULT_MODEL,
                 callback=None  #callback function to call when the user needs to be infromed of progress / action
                ):
        #activate basic logging to terminal
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        self._logger = logging.getLogger(__name__)
        self.db = PublicationStorage() # our postgresql connection
        self.llamaindex_settings = Settings
        self.llm = LiteLLM(llm_name=LLM_NAME, api_key=LOCAL_LLM_API_KEY, api_base=LOCAL_LLM_API_BASE)
        self.EMBEDDING_MODEL = EMBEDDING_MODEL
        self.EMBEDDING_DIMENSIONS = EMBEDDING_DIMENSIONS
        self.hybrid_index = None
        self.callback=callback
        self.last_ingested = None #the most recent document ingested into the index

        #set up our embedding model. It will be downloaded into a local cache directory 
		#if it doesn't exist locally yet. For this, an internet connection would be required
        self._logger.info("loading the embedding model")
        self._embedding_model = HuggingFaceEmbedding(model_name=self.EMBEDDING_MODEL)
        #self._embedding_model = FastEmbedEmbedding(model_name=self.EMBEDDING_MODEL)
        self.llamaindex_settings.embed_model = self._embedding_model
        self.llamaindex_settings.chunk_size = 512  #preliminary hack - we'll change that when we use more sophisticated / semantic chunking methods
        self.llamaindex_settings.batch_size = 20  # batch_size controls how many nodes are encoded with sparse vectors at once
        self.llamaindex_settings.enable_hybrid = True  # create our vector store with hybrid indexing enabled
        self.llamaindex_settings.enable_sparse = True
        self.llamaindex_settings.llm = self.llm
        self._logger.info("setting up the vector store")
        self.initiate_hybrid_vector_store()
        self._logger.info("setting the storage context")
        #self.storage_context = StorageContext.from_defaults(vector_store=self.vector_store)
        Settings.chunk_size = 512
        self._logger.info("creating the vector index")
        self.hybrid_index = VectorStoreIndex.from_vector_store(embed_model=self._embedding_model, vector_store = self.hybrid_vector_store, storage_context=self.storage_context)


    def initiate_hybrid_vector_store(self):
        """
        Initiate the hybrid vector store. Create it if it doesn't exist yet, else load it from storage.
        """
        self.hybrid_vector_store = PGVectorStore.from_params(
            database='medai',
            host='localhost',
            password='thisismedai',
            port=5432,
            user='medai',
            table_name="RAGLibrarian",
            embed_dim=self.EMBEDDING_DIMENSIONS,
            #embed_model=self._embedding_model,
            hybrid_search=True,
            text_search_config="english",
        )

        self.storage_context = StorageContext.from_defaults(
            vector_store=self.hybrid_vector_store
        )
        #try and load the index, if it exists
        try:
            self.hybrid_index = VectorStoreIndex.from_vector_store(embed_model=self._embedding_model, vector_store = self.hybrid_vector_store, storage_context=self.storage_context)
        except Exception as e:
            self._logger.info("failed to activate hybrid index, not initialized yet?")
            self._logger.info(e)
            self.hybrid_index = None


        
    def ingest(self, pdfpath):
        """Ingest a PDF file into the RAG
        Args:
            pdfpath (str): The path to the PDF file    
        """
        if self.db.file_is_ingested(os.path.basename(pdfpath)):
            print(f"{pdfpath} has already been ingested")
            return
        if not os.path.exists(pdfpath):
            print(f"{pdfpath} does not exist")
            return
        documents = SimpleDirectoryReader(input_files=[pdfpath,]).load_data()
        print(f"Loaded {len(documents)} documents, indexing now ....")
        self.hybrid_index = VectorStoreIndex.from_documents(documents, embed_model=self._embedding_model, storage_context=self.storage_context)
        print(f"Indexing complete")
        self.last_ingested = pdfpath

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
        query_engine= self.get_query_engine(top_k=top_k, pdfpath=pdfpath)
        response = query_engine.query(question)
        return response



    def get_query_engine(self, top_k=5, pdfpath=None):
        """Get a query engine for the RAG
        Args:
            top_k (int): The number of documents to retrieve
            pdfpath (str): The path to the PDF file to filter metadata by
        Returns:
            RetrieverQueryEngine: The query engine
        """
        if self.hybrid_index is None:
            print("Index not initialized yet, loading from storage ...")
            self.hybrid_index = load_index_from_storage(self.storage_context)
        metafilters = []
        if pdfpath is not None:
            print(f"-----> METADATA FILTER FOR file_name = {os.path.basename(pdfpath)}")
            metafilters = MetadataFilters(
                filters=[
                    MetadataFilter(key="file_name", value=os.path.basename(pdfpath)),
                ],
            )
        # configure retriever
        retriever = VectorIndexRetriever(
            index=self.hybrid_index,
            similarity_top_k=top_k,
            vector_store_kwargs={"hnsw_ef_search": 300},
            filters=metafilters,
        )
        # configure response synthesizer
        response_synthesizer = get_response_synthesizer(
            response_mode="tree_summarize",
        )
        # configure query engine
        query_engine = RetrieverQueryEngine(
            retriever=retriever,
            response_synthesizer=response_synthesizer,
        )
        return query_engine
    


if __name__ == "__main__":
    pdfpath="/Users/hherb/src/github/MedAiTools/library/10.1101-2024.05.23.24307833.pdf"
    rag = RAG()
    rag.ingest(pdfpath)
    response = rag.query("How were building materials classified?")
    print(response.response.strip())