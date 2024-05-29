import DBBackend
import os
import requests
from datetime import datetime, timedelta
from tqdm import tqdm
from time import sleep
from Summarizer import Summarizer
from KeywordExtractor import KeywordExtractor
from StudyCritique import StudyCritique

class MedrXivScraper:
    """fetches and caches publications from medrXiv"""

    def __init__(self, callback_notification=print, tqdm=tqdm):
        """initializes the MedrXivScraper
        :param callback_notification: a callback function to notify the user of progress. If None, no notification is given.
            if provided, the function should take a string as an argument and display it to the user.
        :param tqdm: a tqdm object to display progress bars. If None, no progress bars are displayed.
        """
        self.tqdm=tqdm
        self.callback_notification = callback_notification
        self.db = DBBackend.DBMedrXiv()
        self.callback_notification("MedrXivScraper initialized")



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
    


    def fetch_from_db(self, date: str) -> list[dict]:
        """fetches publications from the database for a given date
        :param date: the date in the format 'YYYY-MM-DD'
        :return: a list of publications in the form of dictionaries
        """
        publications = self.db.Query()
        results = self.db.search(publications.date == date)
        print(f"Found {len(results)} results in the database")
        return results
    
    

    def fetch_from_db_by_doi(self, doi: str) -> dict:
        """fetches publications from the database for a given doi
        :param doi: the doi of the publication
        :return: a publication in the form of a dictionary
        """
        publications = self.db.Query()
        results = self.db.search(publications.doi == doi)
        print(f"Found {len(results)} results in the database")
        if len(results) > 0:
            return results
        else:
            return None
    


    def fetch_from_server(self, date: str) -> list[dict]:
        """fetches publications from the medrXiv server for a given date
        :param date: the date in the format 'YYYY-MM-DD'
        :return: a list of publications in the form of dictionaries
        """
        base_url = f"https://api.medrxiv.org/details/medrxiv/{date}/{date}"
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
            # Check if more results are available
            messages = data.get('messages', [])
            if messages:
                message = messages[0]
                total_items = message.get('count', 0)
                if cursor + len(publications) >= total_items:
                    break  # No more results
                cursor += len(publications)
            else:
                break  # No messages, likely no more results
        self.callback_notification(f"fetched {len(all_publications)} publications")
        results = self.db.insert_multiple(all_publications)
        self.callback_notification(f"inserted {len(results)} into database")
        return publications


    
    def get_pdf_url(self, publication : dict) -> str:
        """creates a URL for full PDF download from a retrieved publication
		
		:param publication: dictionary, see fetch_medrxiv_publications() for keys
		:return: URL for downloading a PDF
		"""
        pdf_url = f"https://www.medrxiv.org/content/{publication['doi']}.full.pdf"
        return(pdf_url)
    


    def fetch_pdf_from_publication(self, publication: dict, path: str = "./library") -> str:
        """downloads the PDF of a publication to a given path
        :param publication: a publication in the form of a dictionary
        :param path: the path to save the PDF to
        :return: the path to the saved PDF
        """
        pdf_url = self.get_pdf_url(publication)
        
        #file name = sanitized doi
        pdf_path = os.path.join(path, f"{publication['doi'].replace('/', '-')}.pdf")
        
        #is the file already in our library?
        if os.path.isfile(pdf_path):
            if 'pdf_path' not in publication:
                publication['pdf_path'] = pdf_path
                self.db.update(publication, doc_ids=[publication.doc_id])   
            self.callback_notification(f"PDF already exists at {pdf_path}")
            return pdf_path
        
        #fetch the pdf
        self.callback_notification(f"Attempting to fetch PDF from {pdf_url}")
        try:
            response = requests.get(pdf_url)
        except Exception as e:
            self.callback_notification(f"Failed to fetch PDF from {pdf_url}: {e}")
            return None
        if response.status_code != 200:
            self.callback_notification(f"Failed to fetch PDF from {pdf_url}. Status code: {response.status_code}")
            return None
        
        #save the pdf file
        with open(pdf_path, 'wb') as f:
            f.write(response.content)
            publication['pdf_path'] = pdf_path
            self.db.update(publication, doc_ids=[publication.doc_id])    
        return pdf_path
    
    

    def fetch_all_missing_pdfs(self, publications=None):
        """fetches all missing PDFs for publications in the database
        :param publications: a list of publications to fetch PDFs for. If None, fetches PDFs for all publications in the database
        """
        if publications is None:
            publications = self.db
        for publication in self.tqdm(publications, desc="Fetching missing PDFs"):
            if 'pdf_path' not in publication:
                result = self.fetch_pdf_from_publication(publication)
                if result is not None: #a pdf has been downloaded, wait a bit before fetching the next one
                    sleep(3) #don't hammer the medrXiv server needlessly



    def exclude_duplicates(self, publications: list[dict]) -> list[dict]:
        """excludes duplicate publications from a list of publications
        :param publications: a list of publications in the form of dictionaries
        :return: a list of publications with duplicates (records already in database) removed
        """
        duplicates=0
        unique_publications = []
        qpub = self.db.Query()
        for publication in publications:
            if db.search(qpub.doi==publication['doi']):
                #this publication already exists in utr database, skip it
                duplicates+=1
                continue
            unique_publications.append(publication)
        self.callback_notification(f"Excluded {duplicates} duplicates")
        return unique_publications
    


    def fetch_medrxiv_papers(self, from_date: str, to_date: str, keywords=[]) -> list[dict]: 
        """Fetches publications from medrXiv for the given time span between from_date and to_date.
        ReturnsGets the publications them from cache if they have been fetched before, otherwise fetches them from the internet.
        Publications are saved to a local file for future use, as well as inserted into the caching database.

        :param from_date: The start date in the format 'YYYY-MM-DD'
        :param to_date: The end date in the format 'YYYY-MM-DD'
        :param testing: If True, fetches publications from a local text file instead of the internet

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

        dates= self.split_daterange_into_days(from_date, to_date)
        for date in dates:
            publications= self.fetch_from_db(date)
            if len(publications) > 0:
                all_publications.extend(publications)
            else:
                publications=self.fetch_from_server(date)
                if len(publications) > 0:
                    publications = self.exclude_duplicates(publications)
                    all_publications.extend(publications)  #save them , in case something hgoes wrong during analysis or fetching pdfs
                    for publication in publications: #get the pdfs
                        publication['pdf_path'] = self.fetch_pdf_from_publication(publication)
        if len(keywords)>0:   
            all_publications = [publication for publication in all_publications if any(keyword in publication['abstract'] for keyword in keywords)]            

        return all_publications
    
    def fetch_publications_by_keywords(self, keywords: list[str]) -> list[dict]:
        """fetches publications from medrXiv based on a list of keywords
        :param keywords: a list of keywords
        :return: a list of publications in the form of dictionaries
        """
        #Publication=self.db.Query()
        #publications = self.db.search(Publication.keywords.any(keywords))
        publications=self.db.case_insensitive_search('abstract', keywords)
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
    """A class to assist with the medrXiv scraper
    The assistant can summarize publications, extract keywords, and critique studies
    The stored publications fetched from medrXiv are updated with the new information"""

    def __init__(self, callback_notification=print, tqdm=tqdm):
        """initializes the MedrXivAssistant
        :param callback_notification: a callback function to notify the user of progress. If None, no notification is given.
            if provided, the function should take a string as an argument and display it to the user.
        :param tqdm: a tqdm object to display progress bars. If None, no progress bars are displayed.
        """
        self.callback_notification = callback_notification
        self.tqdm=tqdm
        self.scraper = MedrXivScraper()
       

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
            #publication['critique'] = self.critique_study_fulltext(publication)

        # for better performance, do not commit the changes to the database until all analyses are done
        publication['summary'] = self.summarize_publication(publication, commit=False, force=force)
        publication['keywords'] = self.extract_keywords(publication, commit=False, force=force)
        publication['abstract_critique'] = self.critique_study_abstract(publication, commit=False, force=force)
        
        #update the database with the new information
        if commit:
            self.scraper.db.update(publication, doc_ids=[publication.doc_id])
        return publication
    
    def summarize_publication(self, publication: dict, commit=True, force=False) -> str:
        """summarizes a publication's abstract
        :param publication: the publication in the form of a dictionary
        :param commit: if True, updates the publication in the database with the summary
        :param force: if True, forces the summary to be done even if the publication already has a summary
        :return: the publication, with the summary added
        """
        self.callback_notification(f"Summarizing abstract of [publication ]{publication['title']}]")
        if 'summary' in publication and len(publication['summary']>0) and not force: #summary already exists
            return publication['summary']
        summarizer = Summarizer()
        publication['summary'] = summarizer.summarize(publication['abstract'], n_sentences=3)
        if commit:
            self.scraper.db.update(publication, doc_ids=[publication.doc_id])
        return publication
    
    def extract_keywords(self, publication: dict, commit=True, force=False) -> list[str]:
        """extracts keywords from a publication
        :param publication: the publication in the form of a dictionary
        :param commit: if True, updates the publication in the database with the keywords
        :param force: if True, forces the keywords to be extracted even if the publication already has keywords
        :return: publication updated with a list of keywords
        """
        extractor= KeywordExtractor()
        if 'keywords' in publication and len(publication['keywords']>0) and not force: #keywords already exist
            return publication['keywords']
        publication['keywords'] = extractor.extract_keywords(publication['abstract'])
        if commit:
            self.scraper.db.update(publication, doc_ids=[publication.doc_id])
        return publication
    
    def critique_study_abstract(self, publication: dict, commit=True, force=False) -> str:
        """critiques the abstract of a publication
        :param publication: the publication in the form of a dictionary
        :param commit: if True, updates the publication in the database with the critique
        :param force: if True, forces the critique to be done even if the publication already has a critique
        :return: publicatin updated with a critique of the abstract
        """
        critique = StudyCritique()
        if 'abstract_critique' in publication and len(publication['abstract_critique']>0) and not force: #critique already exists
            return publication['abstract_critique']
        publication['abstract_critique'] = critique.critique(publication['abstract'])
        if commit:
            self.scraper.db.update(publication, doc_ids=[publication.doc_id])
        return publication
    
    def summarize_all_abstracts(self, publications=None, force=False):
        """summarizes all publications in the database and commits the summaries to the database
        :param publications: a list of publications to summarize. If None, summarizes all publications in the database
        :param force: if True, forces the summaries to be done even if the publications already have summaries
        """
        if publications == None:
            publications = self.scraper.db #use the whole database
        for publication in self.tqdm(publications, desc="Summarizing abstracts"):
            publication = self.summarize_publication(publication, commit=True, force=force)
            

    def keywords_for_all_abstracts(self, publications=None, force=False):
        """extracts keywords from all publications in either the parameter publications, else 
        in the whole database and commits them to the database
        :param publications: a list of publications to extract keywords from. If None, extracts keywords from the whole database
        :param force: if True, forces the keywords to be extracted even if the publications already have keywords
        """
        if publications == None:
            publications = self.scraper.db #use the whole database
        for publication in self.tqdm(publications, desc="Extracting keywords"):
            publication = self.extract_keywords(publication, commit=True, force=force)

    def critique_all_abstracts(self, publications=None, force=False):
        """critiques all abstracts in the parameter publications or else in the whole database and commits the critiques to the database
        :param publications: a list of publications to critique. If None, critiques all publications in the database
        :param force: if True, forces the critiques to be done even if the publications already have critiques
        """
        if publications == None:
            publications = self.scraper.db #use the whole database
        for publication in self.tqdm(publications, desc="Creating critique for abstracts"):
            publication = self.critique_study_abstract(publication, commit=True, force=force)

    def update_missing_data(self):
        """updates missing data for all publications in the database"""
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

        missing_pdfs = db.search(~q.pdf_path.exists())
        if len(missing_pdfs) > 0:
            self.callback_notification(f"Found {len(missing_pdfs)} publications with missing PDFs")
            self.scraper.fetch_all_missing_pdfs(publications=missing_pdfs)
            
            


if __name__=="__main__":
    #scraper = MedrXivScraper()
    #documents = scraper.fetch_medrxiv_papers('2024-05-28', '2024-05-28')
    #print(f"Retrieved {len(documents)} publications")
    #scraper.fetch_all_missing_pdfs()
    assistant = MedrXivAssistant()
    assistant.update_missing_data()
    #assistant.critique_all_abstracts()
    #assistant.summarize_all_abstracts()
    #assistant.keywords_for_all_abstracts()
    