
import fitz  # PyMuPDF
import re
import requests
from pprint import pprint


class MetaDataExtractor:
    """A class to extract Metadata such as DOIs and titles from PDF files."""
    
    def __init__(self, pdf_path=None):
        """
        Initialize the MetaDataExtractor with a PDF file path.
        :param pdf_path: The path to the PDF file to process.
            if not stated, you have to call e.g. extract first to access the extracted data
        """
        # Define a regular expression pattern for DOIs
        self.doi_pattern = r'10.\d{4,9}/[-._;()/:A-Z0-9]+'
        self.doi=None
        self.title=''
        if pdf_path:
            self.doi, self.title = self.extract(pdf_path)



    def extract(self, pdf_path: str) -> tuple(str, str):
        """
        Extract the DOI and title from a PDF file.
        :param pdf_path: The path to the PDF file to process.
        :return: A tuple containing the extracted DOI and title.
        """
        self.doi=self.extract_doi(pdf_path)
        self.title=self.extract_title(self.doi)
        return self.doi, self.title
    

    
    def extract_doi(self, pdf_path: str) -> str:
        """
        Extract the DOI from a PDF file.
        :param pdf_path: The path to the PDF file to process.
        :return: The extracted DOI.
        """
        # Open the PDF file
        doc = fitz.open(pdf_path)
        # Extract text from each page
        for page in doc:
            text = page.get_text()
            # Search for DOIs in the extracted text
            match = re.search(self.doi_pattern, text, re.IGNORECASE)
            # If a DOI is found, return it
            if match:
                self.doi = match.group(0)
                break
        # Close the document
        doc.close() 
        return self.doi



    def extract_title(self, doi):
        if doi is None:
            return ''
        # Construct the URL for the CrossRef API
        url = f'https://api.crossref.org/works/{doi}'
        
        # Make the GET request
        response = requests.get(url)
        
        # Check if the request was successful
        if response.status_code == 200:
            # Parse the JSON response
            data = response.json()
            pprint(data)
            # Extract the title (note: title is a list, but typically contains only one item)
            self.title = data['message']['title'][0] if data['message']['title'] else 'Title not found'
            
            return self.title
        else:
            return ''
        
 
# Example usage
if __name__ == '__main__':
    import argparse

    # Create the parser
    parser = argparse.ArgumentParser(description='Extract DOI from a PDF file.')
    
    # Add an argument for the PDF file path
    parser.add_argument('pdf_path', type=str, help='The path to the PDF file from which to extract the DOI.')
    
    # Parse the command-line arguments
    args = parser.parse_args()
    
    # Use the provided PDF path
    pdf_path = args.pdf_path
    
    # Extract the DOI
    #doi = extract_doi_from_pdf(pdf_path)
    x = MetaDataExtractor(pdf_path)
    print(x.doi)
    print(x.title)
