import DBBackend
import os
import requests
from datetime import datetime, timedelta
from tqdm import tqdm
from Summarizer import Summarizer
from KeywordExtractor import KeywordExtractor


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
            self.callback_notification(f"PDF already exists at {pdf_path}")
            return pdf_path
        
        #fetch the pdf
        self.callback_notification(f"Attempting to fetch PDF from {pdf_url}")
        response = requests.get(pdf_url)
        if response.status_code != 200:
            self.callback_notification(f"Failed to fetch PDF from {pdf_url}. Status code: {response.status_code}")
            return None
        
        #save the pdf file
        with open(pdf_path, 'wb') as f:
            f.write(response.content)
            publication['pdf_path'] = pdf_path
            self.db.update(publication, doc_ids=[publication.doc_id])    
        return pdf_path
    

    def fetch_medrxiv_papers(self, from_date: str, to_date: str) -> list[dict]: 
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
                    all_publications.extend(publications)
        
        return all_publications
    


class MedrXivAssistant:
    """A class to assist with the medrXiv scraper"""
    def __init__(self, callback_notification=print, tqdm=tqdm):
        """initializes the MedrXivAssistant
        :param callback_notification: a callback function to notify the user of progress. If None, no notification is given.
            if provided, the function should take a string as an argument and display it to the user.
        :param tqdm: a tqdm object to display progress bars. If None, no progress bars are displayed.
        """
        self.callback_notification = callback_notification
        self.tqdm=tqdm
        self.scraper = MedrXivScraper()
       

    def analyze_publication(self, publication: dict, fetch_pdf=False) -> dict:
        """analyzes a publication and adds
        - a summary of the publication
        - a list of keywords
        - a critique of the study
        - the full pdf file if available
        :param publication: the publication in the form of a dictionary
        :return: the publication with additional analysis information
        """
        self.callback_notification(f"Analyzing publication {publication['title']}")
        if fetch_pdf:
            publication['pdf_path'] = self.scraper.fetch_pdf_from_publication(publication)
            #publication['critique'] = self.critique_study_fulltext(publication)

        publication['summary'] = self.summarize_publication(publication)
        publication['keywords'] = self.extract_keywords(publication)
        #publication['abstract_critique'] = self.critique_study_abstract(publication)
        
        #update the database with the new information
        self.scraper.db.update(publication, doc_ids=[publication.doc_id])
        return publication
    
    def summarize_publication(self, publication: dict, commit=False) -> str:
        """summarizes a publication
        :param publication: the publication in the form of a dictionary
        :param commit: if True, updates the publication in the database with the summary
        :return: a summary of the publication
        """
        self.callback_notification(f"Summarizing publication {publication['title']}")
        summarizer = Summarizer()
        publication['summary'] = summarizer.summarize(publication['abstract'], n_sentences=3)
        if commit:
            self.scraper.db.update(publication, doc_ids=[publication.doc_id])
        return publication['summary']
    
    def extract_keywords(self, publication: dict, commit=False) -> list[str]:
        """extracts keywords from a publication
        :param publication: the publication in the form of a dictionary
        :param commit: if True, updates the publication in the database with the keywords
        :return: a list of keywords
        """
        extractor= KeywordExtractor()
        publication['keywords'] = extractor.extract_keywords(publication['abstract'])
        if commit:
            self.scraper.db.update(publication, doc_ids=[publication.doc_id])
        return publication['keywords']
    
    def summarize_all_abstracts(self):
        """summarizes all publications in the database"""
        for publication in self.tqdm(self.scraper.db, desc="Summarizing abstracts"):
            publication = self.summarize_publication(publication, commit=True)
            

    def keywords_for_all_abstracts(self):
        """extracts keywords from all publications in the database"""
        for publication in self.tqdm(self.scraper.db, desc="Extracting keywords"):
            publication = self.extract_keywords(publication, commit=True)
            
            


if __name__=="__main__":
    #scraper = MedrXivScraper()
    #documents = scraper.fetch_medrxiv_papers('2024-05-01', '2024-05-27')
    #print(f"Retrieved {len(documents)} publications")
    assistant = MedrXivAssistant()
    #assistant.summarize_all_abstracts()
    assistant.keywords_for_all_abstracts()