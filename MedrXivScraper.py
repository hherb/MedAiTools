# This code has been released by Dr Horst Herb under the GPL 3.0 license
# contact author under hherb@aiinhealth.org if you want to collaborate or need
# a different license
# Experimental draft - not ready for production!!!
#
# this library fetches a list of publications (title, authors, abstracts) from medrxiv 
# from start_date to end_date
# then screens that list for keywords
# then downloads all pdf files of those pre-screened publications of interest

import os
import requests
import json
from datetime import datetime, timedelta
from transformers import T5Tokenizer, T5ForConditionalGeneration
from tqdm import tqdm #progress bar

import StudyCritique  #our own AI based paper analyzer

#A template for a neat output of retrieved documents. Also requires teh file "styles.css"
#in the current working directory
html_template = """<!DOCTYPE html>
<html lang="en">
<head>
	<meta charset="UTF-8">
	<meta name="viewport" content="width=device-width, initial-scale=1.0">
	<title>Today's reading list</title>
	<link rel="stylesheet" href="styles.css">
</head>
<body>
	<header>
		<h1>Horst's reading list</h1>
		<h2>my helpful librarian, fetching the latest from medRxiv every day</h2>
	</header>

	{html}
	
	<script>
		function toggleAbstract(button) {{
			var abstract = button.nextElementSibling;
			abstract.style.display = abstract.style.display === 'none' ? 'block' : 'none';
		}}
		function toggleCritique(button) {{
			var critique = button.nextElementSibling;
			critique.style.display = critique.style.display === 'none' ? 'block' : 'none';
		}}
	</script>
</body>
</html>
"""


class MedrXivScraper:
	"""
	Fetches a list of publications from medrxiv from start_date to end_date
	
	:param from_date: str, format yyyy-mm-dd
		Required
	:param end_date: str, format yyyy-mm-dd. 
		Default is today's date
	:param max_candidates: int, number of publications (ordered from most to least suited) to be returned. 
		Default = 20
	:param prompt: str. If specified, an LLM will use it to rank the publications in alignment with the prompt
		Default: not specified = no LLM analysis
	:return: List of publications in dict format fetched from the medRxiv API.
	"""
	def __init__(self, from_date, end_date=None, max_candidates=10, prompt=None, criticise=True, summarize=True, abstract_summarizer=False):
		self._from_date = from_date
		if end_date is None:
			end_date = datetime.now().strftime("%Y-%m-%d") #today
		self._end_date = end_date
		self._prompt = prompt
		self._all_publications=[] #the unfiltered and unscreened downloaded publications
		self._keywords=[]
		self._categories=[]
		self._prioritize_category = False
		self._summarize = summarize
		self._abstract_summarizer = abstract_summarizer
		if self._summarize and not self._abstract_summarizer:
			# Load pre-trained T5 model and tokenizer
			self._summarizer_name = "t5-small"
			self._summarizer_tokenizer = T5Tokenizer.from_pretrained(self._summarizer_name, legacy=False)
			self._summarizer_model = T5ForConditionalGeneration.from_pretrained(self._summarizer_name)
		self._criticise = criticise
		self._analyzer = StudyCritique.StudyCritique()
##########################################################################################		

			
	def set_keywords(self, keywords):
		"""if a list of keyword strings is set, the retrieved documents will be filtered by 
		the presence of ANY of the listed keywords.
		TODO: logical operators such as AND, OR, NOT
		
		:param keywords: list of keywords, eg ["emergency", "fracture"]. capitalisation agnostic.
		"""
		
		self._keywords = keywords
		
	def set_category(self, categories=["Emergency Medicine", ], priority=True):
		"""If a category is stated, the retrieved documents will be filtered by that category.
		TODO: allow a list of categories
		:param category: string. See https://www.medrxiv.org/about/FAQ
		:param priority: boolean. If priority is True, then the category filter will be applied prior to the keyword filter
		"""
		
		self._categories = categories
		self._prioritize_category = priority

##########################################################################################		

		
	def fetch_medrxiv_publications(self, testing=False):
		"""
		Fetches a list of publications from medrxiv from start_date to end_date
		TODO: finish testing functionality, where actual download is bypassed using cached data
		
		:return: List of publication dicts fetched from the medRxiv API.
		The following metadata elements are returned as strings in each dict:
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
		
		if testing:
			try:
				with open('dumpfile.json', 'r') as file:
					self._all_publications = json.load(file)
			except:
				pass

		base_url = f"https://api.medrxiv.org/details/medrxiv/{self._from_date}/{self._end_date}"
		print(f"attempting to fetch new publications from {base_url}")
		cursor = 0
		all_results = []
	
		while True:
			url = f"{base_url}/{cursor}/json"
			response = requests.get(url)
			data = response.json()
	
			publications = data.get('collection', [])
			all_results.extend(publications)
	
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
	
		self._all_publications.extend(all_results)
		
		result = self._all_publications
		with open('dumpfile.json', 'w') as f:
			json.dump(json.dumps(result, indent=4), f, indent=4)
		
		print(f"fetched {len(result)} publications")
		
		if self._prioritize_category: #filter before keyword filter
			if len(self._categories) > 0:
				result = self._screen_publications_by_categories(result, self._categories)
		
		if len(self._keywords) > 0:
			result =  self.screen_publications_by_keywords(result, self._keywords) 
			
		if not self._prioritize_category: #filetr after keyword filter
			if len(self._categories) > 0:
				result = self._screen_publications_by_categories(result, self._categories)		
			
		if self._summarize:
			result =  self.summarize(result)
			
		if self._criticise:
			new_results=[]
			for publication in tqdm(result):
				critique = self._analyzer.critique(publication['abstract'])
				publication['critique'] = critique
				new_results.append(publication)
			result=new_results	
						
		return result
	 
##########################################################################################		

		
	def screen_publications_by_keywords(self, publications, keywords):
		"""
		Screens a list of publications for specified keywords in the title or abstract.
	
		:param publications: List of publication dicts fetched from the medRxiv API.
		:param keywords: List of keywords to search for in the title and abstract.
		:return: List of publication dicts that contain any of the keywords in their title or abstract.
		"""
		print(f"screening {len(publications)} publications for the specified key words...")
		print(keywords)
		print("...")
		
		filtered_publications = []
		keywords_lower = [keyword.lower() for keyword in keywords]
	
		for publication in tqdm(publications):
			title = publication.get('title', '').lower()
			abstract = publication.get('abstract', '').lower()
	
			# Check if any of the keywords appear in the title or abstract
			if any(keyword in title or keyword in abstract for keyword in keywords_lower):
				filtered_publications.append(publication)
				print(publication['title']+"\n-----------------------")
				
		print(f"{len(filtered_publications)} publications passed screening")
		return filtered_publications	
		
	##########################################################################################		
	
		
	def rank_publications_by_interest(self, publications, prompt = "Is the following context useful for a doctor working in emergency medicine?"):
		pass
	
	##########################################################################################		
	
		
	def evaluate_publications(self, publications, prompt = "List the weaknesses you can identify in the following publication. Use dot points."):
		pass
	
	##########################################################################################
	
	def summarize(self, publications):
		"""create a brief summary for each publication in a list of publications
		
		:param publication: dictionary, see fetch_medrxiv_publications() for keys
		:return: the list of publications, with an added key "summary" and the respective summary data
		
		TODO: presently, summarisation is hardcoded with the extractive T5 summarizer, which
		seemed to work better than BERT or BART on brief initial testing 
		This should be user definable, and allow for more advanced abstractive summarizers		
		"""
		
		print(f"summarizing {len(publications)} documents ...") 
		summarized_publications=[]
		
		for publication in tqdm(publications):
			# Tokenize and summarize the input text using T5
			inputs = self._summarizer_tokenizer.encode("summarize: " + publication['abstract'], return_tensors="pt", max_length=1024, truncation=True)
			summary_ids = self._summarizer_model.generate(inputs, max_length=250, min_length=50, length_penalty=2.0, num_beams=4, early_stopping=True)
			
			# Decode and output the summary
			summary_t5	= self._summarizer_tokenizer.decode(summary_ids[0], skip_special_tokens=True)
			publication['summary'] = summary_t5
			#print(summary_t5+"\n-----------------------")
			summarized_publications.append(publication)
			
		return(summarized_publications)

	##########################################################################################		

	
	def get_pdf_URL(self, publication):
		"""creates a URL for full PDF download from a retrieved publication
		
		:param publication: dictionary, see fetch_medrxiv_publications() for keys
		:return: URL for downloading a PDF
		"""
		
		pdf_url = f"https://www.medrxiv.org/content/{publication['doi']}.full.pdf"
		return(pdf_url)

	##########################################################################################		

	
	def download_pdf(self, publication, output_dir = "./pdf"):
		"""download the corresponding pdf file for a given medRxiv publication in dict format
			into the specified path. The pdf will be renamed with the title of the publication
			
			:param publication: dictionary, see fetch_medrxiv_publications() for keys
			:param output_dir: string. the path into which the pdf will be downloaded. 
			                   The specified output directory will be created if it doesn't exist
			
			:return Boolean - True if succesfully downloaded, else False
			"""
		
		if not os.path.exists(output_dir):
			os.makedirs(output_dir)
	
		pdf_url = get_pdf_URL(publication)
		title = publication.get('title', '')
		pdf_filename = f"{output_dir}/{title}.pdf"
	
		try:
			response = requests.get(pdf_url)
			if response.status_code == 200:
				with open(pdf_filename, "wb") as pdf_file:
					pdf_file.write(response.content)
					print(f"Downloaded: {title}.pdf")
					print("\n=========================================================================\n")
				return True
			else:
				print(f"Failed to download: {title}.pdf")
				return False
		except Exception as e:
			print(f"Error downloading {title}.pdf: {e}")
			return False
	
	
	##########################################################################################		
			
	def list_abstracts(self, publications, format="html", fromfile=""):
		"""
		Generates a single HTML document string with each  title followed by its abstract.
		
		:param publications: publications in dict format, see fetch_medrxiv_publications()
		:return: A string containing the composed HTML document.
		"""
		
		if len(fromfile) > 0:
			with open(fromfile, 'r') as file:
				publications = json.load(file)
		
		html=""	 #we will create a list of publications by appending to this string
		
		print("Generating html ...")
		for doc in tqdm(publications):
			pdfurl = self.get_pdf_URL(doc)
			html += f"""
			<section class="article">
				<h3 class="publication-title">{doc['title']} - ({doc['date']})</h3>
				<p class="authors">{doc['authors']}</p>
				<p class="summary">{doc['summary']}</p>
				<div class="abstract-container">
					<button onclick="toggleAbstract(this)">Read Abstract</button>
					<p class="abstract" style="display:none;">{doc['abstract']}</p>
				</div>
				<div class="abstract-container">
					<button onclick="toggleCritique(this)">Read Critique</button>
					<p class="abstract" style="display:none;">{doc['critique']}</p>
				</div>
				<a href="{pdfurl}" target="_blank"> <button>Full PDF</button></a>
			</section>			
			"""
		html_output = html_template.format(html=html)
		
		return html_output
		
		

	##########################################################################################		
		
		

if __name__ == "__main__":
	# Example usage of the medrxiv_scraper class
	
	end_date = datetime.now().strftime("%Y-%m-%d")	#today
	how_many_days_past = 2
	start_date = (datetime.strptime(end_date, '%Y-%m-%d')-timedelta(days=how_many_days_past)).strftime('%Y-%m-%d')
	
	keywords = ["GPT4", "machine learning", "deep learning", "large language model", "LLM", "Anthropic", "OpenAI", "Artifical Intelligence"]
	
	scraper = MedrXivScraper(from_date=start_date, end_date=end_date, summarize=True)
	scraper.set_keywords(keywords)
	
	publications = scraper.fetch_medrxiv_publications()
		
	# # Print the titles and DOIs of the fetched publications
# 	for publication in publications:
# 		print(f"\nTitle: {publication['title']}")
# 		print(f"\nAuthors: {publication['authors']}")
# 		print(f"\nDOI: {publication['doi']}")
# 		print(f"\nPublication Date: {publication['date']}")
# 		print(f"\nAbstract: {publication['abstract']}\n")
# 		print(f"\nSummary: {publication['summary']}\n")
# 	
# 		print("\n=========================================================================\n")
# 		#scraper.download_pdf(publication)
	
	
	# Optionally, save the results to a file
	#with open('new_medrxiv_publications.json', 'w') as f:
		#json.dump(publications, f, indent=4)
		
	with open('new_medrxiv_publications.html', 'w') as f:
		f.write(scraper.list_abstracts(publications, format="html"))
