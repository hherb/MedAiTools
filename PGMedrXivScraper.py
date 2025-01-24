import os, os.path
import logging
import requests
from datetime import datetime, timedelta
from tqdm import tqdm
from time import sleep
from Summarizer import Summarizer
from KeywordExtractor import KeywordExtractor
from StudyCritique import StudyCritique
from tenacity import retry, wait_random
from pprint import pprint
from medai.Settings import Settings as MedAISettings


from PersistentStorage import PublicationStorage, dict_row

s = MedAISettings()

class MedrXivScraper:
    """
    fetches publications from medrXiv and stores them in a database
    provides helper functions to access, search, and manipulate the data
    including fetchin associated full texts (e.g. pdf) from the internet
    """

    def __init__(self, db : PublicationStorage = None, callback_notification=print, tqdm=tqdm):
        """initializes the MedrXivScraper
        :param db: a PublicationStorage object from module PersistentStorage. If None, a new one is created with default settings.
        :param callback_notification: a callback function to notify the user of progress. If None, no notification is given.
            if provided, the function should take a string as an argument and display it to the user.
        :param tqdm: a tqdm object to display progress bars. If None, no progress bars are displayed.
        """
        self.tqdm=tqdm
        if db is None:
            db = PublicationStorage(tqdm=self.tqdm)
        self.db=db
        self.callback_notification = callback_notification
        self.callback_notification("MedrXivScraper initialized")


    def count(self):
        """returns the number of publications in the database"""
        return self.db.count(whereclause= "where server ILIKE 'medrXiv'")


    def split_daterange_into_days(self, start_date: str, end_date: str) ->list[str]:
        """splits a date range into individual days
        :param start_date: the start date in the format 'YYYY-MM-DD'
        :param end_date: the end date in the format 'YYYY-MM-DD'
        :return: a list of dates in the format 'YYYY-MM-DD'"""

        start_date = datetime.strptime(start_date, '%Y-%m-%d')
        end_date = datetime.strptime(end_date, '%Y-%m-%d')
        delta = end_date - start_date
        dates = []
        for i in range(delta.days + 1):
            day = start_date + timedelta(days=i)
            dates.append(day.strftime('%Y-%m-%d'))
        return dates
    

    #@retry(wait=wait_random(min=3, max=10))
    def fetch_from_medrXiv(self, from_date: str, to_date: str, fetch_pdfs=True) -> list[dict]:
        """fetches publications from the medrXiv server for a given date
        :param from_date: the start date in the format 'YYYY-MM-DD'
        :param to_date: the end date in the format 'YYYY-MM-DD'
        :return: a list of publications in the form of dictionaries
        """
        base_url = f"https://api.medrxiv.org/details/medrxiv/{from_date}/{to_date}"
        self.callback_notification(f"attempting to fetch new publications from {base_url}")

        all_publications = []   
        cursor = 0    
        while True:
            url = f"{base_url}/{cursor}/json"
            response = requests.get(url)
            if response.status_code != 200:
                self.callback_notification(f"Failed to fetch data from {url}. Status code: {response.status_code}")
                break
            data = response.json()
            publications = data.get('collection', [])
            all_publications.extend(publications)
            for publication in tqdm(publications, total=len(publications), desc="Inserting into database"):
                publication['id'] = self.db.upsert(publication)
                if fetch_pdfs:
                    self.fetch_pdf_from_medrXiv(publication, upsert=True)
                    self.callback_notification(f"inserted {len(publications)} into database including PDFs")
            # Check if more results are available
            messages = data.get('messages', [])
            pprint(messages)
            if messages:
                message = messages[0]
                total_items = message.get('total', 0)
                print(f"message={message}, total_items={total_items}")
                if cursor + len(all_publications) >= total_items:
                    break  # No more results
                cursor += len(publications)
            else:
                break  # No messages, likely no more results
        self.callback_notification(f"fetched {len(all_publications)} publications")
        
        #self.fetch_all_missing_pdfs(publications=publications)
        return all_publications


    def fetch_latest_publications(self, days:int = 0, start_date: str = None, fetch_pdfs:bool=False) -> list[dict]:
        """fetches the latest publications from medrXiv
        :param days: the number of days to fetch publications, counting backwards from today. 
            If 0, fetches all not yet ingested publications from the last day in the database 
            until today
        :return: a list of publications in the form of dictionaries for the given time span
            which is either the specified number of days until today, or from the last stored date until today
        """
        today = datetime.now().strftime('%Y-%m-%d')
        
        if days==0 and not start_date:
            start_date=self.db.latest_stored()
        elif days>0:  #we want an overlap in case we didn't fetch the full day or late submissions
            start_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
        logging.info(f"Fetching publications from {start_date} to {today}")
        if start_date != today:
            try:
                self.fetch_from_medrXiv(start_date, today, fetch_pdfs=fetch_pdfs)
            except Exception as e:
                logging.error(f"Failed to fetch publications: {e}")
        #self.update_summaries()
        return self.db.fetch_daterange(start_date, today)
    
    def update_summaries(self):
        """updates summaries for a list of publications
        :param publications: a list of publications in the form of dictionaries
        """
        assistant = MedrXivAssistant(self.db, tqdm=self.tqdm)
        for publication in self.db.missing_summaries():
            assistant.summarize(publication, commit=True)

    def get_pdf_url(self, publication : dict) -> str:
        """creates a URL for full PDF download from a retrieved publication
		
		:param publication: dictionary, see fetch_medrxiv_publications() for keys
		:return: URL for downloading a PDF
		"""
        pdf_url = f"https://www.medrxiv.org/content/{publication['doi']}.full.pdf"
        return(pdf_url)
    

    #@retry(wait=wait_random(min=5, max=15))
    def fetch_pdf_from_medrXiv(self, publication: dict, path: str = "./library", upsert=True) -> str:
        """downloads the PDF of a publication to a given path
        :param publication: a publication in the form of a dictionary
        :param path: the path to save the PDF to
        :return: the path to the saved PDF
        """
        pdf_url = self.get_pdf_url(publication)
        pdf_name = f"{publication['doi'].replace('/', '-')}.pdf"
        try:
            path = s.get('PUBLICATION_DIR', path)
        except:
            pass
        pdf_path = os.path.join(path, pdf_name)

        # Check if the PDF file already exists - only download once
        if not os.path.isfile(pdf_path):
            # Download and save the PDF if it doesn't exist
            try:
                response = requests.get(pdf_url)
                response.raise_for_status()  # Raises an HTTPError if the response was an error
                with open(pdf_path, 'wb') as f:
                    f.write(response.content)
                #self.callback_notification(f"PDF saved at {pdf_path}")
            except Exception as e:
                self.callback_notification(f"Failed to fetch PDF: {e}")
                return None
        else:
            self.callback_notification(f"PDF already exists at {pdf_path}")
            
        if upsert:
            #print(f"Upserting {pdf_name} into database")
            with self.db.connection() as conn:
                #print(f"Inserting {pdf_name} now")
                cursor=conn.execute("""
                    INSERT INTO fulltext (pdf_filename, id_publication)
                    VALUES (%s, %s)
                    ON CONFLICT (id_publication)
                    DO UPDATE SET pdf_filename = EXCLUDED.pdf_filename
                    """, (pdf_name, publication['id']))
                conn.commit()

        return pdf_path
    

    def fetch_all_missing_pdfs(self, publications=None, only_highest_version=True):
        """fetches all missing PDFs for publications in the database
        :param publications: a list of publications to fetch PDFs for. If None, fetches PDFs for all publications in the database
        :param only_highest_version: if True, only fetches the PDFs for the highest version of each publication['doi']
        """
        import random
        if publications is None:
            publications = self.find_publications_without_pdf(only_highest_version=only_highest_version)
        for publication in publications:
                result = self.fetch_pdf_from_medrXiv(publication)
                if result is not None: #a pdf has been downloaded, wait a bit before fetching the next one
                    sleep(random.randint(1,6)) #don't hammer the medrXiv server needlessly


    def has_pdf(self, publication: dict) -> bool:
        """checks if a publication has a PDF
        :param publication: a publication in the form of a dictionary
        :return: True if the publication has a PDF, False otherwise
        """
        return publication.get('pdf_filename', '') != ''


    def pdf_path(self, publication: dict, fetch: bool = False) -> str:
        """returns the path to the PDF of a publication
        :param publication: a publication in the form of a dictionary
        :return: the path to the PDF file
        """
        pdfpath = self.db.get_pdf_path(publication['id'])
        if not pdfpath and fetch:
            pdfpath = self.fetch_pdf_from_medrXiv(publication)
        return pdfpath


    def exclude_duplicates(self, publications: list[dict]) -> list[dict]:
        """excludes duplicate publications from a list
        :param publications: a list of publications in the form of dictionaries
        :return: a list of publications without duplicates
        """
        dois = set()
        unique_publications = []
        for publication in publications:
            doi = publication['doi']
            if doi not in dois:
                unique_publications.append(publication)
                dois.add(doi)
        return unique_publications  

     
    def find_publications_without_pdf(self, only_highest_version=True):
        """finds publications in the database without a PDF
        :param publications: a list of publications to search. If None, searches the whole database
        :param only_highest_version: if True, only searches for the highest version of each publication
        :return: a list of publications without a PDF
        """
        if only_highest_version:
            query = """WITH LatestVersions AS (
            SELECT m.doi, MAX(m.version) AS max_version
            FROM medrxiv m
            GROUP BY m.doi
            )
            SELECT m.id, m.doi, m.version
            FROM medrxiv m
            JOIN LatestVersions lv ON m.doi = lv.doi AND m.version = lv.max_version
            LEFT JOIN fulltext ft ON m.id = ft.id_publication
            WHERE ft.id_publication IS NULL OR ft.pdf_filename = ''"""
        else:
            query = """SELECT m.id, m.doi, m.version
            FROM medrxiv m
            LEFT JOIN fulltext ft ON m.id = ft.id_publication
            WHERE ft.id_publication IS NULL OR ft.pdf_filename = ''"""
        with self.db.connection() as conn:
            with conn.cursor(row_factory=dict_row) as cursor:
                cursor.execute(query)
                #return cursor
                rowcount=cursor.rowcount
                #logger.info(f"Found [{rowcount}] publications without a PDF.")
                for publication in tqdm(cursor, total=rowcount, desc="Fetching missing PDFs"):
                    yield dict(publication)
    

    def fetch_medrxiv_publications(self, from_date: str, to_date: str) -> list[dict]: 
        """Fetches publications from medrXiv for the given time span between from_date and to_date.
        ReturnsGets the publications them from cache if they have been fetched before, otherwise fetches them from the internet.
        Publications are saved to a local file for future use, as well as inserted into the caching database.

        :param from_date: The start date in the format 'YYYY-MM-DD'
        :param to_date: The end date in the format 'YYYY-MM-DD'
        
        :return: A list of publications in the form of dictionaries with the following keys:
                doi
                title
                authors
                author_corresponding
                author_corresponding_institution
                date
                version
                type
                license
                category
                jats xml path
                abstract
                published
                server
        """   
        all_publications = []

        #check what's in the database already
        latest_stored = self.db.latest_stored()
        if not latest_stored:
            latest_stored = from_date
        #if the latest stored date is before the requested date, fetch the new publications including the latest_stored date, 
        # in case there were any new publications on that day that hadn't been fetched yet on the last run
        if datetime.strptime(to_date, "%Y-%m-%d").date() > datetime.strptime(latest_stored, "%Y-%m-%d").date():
            publications=self.fetch_from_medrXiv(latest_stored, to_date)
            if len(publications) > 0:
                publications = self.exclude_duplicates(publications)
                all_publications.extend(publications)  #save them , in case something goes wrong during analysis or fetching pdfs           
        return all_publications
    

    def fetch_publications_by_keywords(self, keywords: list=[], from_date=None, to_date=None, limit=0) -> iter:
        """fetches publications from medrXiv based on a list of keywords
        :param keywords: a list of keywords
        :return: a list of publications in the form of dictionaries
        """
        publications=self.db.search_for(keywords, from_date=from_date, to_date=to_date, limit=limit)
        return publications


    def list_abstracts(self, publications: list[dict], format="markdown") -> str:
        """lists the abstracts of publications in a human-readable format
        :param publications: a list of publications in the form of dictionaries
        :param format: the format to return the abstracts in. Can be 'markdown' or 'html'
        :return: a string with the abstracts
        """
        if format == "markdown":
            abstracts = "\n".join([f"### {publication['title']}\n{publication['abstract']}" for publication in publications])
        elif format == "html":
            abstracts = "\n".join([f"<h3>{publication['title']}</h3><p>{publication['abstract']}</p>" for publication in publications])
        return abstracts
    



            
            
class MedrXivAssistant:
    """
    A class to assist with the medrXiv scraper
    The assistant can summarize publications, extract keywords, and critique studies
    The stored publications fetched from medrXiv are updated with the new information
    """

    def __init__(self, db: PublicationStorage, callback_notification=print, tqdm=tqdm):
        """
        initializes the MedrXivAssistant
        :param db: a DocumentStorage object from module PersistentStorage
        :param callback_notification: a callback function to notify the user of progress. If None, no notification is given.
            if provided, the function should take a string as an argument and display it to the user.
        :param tqdm: a tqdm object to display progress bars. If None, no progress bars are displayed.
        """
        self.callback_notification = callback_notification
        self.tqdm=tqdm
        self.scraper = MedrXivScraper()
        if db is None:
            db = PublicationStorage()
        self.db = db
        
     
    
    def fetch_missing_pdfs_from_medrXiv(self, publications=None, only_highest_version=True):
        """
        fetches all missing PDFs for publications in the database
        :param publications: a list of publications to fetch PDFs for. If None, fetches PDFs for all publications in the database
        :param only_highest_version: if True, only fetches the PDFs for the highest version of each publication
        """

        if publications is None:
            publications = self.find_publications_without_pdf(only_highest_version=only_highest_version)
        for publication in self.tqdm(publications, desc="Fetching missing PDFs"):
            result = self.fetch_pdf_from_publication(publication)
            #if result is not None:
       

    def analyze_publication(self, publication: dict, fetch_pdf=False, commit=True, force=False) -> dict:
        """analyzes a publication and adds
        - a summary of the publication
        - a list of keywords
        - a critique of the study
        - the full pdf file if available
        :param publication: the publication in the form of a dictionary
        :param fetch_pdf: if True, fetches the full PDF of the publication
        :param commit: if True, updates the publication in the database with the new information
        :param force: if True, forces the analysis to be done even if the publication already has the information
        :return: the publication with additional analysis information
        """
        self.callback_notification(f"Analyzing publication {publication['title']}")
        if fetch_pdf:
            publication['pdf_path'] = self.scraper.fetch_pdf_from_publication(publication)

        # for better performance, do not commit the changes to the database until all analyses are done
        publication['summary'] = self.summarize_publication(publication, commit=False, force=force)
        publication['keywords'] = self.extract_keywords(publication, commit=False, force=force)
        publication['abstract_critique'] = self.critique_study_abstract(publication, commit=False, force=force)
        
        #update the database with the new information
        if commit:
            self.scraper.db.update(publication, doc_ids=[publication.doc_id])
        return publication
    
    def analyze_publications(self, publications: list[dict], fetch_pdf=True, commit=True, force=False) -> list[dict]:
        """
        analyzes a list of publications
        :param publications: a list of publications in the form of dictionaries
        :param fetch_pdf: if True, fetches the full PDF of the publication
        :param commit: if True, updates the publication in the database with the new information
        :param force: if True, forces the analysis to be done even if the publication already has the information
        :return: the publications with additional analysis information
        """
        analyzed_publications = []
        for publication in self.tqdm(publications, desc="Analyzing publications"):
            analyzed_publication = self.analyze_publication(publication, fetch_pdf=fetch_pdf, commit=commit, force=force)
            analyzed_publications.append(analyzed_publication)
        return analyzed_publications
    
    def summarize(self, publication:dict, commit=True, force=False) -> str:
        """
        summarizes a publication's abstract
        :param publication: the publication in the form of a dictionary
        :param commit: if True, updates the publication in the database with the summary
        :param force: if True, forces the summary to be done even if the publication already has a summary
        :return: the publication, with the summary added
        """
        #self.callback_notification(f"Summarizing abstract of [{publication['title']}]")
        # if 'summary' in publication and len(publication['summary'])>0 and not force: #summary already exists
        #     return publication['summary']
        summarizer = Summarizer()
        summary = summarizer.summarize(publication['abstract'], n_sentences=3)
        if commit:
            self.db.save_summary(summary, id_publication=publication['id'])
        return summary
    
    def extract_keywords(self, publication: dict, commit=True, force=False) -> list[str]:
        """
        extracts keywords from a publication
        :param publication: the publication in the form of a dictionary
        :param commit: if True, updates the publication in the database with the keywords
        :param force: if True, forces the keywords to be extracted even if the publication already has keywords
        :return: publication updated with a list of keywords
        """
        extractor= KeywordExtractor()
        if 'keywords' in publication and len(publication['keywords'])>0 and not force: #keywords already exist
            return publication['keywords']
        publication['keywords'] = extractor.extract_keywords(publication['abstract'])
        if commit:
            self.scraper.db.update(publication, doc_ids=[publication.doc_id])
        return publication
    
    def critique_study_abstract(self, publication: dict, commit=True, force=False) -> str:
        """
        critiques the abstract of a publication
        :param publication: the publication in the form of a dictionary
        :param commit: if True, updates the publication in the database with the critique
        :param force: if True, forces the critique to be done even if the publication already has a critique
        :return: publicatin updated with a critique of the abstract
        """
        critique = StudyCritique()
        if 'abstract_critique' in publication and len(publication['abstract_critique'])>0 and not force: #critique already exists
            return publication['abstract_critique']
        publication['abstract_critique'] = critique.critique(publication['abstract'])
        if commit:
            self.scraper.db.update(publication, doc_ids=[publication.doc_id])
        return publication
    
    def summarize_all_abstracts(self, publications=None, force=False):
        """
        summarizes all publications in the database and commits the summaries to the database
        :param publications: a list of publications to summarize. If None, summarizes all publications in the database
        :param force: if True, forces the summaries to be done even if the publications already have summaries
        """
        if publications == None:
            publications = self.scraper.db #use the whole database
        for publication in self.tqdm(publications, desc="Summarizing abstracts"):
            publication = self.summarize_publication(publication, commit=True, force=force)

    def add_missing_summaries(self):
        """
        adds missing summaries for all publications in the database
        """
        publications = self.scraper.db.missing_summaries()
        for publication in self.tqdm(publications, desc="Adding missing summaries"):
            publication = self.summarize_publication(publication, commit=True)
            

    def keywords_for_all_abstracts(self, publications=None, force=False):
        """
        extracts keywords from all publications in either the parameter publications, else 
        in the whole database and commits them to the database
        :param publications: a list of publications to extract keywords from. If None, extracts keywords from the whole database
        :param force: if True, forces the keywords to be extracted even if the publications already have keywords
        """
        if publications == None:
            publications = self.scraper.db #use the whole database
        for publication in self.tqdm(publications, desc="Extracting keywords"):
            publication = self.extract_keywords(publication, commit=True, force=force)

    def critique_all_abstracts(self, publications=None, force=False):
        """
        critiques all abstracts in the parameter publications or else in the whole database and commits the critiques to the database
        :param publications: a list of publications to critique. If None, critiques all publications in the database
        :param force: if True, forces the critiques to be done even if the publications already have critiques
        """
        if publications == None:
            publications = self.scraper.db #use the whole database
        for publication in self.tqdm(publications, desc="Creating critique for abstracts"):
            publication = self.critique_study_abstract(publication, commit=True, force=force)

    def update_missing_data(self):
        """
        updates missing data for all publications in the database
        """
        db = self.scraper.db
        q=db.Query()
        missing_abstract_critiques = db.search(~q.abstract_critique.exists())
        if len(missing_abstract_critiques) > 0:
            self.callback_notification(f"Found {len(missing_abstract_critiques)} publications with missing abstract critiques")
            self.critique_all_abstracts(publications=missing_abstract_critiques)
        
        missing_summaries = db.search(~q.summary.exists())  
        if len(missing_summaries) > 0:
            self.callback_notification(f"Found {len(missing_summaries)} publications with missing summaries")
            self.summarize_all_abstracts(publications=missing_summaries)
        
        missing_keywords = db.search(~q.keywords.exists())
        if len(missing_keywords) > 0:
            self.callback_notification(f"Found {len(missing_keywords)} publications with missing keywords")
            self.keywords_for_all_abstracts(publications=missing_keywords)

      
if __name__=="__main__":
    scraper = MedrXivScraper()
    #scraper.fetch_latest_publications(fetch_pdfs=True)
    #scraper.fetch_all_missing_pdfs()
    scraper.update_summaries()
    #assistant = MedrXivAssistant()
    #assistant.summarize_all_abstracts()

    