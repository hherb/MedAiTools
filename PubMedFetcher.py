import metapub


from metapub import PubMedFetcher
fetch = PubMedFetcher()
pmids = fetch.pmids_for_clinical_query("diastolic hypertension and cognitive impairment", category="prognosis", optimization="narrow")
for pmid in pmids:
    article = fetch.article_by_pmid(pmid)
    print(article.abstract)