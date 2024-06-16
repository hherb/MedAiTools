importmetapub


from metapub import PubMedFetcher
fetch = PubMedFetcher()
pmids = fetch.pmids_for_clinical_query("diastolic hypertension and cognitive impairment", category="prognosis", optimization="narrow")
pmid= pmids[0]
article = fetch.article_by_pmid(pmid)
dir(article)
article.abstract