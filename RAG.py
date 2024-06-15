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
#from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.embeddings.fastembed import FastEmbedEmbedding
from llama_index.llms.litellm import LiteLLM
from medai.LLM import LOCAL_DEFAULT_MODEL, LOCAL_LLM_API_KEY, LOCAL_LLM_API_BASE

from llama_index.vector_stores.postgres import PGVectorStore


from llama_index.vector_stores.qdrant import QdrantVectorStore
from qdrant_client import QdrantClient, AsyncQdrantClient


#from dotenv import load_dotenv
#load_dotenv()  #load the environment variables
#api_key=os.getenv('OPENAI_API_KEY')



class RAG:

    def __init__(self, 
                 #EMBEDDING_MODEL="BAAI/bge-m3",
                 #EMBEDDING_MODEL="mixedbread-ai/mxbai-embed-large-v1",
                 EMBEDDING_MODEL="snowflake/snowflake-arctic-embed-l",
                 EMBEDDING_DIMENSIONS=1024,
                 LLM_NAME=LOCAL_DEFAULT_MODEL,
                 PERSIST_DIR="./storage",
                 callback=None  #callback function to call when the user needs to be infromed of progress / action
                ):
        #activate basic logging to terminal
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        self._logger = logging.getLogger(__name__)
        self.llamaindex_settings = Settings
        self.llm = LiteLLM(llm_name=LLM_NAME, api_key=LOCAL_LLM_API_KEY, api_base=LOCAL_LLM_API_BASE)
        self.EMBEDDING_MODEL = EMBEDDING_MODEL
        self.EMBEDDING_DIMENSIONS = EMBEDDING_DIMENSIONS
        self.PERSIST_DIR = PERSIST_DIR
        self.index = None
        self.callback=callback
        self.last_ingested = None #the most recent document ingested into the index

        if not os.path.exists(self.PERSIST_DIR):
            os.makedirs(self.PERSIST_DIR, exist_ok=True) #create the directory if it doesn't exist yet
        print(f"Using {self.PERSIST_DIR} as the storage directory")

        #set up our embedding model. It will be downloaded into a local cache directory 
		#if it doesn't exist locally yet. For this, an internet connection would be required
        self._logger.info("loading the embedding model")
        #self._embedding_model = HuggingFaceEmbedding(model_name=self.EMBEDDING_MODEL)
        self.embedding_model = FastEmbedEmbedding(model_name=self.EMBEDDING_MODEL)
        self.llamaindex_settings.embed_model = self.embedding_model
        self.llamaindex_settings.chunk_size = 512
        self.llamaindex_settings.batch_size = 20
        self.llamaindex_settings.enable_hybrid = True
        self.llamaindex_settings.enable_sparse = True
        self.llamaindex_settings.llm = self.llm
        # activates or creates a persistant index to disk
        client = QdrantClient(path=self.PERSIST_DIR)

        # create our vector store with hybrid indexing enabled
        # batch_size controls how many nodes are encoded with sparse vectors at once
        self._logger.info("setting up the vector store")
        self.vector_store = QdrantVectorStore(
            "hybrid_indexed_vector_store",
            client=client,
            enable_hybrid=True,
            batch_size=20,
            embed_model=self.embedding_model,
        )
        self._logger.info("setting the storage context")
        self.storage_context = StorageContext.from_defaults(vector_store=self.vector_store)
        Settings.chunk_size = 512
        self._logger.info("creating the vector index")
        self.index = VectorStoreIndex.from_vector_store(embed_model=self.embedding_model, vector_store = self.vector_store)
        self.hybrid_index = self.initiate_hybrid_vector_store()



    def initiate_hybrid_vector_store(self):
        """Initiate the hybrid vector store. Create it if it doesn't exist yet, else load it from storage."""
        self.hybrid_vector_store = PGVectorStore.from_params(
            database='medai',
            host='localhost',
            password='thisismedai',
            port=5432,
            user='medai',
            table_name="RAGLibrarian",
            embed_dim=self.EMBEDDING_DIMENSIONS,
            #embed_model=self.embedding_model,
            hybrid_search=True,
            text_search_config="english",
        )

        self.storage_context = StorageContext.from_defaults(
            vector_store=self.hybrid_vector_store
        )
        try:
            self.hybrid_index = VectorStoreIndex.from_vector_store(vector_store=self.hybrid_vector_store, storage_context=self.storage_context)
        except Exception as e:
            self._logger.info("failed to activate hybrid index, not initialized yet?")
        # self.hybrid_index = VectorStoreIndex.from_documents(
        #     documents, storage_context=storage_context
        # )

        
    def ingest(self, pdfpath):
        if not os.path.exists(pdfpath):
            print(f"{pdfpath} does not exist")
            return
        documents = SimpleDirectoryReader(input_files=[pdfpath,]).load_data()
        print(f"Loaded {len(documents)} documents, indexing now ....")
        self.index = VectorStoreIndex.from_documents(documents, storage_context=self.storage_context)
        print(self.index)
        #self.query_engine = self.index.as_query_engine(response_mode="tree_summarize",similarity_top_k=8)
        print(f"Indexing complete")
        self.last_ingested = pdfpath

    def query(self, question, pdfpath=None, top_k=5):
        print(f"-----> running query [{question}] with pdfpath=[{pdfpath}]")
        query_engine= self.get_query_engine(top_k=top_k, pdfpath=pdfpath)
        response = query_engine.query(question)
        return response



    def get_query_engine(self, top_k=5, pdfpath=None):
        if self.index is None:
            print("Index not initialized yet, loading from storage ...")
            self.index = load_index_from_storage(self.storage_context)
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
            index=self.index,
            similarity_top_k=top_k,
            filters=metafilters
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