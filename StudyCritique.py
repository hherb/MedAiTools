# StudyCritique.py
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

import os
from litellm import completion
from medai.tools.apikeys import load_api_keys	  
from PDFParser import PDFParser

FAST_LLM="gpt-3.5-turbo-instruct"
SMART_LLM="gpt-4o"

#The API keys needed for this to work - they will be loaded from the os environment:
APIS=('OPENAI_API_KEY', 'LLAMA_CLOUD_API_KEY')
load_api_keys(APIS)


SYSTEM_PROMPT = """you are an experienced health scientist and clinician. 
You will analyze the presented publication or study to the best of your abilities
and provide the requested details. Pay particular attention to the study population, 
whether the findings can be extrapolated to the general population or a specific target population,
where the intervention and the comparator is, and what the significant findings / outcomes are.
Always try and find out whether overall mortality was among the outcome criteria, and mention this in your findings
"""

CRITIQUE_PROMPT = """Identify the main weaknesses in this study / argumentation 
	and list them as dot points in html format (<li> ...</li>). 
	ONLY return the list without any introductory sentences.
	Here is the document: """

RELEVANCE_FOR_CATEGORY_PROMPT = """If you think the following text is relevant to the practice of {category}, 
	please state in less than 4	 sentences why you think so. Be brief and terse in your response! """

RERANK_BY_RELEVANCE_PROMPT = """You are a senior doctor working in Emergency Medicine in a 
	remote Australian hospital with very limited resources. 
	Your focus is on detecting, averting or managing ACUTE life threatening scenarios. 
	From the following summaries, select the {top_k} ones with the highest relevance to you, 
	ordered by relevance for your work. Here are the summaries: {summaries}. IMPORTANT: ONLY
	return a comma separated list of numbers (the indices of the summaries), no other comments
	and no explanations. Answer format is for example '15,3,7...'"""
	
SUMMARY_PROMPT = """summarize the following document into a maximum of {n_sentences}.
				 Pay attention not to miss any details of importance in the summary. 
				 Here is the document: """
	                        
					                           																			
 
class StudyCritique:

	def __init__(self, 
			     llm, 
				 system_prompt = SYSTEM_PROMPT):
		self._system_prompt = system_prompt
		self._llm = llm

	def complete(self, prompt, model=FAST_LLM):
		response = self._llm( model=model,
  			messages=[{ "content": f"{prompt}","role": "user"}]
		)
		return(response.choices[0].message.content.strip())
	
	def pdf2document(self, pdf_file):
		if pdf_file is not None:
			doc = PDFParser.parse(pdf_file)
			return(doc)
		else:
			print("ERROR: empty document sent for conversion")

	def summary(self, document, max_sentences=15, prompt=SUMMARY_PROMPT):
		print("composing a summary of the publication ...")
		response = self.complete(prompt.format(n_sentences=str(max_sentences)) + document)
		return(response)
		
	def critique(self, document, prompt=CRITIQUE_PROMPT):
		print("preparing a critique of the publication ...")
		response = self.complete(prompt + document, model=SMART_LLM)
		return(response)
		
	def rerank(self, summaries, top_k=5, prompt=RERANK_BY_RELEVANCE_PROMPT):
		print("re-ranking summaries...")
		myprompt = prompt.format(summaries=summaries, top_k=top_k)
		response = self.complete(myprompt)
		return(response)
		
if __name__ == "__main__":
	document = """Artificial Intelligence in Diabetes Care: 
	Evaluating GPT-4's Competency in Reviewing Diabetic Patient Management Plan in Comparison to Expert Review
	Background: The escalating global burden of diabetes necessitates innovative management strategies. 
	Artificial intelligence, particularly large language models like GPT-4, presents a promising avenue 
	for improving guideline adherence in diabetes care. Such technologies could revolutionize patient 
	management by offering personalized, evidence-based treatment recommendations. 
	Methods: A comparative, blinded design was employed, involving 50 hypothetical diabetes mellitus case 
	summaries, emphasizing varied aspects of diabetes management. 
	GPT-4 evaluated each summary for guideline adherence, classifying them as compliant or 
	non-compliant, based on the ADA guidelines. A medical expert, blinded to GPT-4's assessments, 
	independently reviewed the summaries. Concordance between GPT-4 and the expert's evaluations 
	was statistically analyzed, including calculating Cohen's kappa for agreement. 
	Results: GPT-4 labelled 30 summaries as compliant and 20 as non-compliant, while the expert 
	identified 28 as compliant and 22 as non-compliant. Agreement was reached on 46 of the 50 
	cases, yielding a Cohen's kappa of 0.84, indicating near-perfect agreement. 
	GPT-4 demonstrated a 92% accuracy, with a sensitivity of 86.4% and a specificity of 96.4%. 
	Discrepancies in four cases highlighted challenges in AI's understanding of complex clinical judgments 
	related to medication adjustments and treatment modifications. Conclusion: GPT-4 exhibits 
	promising potential to support healthcare professionals in reviewing diabetes management 
	plans for guideline adherence. Despite high concordance with expert assessments, instances 
	of non-agreement underscore the need for AI refinement in complex clinical scenarios. 
	Future research should aim at enhancing AI's clinical reasoning capabilities and exploring 
	its integration with other technologies for improved healthcare delivery."""
	
	unranked = """
Summary 1: a comparative, blinded design was employed, involving 50 hypothetical diabetes mellitus case summaries. GPT-4 labelled 30 summaries as compliant and 20 as non-compliant. the expert identified 28 as compliant and 22 as non-compliant.

Summary 2: machine learning has identified an association between right sided precordial U waves and moderate to severe aortic stenosis. no study has explored the role of ECG screening by primary care physicians for patients with unknown aortic stenosis status.

Summary 3: deep learning models are becoming increasingly accessible for automated detection of diabetic retinopathy (DR). the study used one proprietary and two publicly available datasets, containing two-dimensional (2D) wide-angle color fundus, scanning laser ophthalmoscopy (SLO) fundus, and three-dimensional (3D) Optical Coherence Tomography (OCT) B-Scans, to assess deep learning models.

Summary 4: two neuropathological hallmarks of Alzheimer's disease are the accumulation of amyloid-beta (Abeta) proteins and alterations in cortical neurophysiological signaling. cortical alignments are topographically aligned with cholinergic, serotonergic, and dopaminergic neurochemical systems.

Summary 5: treatment of peritoneal mesothelioma poses significant challenges owing to its rare incidence, heterogeneity and limited clinical evidence. the consensus-driven pathway provides essential guidance regarding the management of PeM.

Summary 6: vascular thromboembolism (VTE) poses a significant risk during the acute phase post-stroke. early recognition is critical for preventive intervention of VTE. the median age of patients with VTE was significantly older than that of non-VTE individuals.

Summary 7: despite decades of research, sepsis remains a major challenge faced by patients, clinicians, and medical systems worldwide. we developed a predictive model for sepsis using data from the physionet cardiology challenge 2019 ICU database. the model was designed to anticipate sepsis before the appearance of clinical symptoms."""
	
	sc = StudyCritique(completion)
	print(f"SUMMARY:\n {sc.summary(document)}\n" + 50*"="+"\n")
	print(f"CRITIQUE:\n {sc.critique(document)}\n" + 50*"="+"\n")
	print(f"RERANK:\n {sc.rerank(summaries=unranked)}\n" + 50*"="+"\n")

	
	
	