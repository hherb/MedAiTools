# This code has been released by Dr Horst Herb under the GPL 3.0 license
# contact author under hherb@aiinhealth.org if you want to collaborate or need
# a different license
# Experimental draft - not ready for production!!!
#
# this library provides a RAG (retrieval augmented generation) pipeline
# allowing to ingest and query PDF and other documents
# If run as a standalone, it provides a simple web interface to upload documents
# and to query the knowledge base
#
# TODO:
# - run qdrant as a server
# - if the collection is still empty in qdrant, create it
# - check if file paths exist, incl model

from llama_index.core import (
	SimpleDirectoryReader, 
	VectorStoreIndex,
	StorageContext,
	set_global_handler,
	ServiceContext,
)

from llama_index.core.extractors import (
	TitleExtractor,
	QuestionsAnsweredExtractor,
	SummaryExtractor,
	#EntityExtractor,
)

from llama_index.core.node_parser import TokenTextSplitter
from llama_index.core.ingestion import IngestionPipeline

#we will re-rank the retrieved documents using a llm for it
from llama_index.postprocessor.colbert_rerank import ColbertRerank

#we use Qdrant as vector database
from llama_index.vector_stores.qdrant import QdrantVectorStore
from qdrant_client import QdrantClient

# we use  one of the embedding models stored at HuggingFAce
from llama_index.embeddings.huggingface import HuggingFaceEmbedding

#from llama_index.llms.ollama import Ollama #we need a ollama server running for this

#our local LLM engine - one could use eg Ollama instead, but llamacpp performs very well on Apple metal too
from llama_index.llms.llama_cpp import LlamaCPP 




class RAGLibrarian:

	def __init__(self, llm_path= """./Hermes-2-Pro-Mistral-7B.Q8_0.gguf""",
		embedding_model_name = "BAAI/bge-m3", # consider mxbai-embed-large-v1
		
		vectordb_path = "./vectors.qdrant", 
		vectordb_collection="stuff", 
		similarity_top_k=10,
		evaluating=True):		
		"""
		This class allows to ingest documents into a embedding vector database
		and retrieve data from it, providing context for inference with  a LLM
		The vectors have persistent storage in a Qdrant vector database
		
		:param llm_path: path of a LLM compatible with LlamaCPP, usually a .gguf file
		:param embedding_model_name: the HuggingFace model used for our embeddings
		:param vectordb_path: our persistent storage path for the Qdrant vector database
		:param vectordb_collection: the name of the Qdrant collection used for our instance
		:param similarity_to_k: the max number of index query returns (the top_k highest scoring)
		
		"""
		
		self._llm_path = llm_path
		self._embedding_model_name = embedding_model_name
		self._vectordb_path = vectordb_path
		self._vectordb_collection= vectordb_collection
		self._evaluating  = evaluating
		self._similarity_top_k = similarity_top_k
		
		#set up pur vector persistance database
		print("setting up the qdrant vector store")
		self._dbclient = QdrantClient(path=self._vectordb_path)
		self._vector_store = QdrantVectorStore(client=self._dbclient, collection_name=self._vectordb_collection)
		self._storage_context = StorageContext.from_defaults(vector_store=self._vector_store)
		
		#set up our embedding model. It will be downloaded into a local cache directory 
		#if it doesn't exist locally yet. For this, an internet connection would be required
		print("loading the embedding model")
		self._embedding_model = HuggingFaceEmbedding(model_name=self._embedding_model_name)
		
		#get the RAG system up and running
		print("loading the LLM...")
		#llama = Ollama(model="nous-hermes2:10.7b-solar-q5_0", request_timeout=100.0,)
		print(self._llm_path)
		self._llm = LlamaCPP(
			#model_url=model_url,
			model_path = self._llm_path,
			#model_path="./Hermes-2-Pro-Mistral-7B.Q8_0.gguf",
			temperature=0.1,
			max_new_tokens=1024,
			context_window=10000,
			generate_kwargs={},
			model_kwargs={"n_gpu_layers": -1},  # if compiled to use GPU
			#messages_to_prompt= self._messages_to_prompt,
			#completion_to_prompt= self._completion_to_prompt,
			verbose=True,
		)
		
		
		colbert_reranker = ColbertRerank(
			top_n=5,
			model="colbert-ir/colbertv2.0",
			tokenizer="colbert-ir/colbertv2.0",
			keep_retrieval_score=True,
		)
		
		print("loading index from qdrant")
		self._index = VectorStoreIndex.from_vector_store(embed_model=self._embedding_model, vector_store = self._vector_store)
		
		print("starting query engine...")
		self._query_engine = self._index.as_query_engine(llm=self._llm, similarity_top_k = self._similarity_top_k, node_postprocessors=[colbert_reranker],)
						
		if self._evaluating:
			self.set_evaluation_on()
		
	##########################################################################################
 	
	def set_evaluation_on(self):
		
		#our debugger / evaluator of the LLM / RAG pipeline
		import phoenix as px
		from phoenix.evals import (
			HallucinationEvaluator,
			OpenAIModel,
			QAEvaluator,
			RelevanceEvaluator,
			run_evals,
		)
		from phoenix.session.evaluation import get_qa_with_reference, get_retrieved_documents
		from phoenix.trace import DocumentEvaluations, SpanEvaluations
		
		# To view traces in Phoenix, you will first have to start a Phoenix server. You can do this by running the following:
		session = px.launch_app()

		# Once you have started a Phoenix server, you can start your LlamaIndex application and configure it to send traces to Phoenix. To do this, you will have to add configure Phoenix as the global handler
		set_global_handler("arize_phoenix")
		
		#launch our evaluator / LLM debugger
		px.active_session().url
		
		#feed our evaluator/debugger:
		queries_df = get_qa_with_reference(px.Client())
		retrieved_documents_df = get_retrieved_documents(px.Client())
		
	##########################################################################################
 
	def count_files(self, path, extension=".pdf"):
		"""
		Counts the number of PDF files in a given directory.
		
		Args:
			directory (str): The path to the directory to search.
			
		Returns:
			int: The number of PDF files found.
		"""
		file_count = 0
		for filename in os.listdir(path):
			if filename.endswith(extension):
				file_count += 1
		return file_count
	
	##########################################################################################
 	
	def load_documents(self, input_dir="./data"):
		"""Loads documents in PDF format from the path 'input_dir''
		   recursively and returns a list of pdf file paths"""	
		
		nfiles= count_files(input_dir)
		if nfiles<1:
			return []
		print(f"INFO: loading {nfiles} pdf documents to be processed...")  
			
		filename_fn = lambda filename: {"file_name": filename}	#add the file name to the meta data
		loader = SimpleDirectoryReader(
			input_dir=input_dir,
			recursive=True,
			required_exts=[".pdf"],
			#file_metadata=filename_fn
		)
		print("reading the documents ...")
		
		documents = loader.load_data()
		#documents is a list of dictionaries including document metadata and extracted plain text
		return documents
		
	##########################################################################################
 		
	def ingest_documents(self, document_path):
		documents=self._load_documents(document_path)
		if documents and len(documents)>0:
			index_documents(documents)
		
	##########################################################################################
 
	def index_documents(self, documents=None):
		"""indexes pdf files and other documents (see llama_index documentation re formats)
		using the specified embedding model, and stores them in the specified storage context"""	
		
		#index the documents in the list of documents
		if documents is None:
			documents=load_documents()
		if not documents or len(documents)<1:	
			print("no documents found to index")
			return
			
		index = VectorStoreIndex.from_documents(
			documents,
			embed_model=embedding_model,
			storage_context=storage_context,
			embeddings_kernel_kwargs={
				#embeddings_kernel_fn: "custom",
				embeddings_kernel_kwargs: {"progress_bar": tqdm}
			},
		)	
		
	##########################################################################################
 		
	def run_query(self, message, history=[], doc=None):
		query = message
		print(query)
		if len(query)<1:
			return("")
		answer=str(self._query_engine.query(query))
		return(answer)
		
##########################################################################################		
		
if __name__ == "__main__":
	import gradio as gr	 #our web based user interface
	from gradio_pdf import PDF as PDFwidget

	librarian = RAGLibrarian()
	pdf = PDFwidget(label="Upload a PDF", interactive=True, )
	iface = gr.ChatInterface(fn=librarian.run_query, title="Horst's RAG Librarian", additional_inputs=[pdf],analytics_enabled=False)	
	#run the user interface loop
	iface.launch()

