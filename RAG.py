import os
import os.path
from llama_index.core import (
    VectorStoreIndex,
    SimpleDirectoryReader,
    StorageContext,
    load_index_from_storage,
)

from llama_index.vector_stores.lancedb import LanceDBVectorStore


from dotenv import load_dotenv
load_dotenv()  #load the environment variables
api_key=os.getenv('OPENAI_API_KEY')


class RAG:
    def __init__(self):
        self.index=None
        self.text_store = LanceDBVectorStore(uri="lancedb", table_name="RAG_text_store")
        print(f"Using {self.text_store} as the text store")
        self.storage_context = StorageContext.from_defaults(vector_store=self.text_store)
        
        try:
            print("Loading index from storage ...")
            self.index = load_index_from_storage(self.storage_context)
            self.query_engine = self.index.as_query_engine()
        except:
            print("Index not initialized yet ...")
            


        
    def ingest(self, pdfpath):
        if not os.path.exists(pdfpath):
            print(f"{pdfpath} does not exist")
            return
        documents = SimpleDirectoryReader(input_files=[pdfpath,]).load_data()
        print(f"Loaded {len(documents)} documents, indexing now ....")
        self.index = VectorStoreIndex.from_documents(documents, storage_context=self.storage_context)
        self.query_engine = self.index.as_query_engine()
        print(f"Indexing complete")

    def query(self, question):
        if self.index is None:
            print("Index not initialized yet, loading from storage ...")
            self.index = load_index_from_storage(self.storage_context)
            self.query_engine = self.index.as_query_engine()
        response = self.query_engine.query(question)
        return str(response).strip()

if __name__ == "__main__":
    pdfpath="/Users/hherb/src/github/MedAiTools/library/10.1101-2024.05.23.24307833.pdf"
    rag = RAG()
    rag.ingest(pdfpath)
    response = rag.query("How were building materials classified?")
    print(response)