
# Copyright (C) 2024  Dr Horst Herb
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
# This module provides abstracted Postgresql database backend connections
# for the MedAiTools project

import os
import dotenv
import logging
import sys
import time
from tqdm import tqdm
from pprint import pprint
from psycopg_pool import ConnectionPool
from psycopg import sql, errors
from psycopg.rows import dict_row

from llama_index.core import (
    Settings,
    VectorStoreIndex,
    SimpleDirectoryReader,
    StorageContext,
    load_index_from_storage,
)

from llama_index.core import VectorStoreIndex
from llama_index.vector_stores.postgres import PGVectorStore

import PDFParser
from medai.Settings import Settings as MedAISettings

s = MedAISettings()

#hack, so that we don't have to explicity import dict_row from psycopg in the calling module (in case our abstraction changes away from psycopg)
dict_row=dict_row

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
    

class PersistentStorage:
    """Base class for a PostgreSQL connection pool"""

    def __init__(self,  
                 storage_directory=s.STORAGE.PUBLICATION_DIR, #this is where we store blobs, eg PDF files
                 server_url=None, #the connection string to log into our postgresql server (DBAPI 2 compliant)
                 min_size= 1, max_size=8, #size of our connection pool
                 schema_migration_file=None, #if stated, this file will be used to migrate the database schema
                 ):
        """
        Abstracts PostgreSQL interactions, maintains a connectio to the PostgreSQL server
        and provides often used functionality in simple class methods.
        Requires server connection parameters as via our configuration file
        but is overriden by environment variables (fetches them from from .env if exists)
        
        :param storage_directory: str, the directory to store static files
        :param server_url: str, the connection URL to the PostgreSQL server
        :param min_size: int, the minimum number of connections in the connection pool
        :param max_size: int, the maximum number of connections in the connection pool
        :param schema_migration_file: str, the path to the SQL file containing the schema migration
        """ 
        #set the storage directory for static files
        self.storage_directory=storage_directory
        #check whether this directory exists, else create it
        if not os.path.exists(self.storage_directory):
            os.makedirs(self.storage_directory)
        #get our login parameters from the environment variables
        dotenv.load_dotenv()
        self.url=server_url or self.connection_url()
        # Connect to the PostgreSQL database
        logger.info("Initiating PostgreSQLconnection pool ...")
        self.connection_pool = None
        self.initiate_connection_pool(min_size=min_size, max_size=max_size)
        logger.info("PostgreSQL connection pool ready.")
        if schema_migration_file:
            self.migrate_schema(schema_migration_file)

        
    def migrate_schema(self, schema_migration_file : str ):
        """
        Migrate the database schema using a SQL file.
        :param schema_migration_file: str, the path to the SQL file containing the schema migration
        TODO: ERROR HANDLING
        """
        with open(schema_migration_file) as f:
            schema = f.read()
        with self.connection() as conn:
            conn.execute(schema)
        logger.info("Database schema migrated successfully.")

    def connection_url(self, 
                       host : str = s.STORAGE.HOST,  
                       port : int = s.STORAGE.PORT, 
                       dbname : str =s.STORAGE.DBNAME, 
                       user : str = s.DBUSER, 
                       password : str = s.DBPASS) -> str:
        """
        Create a connection URL to the PostgreSQL server.
        It will always prioritize settings from environment variables over the default values,
        since it is good practice to use environment variables for sensitive information.
        
        :param host: str, the hostname of the PostgreSQL server
        :param port: int, the port number of the PostgreSQL server
        :param dbname: str, the name of the database to connect to
        :param user: str, the username to connect with
        :param password: str, the password to connect with
        :return: str, the connection URL to the PostgreSQL server
        """
        host,=os.getenv('PG_HOST') or host,
        port,=os.getenv('PG_PORT') or port,
        dbname,=os.getenv('PG_DBNAME') or dbname,
        user,=os.getenv('PG_USER') or user,
        password,=os.getenv('PG_PASSWORD') or password,
        url=f"""host={host} port={port} user={user} password={password} dbname={dbname} connect_timeout=10"""
        logger.debug(f"Connecting to PostgreSQL server with [{url}]")
        return url

    def initiate_connection_pool(self, retries=5, min_size=1, max_size=8):
        """Initiate a connection pool to the PostgreSQL server
        :param retries: int, the number of retries to attempt
        """
        
        for i in range(retries):
            try:
                self.connection_pool = ConnectionPool(conninfo=self.url, min_size=min_size, max_size=max_size)
                self.connection_pool.wait() #wait for the pool to be ready
                logger.info("PostgreSQL connection pool ready.")
                return
            except errors.ConnectionFailure as e:
                logger.error(f"Could not connect to the PostgreSQL server. Retrying ... (error: {e})")
                time.sleep(5)
        logger.error(f"Could not connect to the PostgreSQL server after [{retries}] retries. Exiting ...")
        sys.exit(1)

    def connection(self):
        """Get a database connection from the pool."""
        return self.connection_pool.connection()
            
    def release_connection(self, conn):
        """Release a connection back to the pool."""
        self.connection_pool.putconn(conn)

    def close_all_connections(self):
        """Close all connections in the pool."""
        logger.info("Closing all connections in the PostgreSQL connection pool.")
        try:
            self.connection_pool.close()
        except Exception as e:
            logger.error(f"Could not close all connections in the PostgreSQL connection pool. Error: {e}")

    def __del__(self):
        self.close_all_connections()

    
class VectorStorage(PersistentStorage):
    """
    A LlamaIndex vector store & indexing system using PostgreSQL as backend
    """

    def __init__(self, 
                 storage_directory=s.STORAGE.PUBLICATION_DIR, #this is where we store blobs, eg PDF files
                 server_url=None, #the connection string to log into our postgresql server (DBAPI 2 compliant)
                 min_size= 1, max_size=10, #size of our connection pool
                 schema_migration_file=None #if stated, this file will be used to migrate the database schema
                 ):
        super().__init__(storage_directory=storage_directory, server_url=server_url, min_size=min_size, max_size=max_size, schema_migration_file=schema_migration_file)
        self.vector_store = None
        self.storage_context = None
        self.initiate_vector_store()
    

    def initiate_hybrid_vector_store(self):
        """
        Initiate the hybrid vector store. Create it if it doesn't exist yet, else load it from storage.
        """
        self.llamaindex_settings = Settings
        self.llm = LLM.get_local_32k_model()
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
    
        Settings.chunk_size = 512
        self._logger.info("preparing the vector index")
        self.hybrid_index = VectorStoreIndex.from_vector_store(embed_model=self._embedding_model, vector_store = self.hybrid_vector_store, storage_context=self.storage_context)
        self.hybrid_vector_store = PGVectorStore.from_params(
            database='medai',
            host='localhost',
            password='thisismedai',
            port=5432,
            user='medai',
            table_name="RAGLibrarian",
            embed_dim=self.EMBEDDING_DIMENSIONS,
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


    def _ingest(self, pdfpath, force=False) -> str:
        """
        Ingest a PDF file into the hydrid store
        :pdfpath (str): The path to the PDF file
        :force (bool): Whether to force re-ingestion of the file
        :return: str, the path to the ingested file
        """
        if self.db.file_is_ingested(os.path.basename(pdfpath)) and not force:
            print(f"{pdfpath} has already been ingested")
            return(pdfpath)
        if not os.path.exists(pdfpath):
            print(f"{pdfpath} does not exist")
            return('')
        self._logger.info(f"ingesting {pdfpath}") 
        documents=PDFParser.pdf2llama(pdfpath)
        self._logger.info(f"Loaded {len(documents)} nodes from {pdfpath}, indexing now ....")
        self.hybrid_index = VectorStoreIndex.from_documents(documents, embed_model=self._embedding_model, storage_context=self.storage_context)
        self._logger.info(f"Indexing of {pdfpath} complete") 
        return(pdfpath)

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


    
class PublicationStorage(PersistentStorage):
    """
    A persistent storage backend for MedrXiv publications
    """
    def __init__(self,  
                 storage_directory=s.STORAGE.PUBLICATION_DIR, #this is where we store blobs, eg PDF files
                 server_url=None, #the connection string to log into our postgresql server (DBAPI 2 compliant)
                 min_size= 1, max_size=10, #size of our connection pool
                 schema_migration_file=None #if stated, this file will be used to migrate the database schema
                 ):
        """
        Abstracts PostgreSQL interactions, maintains a connection to the PostgreSQL server
        and provides often used functionality in simple class methods.
        Requires server connection paarmeters as enironment variables (fetches them from from .env if exists)
        :param storage_directory: str, the directory to store static files
        :param server_url: str, the connection URL to the PostgreSQL server
        :param min_size: int, the minimum number of connections in the connection pool
        :param max_size: int, the maximum number of connections in the connection pool
        :param schema_migration_file: str, the path to the SQL file containing the schema migration
        """ 
        super().__init__(storage_directory=storage_directory, server_url=server_url, min_size=min_size, max_size=max_size, schema_migration_file=schema_migration_file)


    def count(self, whereclause=None):
        """
        Get the number of publications stored in the database
        :return: int, the number of publications stored in the database
        """
        query = "SELECT COUNT(*) FROM medrxiv;"
        if whereclause:
            query = f"{query} {whereclause}"
        with self.connection() as conn:
            cursor = conn.execute(query)
            result = cursor.fetchone()
        return result[0]


    def file_is_ingested(self, filename):
        """
        Check if a file has been ingested before by checking the vector database metadata for the filename (with path stripped off)
        :param filename: str, the filename to check
        :return: bool, True if the file has been ingested, False otherwise
        """
        with self.connection() as conn:
            querytemplate = """select EXISTS(select 1 from data_raglibrarian where metadata_ ->> 'file_name' = {filename})"""
            query = sql.SQL(querytemplate).format(filename=sql.Literal(filename))
            cursor = conn.execute(query)
            result = cursor.fetchone()
        return result[0]
    

    def latest_stored(self, from_which_server : str = "medrxiv") -> str:
        """
        Get the latest date of the publication stored in the database
        :param from_which_server: str, the server to check
        :return: str, the latest date of the publications stored in the database as 'yyyy-mm-dd'
        """
        query =f"SELECT MAX(TO_DATE(date, 'YYYY-MM-DD')) FROM medrxiv WHERE SERVER = '{from_which_server}';"
        with self.connection() as conn:
            cursor=conn.execute(query)
            result = cursor.fetchone()
        return result[0]


    def upsert(self, publication: dict) -> int:
        """returns the id of the publication or None if the publication could not be saved
           duplications are handled as upserts (existing publication gets updated if different)
        :param publication: dict with the publication data
        :return: int (upserted record id)  or None
        """
        columns = publication.keys()
        values = [publication[column] for column in columns]
        # Sanitize column names
        #sanitized_columns = [sql.Identifier(col) for col in columns]
        #sanitized_values = [sql.Literal(value) for value in values] 
        query = f"""
        INSERT INTO medrxiv ({', '.join(columns)})
        VALUES ({', '.join(['%s'] * len(values))})
        ON CONFLICT (doi, version)
        DO UPDATE SET
            title = EXCLUDED.title,
            authors = EXCLUDED.authors,
            author_corresponding = EXCLUDED.author_corresponding,
            author_corresponding_institution = EXCLUDED.author_corresponding_institution,
            date = EXCLUDED.date,
            type = EXCLUDED.type,
            license = EXCLUDED.license,
            category = EXCLUDED.category,
            jatsxml = EXCLUDED.jatsxml,
            abstract = EXCLUDED.abstract,
            published = EXCLUDED.published,
            server = EXCLUDED.server
        RETURNING id;
        """
        # Execute the query
        with self.connection() as conn:

            with conn.cursor(row_factory=dict_row) as cursor:
                cursor.execute(query, values)
                upserted_id = cursor.fetchone()['id']
                # No explicit commit needed if using 'with' context for the cursor in psycopg 3
                return upserted_id
    

    def bulk_upsert(self, publications: list) -> list:
        """Bulk upsert a list of publications.
        :param publications: list of dicts with the publication data
        :return: list of upserted record ids
        """
        # Assuming all publications have the same columns
        if not publications:
            return []

        columns = publications[0].keys()
        values_placeholder = ", ".join([f"(%s)" for _ in publications])
        values = [value for publication in publications for value in publication.values()]
        on_conflict_set = ", ".join([f"{column}=EXCLUDED.{column}" for column in columns if column not in ('doi', 'version')])

        query = f"""
        INSERT INTO medrxiv ({', '.join(columns)})
        VALUES {values_placeholder}
        ON CONFLICT (doi, version) DO UPDATE SET {on_conflict_set}
        RETURNING id;
        """

        with self.connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, values)
            upserted_ids = cursor.fetchall()
            return [upserted_id[0] for upserted_id in upserted_ids]


    def fetch(self, publication_id: int) -> dict:
        """fetch one publication by id from the database
        :param publication_id: str, the publication id
        :return: dict, the publication data
        """
        query = sql.SQL("SELECT * FROM medrxiv WHERE id = {publication_id}").format(publication_id=sql.Literal(publication_id))
        with self.connection() as conn:
            # Use a cursor with DictCursor to fetch rows as dictionaries
            with conn.cursor(row_factory=dict_row) as cursor:
                cursor.execute(query)
                publication = cursor.fetchone()
                if publication:
                    return dict(publication)  # Convert DictRow to a standard dict if needed
                return None
            

    def list_newest_versions(self):
        """Get the newest versions of the publications (if there are versions higher than 1)
        :param limit: int, the number of publications to return
        :return: iterator of dicts, each dict containing the newest revisionfor the doi
        """
        query = sql.SQL("""
        WITH LatestVersion AS (
            SELECT 
                MAX(version) AS version, doi
            FROM
                medrxiv
            GROUP BY
                doi
        ),
        LatestMedrxiv AS (
            SELECT
                m.*
            FROM
                medrxiv m
            INNER JOIN LatestVersion lv ON m.doi = lv.doi AND m.version = lv.version
        )
        SELECT
            lm.*,
            s.text AS summary
        FROM
            LatestMedrxiv lm
        JOIN
            summaries s ON lm.id = s.id_publication
        """)
        with self.connection() as conn:
            with conn.cursor(row_factory=dict_row) as cursor:
                cursor.execute(query)
                for publication in cursor:
                    yield dict(publication)


    def search_for(self, keywords: list, from_date=None, to_date=None, limit=0) -> iter:
        """Search for publications with the given keywords within a specified date range.
        :param keywords: list of str, the keywords to search for
        :param from_date: str or None, the start date for filtering (inclusive)
        :param to_date: str or None, the end date for filtering (inclusive)
        :param limit: int, the maximum number of results to return
        :return: iterator of dicts, the publications found
        """
        # Prepare the keywords placeholder
        keywords_placeholder = sql.SQL(', ').join(sql.Literal("%{}%".format(k)) for k in keywords)
        # Base query with placeholders for dynamic parts
        query_template = sql.SQL("""
            SELECT
                *
            FROM
                newest_revision_with_fulltext_columns
            WHERE
                (title ILIKE ANY(ARRAY[{keywords}])
                OR abstract ILIKE ANY(ARRAY[{keywords}])
                OR summary ILIKE ANY(ARRAY[{keywords}]))
        """)
        # Replace the placeholder in the base query
        query_filled = query_template.format(keywords=keywords_placeholder)
        # Date range filtering
        date_conditions = []
        if from_date:
            date_conditions.append(sql.SQL("date >= {}").format(sql.Literal(from_date)))
        if to_date:
            date_conditions.append(sql.SQL("date <= {}").format(sql.Literal(to_date)))
        # Add date conditions to the query
        if date_conditions:
            query_filled += sql.SQL(" AND ") + sql.SQL(" AND ").join(date_conditions)
        query_filled += sql.SQL(" ORDER BY date DESC")
        # Add limit to the query
        if limit>0:
            query_filled += sql.SQL(" LIMIT {}").format(sql.Literal(limit))

        # Execute the query
        with self.connection() as conn:
            with conn.cursor(row_factory=dict_row) as cursor:
                cursor.execute(query_filled)
                for publication in cursor:
                    yield dict(publication)

    def get_pdf_path(self, publication_id: int) -> str:
        """Get the path to the PDF file of a publication
        :param publication_id: int, the publication id
        :return: str, the path to the PDF file
        """
        fname=''
        query = sql.SQL("SELECT pdf_filename FROM fulltext WHERE id_publication = {publication_id}").format(publication_id=sql.Literal(publication_id))
        with self.connection() as conn:
            cursor = conn.execute(query)
            result = cursor.fetchone()
            if result:
                fname = os.path.join(self.storage_directory, result[0])
        return fname

    def delete(self, publication_id):
        raise NotImplementedError()
    

    def save_summary_method(self, summarymethod: str) -> int:
        """if not already existing, save a summary method to the database
        :param summary_method: str, the summary method to save
        :return: int, the id of the summary method
        """
        query = sql.SQL("INSERT INTO summarymethod (name) VALUES ({method}) ON CONFLICT DO NOTHING RETURNING id;").format(method=sql.Literal(summarymethod))
        with self.connection() as conn:
            cursor=conn.execute(query)
            summary_method_id = cursor.fetchone()
            return summary_method_id
        
        
    def save_summary(self, summary: str, id_publication: int, id_summarymethod: int=1) -> int:
        """Save a summary to the database
        :param summary: str, the summary to save
        :param id_publication: int, foreign key of the publication
        :param id_summarymethod: int, foreign key of the summary method 
        :return: int, the id of the summary
        """
        query = """
        INSERT INTO summaries (text, id_publication, id_summarymethod)
        VALUES (%s, %s, %s) RETURNING id;
        """
        with self.connection() as conn:
            with conn.cursor() as cursor:
                #logger.info(f"Saving summary for publication id=[{id_publication}]")
                logger.debug(f"query=[{query}]")
                cursor.execute(query, (summary, id_publication, id_summarymethod))
                summary_id = cursor.fetchone()[0]
                conn.commit()
                return summary_id
            

    def missing_summaries(self, id_summarymethod : int =1) -> iter:
        """Get all publications that do not have a summary yet
        :return: iterator over a list of dicts, the publications without a summary
        """
        query = """
        SELECT m.* FROM medrxiv m
        LEFT JOIN summaries s ON m.id = s.id_publication AND s.id_summarymethod = %s
        WHERE s.id IS NULL;
        """
        with self.connection() as conn:
            with conn.cursor(row_factory=dict_row) as cursor:
                cursor.execute(query, (id_summarymethod,))
                rowcount=cursor.rowcount
                logger.info(f"Found [{rowcount}] publications without a summary.")
                for publication in tqdm(cursor, total=rowcount):
                    yield dict(publication)
   
    def _ingest(self, pdfpath: str):
        return(self.getRAG().ingest(pdfpath))
    
    def ingest_pdf(self, pdfpath: str, force=False):
        """Ingest a PDF file into the database
        :param pdfpath: str, the path to the PDF file
        """
        pdf_fname = os.path.basename(pdfpath)
        #don't ingest the same file twice unless specifically requested
        if self.file_is_ingested(pdf_fname):
            logger.info(f"PDF file [{pdf_fname}] has already been ingested.")
            if force:
                #TODO: remove the existing record and re-ingest
                logger.info(f"Re-ingesting PDF file [{pdf_fname}] with _ingest...")
                return self._ingest(pdfpath)
            else:
                return(pdfpath)
        logger.info(f"Re-ingesting PDF file [{pdf_fname}] with _ingest...")
        return self._ingest(pdfpath)

if __name__ == "__main__":
    from pprint import pprint
    import PGMedrXivScraper

    pg = PublicationStorage()
    assert pg.file_is_ingested("10.1101-2024.05.23.24307833.pdf"), "file_is_ingested failed"
    latest=pg.latest_stored()
    logger.info(f"Latest stored medrxiv record is [{latest}]")
    #assert str(latest).strip() == "2024-06-10", "latest_stored failed"
    #pub = pg.fetch(100)
    #assert pub['doi']=='10.1101/19001925', f"fetch failed, doi=[{pub['doi']}]"
    #pub = pg.fetch(103)
    #from PGMedrXivScraper import MedrXivScraper
    #scraper = MedrXivScraper(db=pg)
    #pprint(f"fetched pdf: {scraper.fetch_pdf_from_medrXiv(pub)}")
    #logger.info(f"""summary method saved, id=[{pg.save_summary_method("default")}]""")
    #logger.info(f"""summary saved, id=[{pg.save_summary("This is a summary", 100)}]""")

    assistant = PGMedrXivScraper.MedrXivAssistant(pg)
    print("summarizing missing publications ...")
    for publication in pg.missing_summaries():
        #logger.info(f"publication=[{publication}]")
        summary = assistant.summarize(publication)
        #logger.info(f"summary=[{summary}]")
        #pg.save_summary(summary, publication['id'])
    # news = pg.list_newest_versions()s
    # for n in news:
    #     pprint(n)

    