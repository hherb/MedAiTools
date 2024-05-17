# MetaAnalysisAppraiser.py
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

"""This module uses a LLM to analyze a meta-analysis paper for quality according to
the guidelines specified in https://www.nhlbi.nih.gov/health-topics/study-quality-assessment-tools
It uses a list of questions to evaluate the paper and generates a report based on the responses to the questions.
"""

METAANALYSIS_APPRAISAL_CRITERIA = """1. Is the review based on a focused question that is adequately formulated and described? 
2. Were eligibility criteria for included and excluded studies predefined and specified?
3. Did the literature search strategy use a comprehensive, systematic approach?
4. Were titles, abstracts, and full-text articles dually and independently reviewed for inclusion and exclusion to minimize bias?
5. Was the quality of each included study rated independently by two or more reviewers using a standard method to appraise its internal validity?
6. Were the included studies listed along with important characteristics and results of each study?
7. Was publication bias assessed? 
8. Was heterogeneity assessed? (This question applies only to meta-analyses.)"""

FOCUSED_QUESTION = """## Is the review based on a focused question that is adequately formulated and described?
The review should be based on a question that is clearly stated and well-formulated. An example would be a question that uses the PICO (population, intervention, comparator, outcome) format, with all components clearly described."""

ELIGIBILITTY_CRITERIA = """## Were eligibility criteria for included and excluded studies predefined and specified?
The eligibility criteria used to determine whether studies were included or excluded should be clearly specified and predefined. It should be clear to the reader why studies were included or excluded."""

LITERATURE_SEARCH_STRATEGY = """## Did the literature search strategy use a comprehensive, systematic approach?
The search strategy should employ a comprehensive, systematic approach in order to capture all of the evidence possible that pertains to the question of interest. At a minimum, a comprehensive review has the following attributes:
- Electronic searches were conducted using multiple scientific literature databases, such as MEDLINE, EMBASE, Cochrane Central Register of Controlled Trials, PsychLit, and others as appropriate for the subject matter.
- Manual searches of references found in articles and textbooks should supplement the electronic searches.
Additional search strategies that may be used to improve the yield include the following:
- Studies published in other countries
- Studies published in languages other than English
- Identification by experts in the field of studies and articles that may have been missed
- Search of grey literature, including technical reports and other papers from government agencies or scientific groups or committees; presentations and posters from scientific meetings, conference proceedings, unpublished manuscripts; and others. Searching the grey literature is important (whenever feasible) because sometimes only positive studies with significant findings are published in the peer-reviewed literature, which can bias the results of a review.
In their reviews, researchers described the literature search strategy clearly, and ascertained it could be reproducible by others with similar results.
"""

DUALLY_REVIEWED = """## Were titles, abstracts, and full-text articles dually and independently reviewed for inclusion and exclusion to minimize bias?
Titles, abstracts, and full-text articles (when indicated) should be reviewed by two independent reviewers to determine which studies to include and exclude in the review. Reviewers resolved disagreements through discussion and consensus or with third parties. They clearly stated the review process, including methods for settling disagreements.
"""

QUALITY_RATED = """## Was the quality of each included study rated independently by two or more reviewers using a standard method to appraise its internal validity?
Each included study should be appraised for internal validity (study quality assessment) using a standardized approach for rating the quality of the individual studies. Ideally, this should be done by at least two independent reviewers appraised each study for internal validity. However, there is not one commonly accepted, standardized tool for rating the quality of studies. So, in the research papers, reviewers looked for an assessment of the quality of each study and a clear description of the process used.
"""

STUDIES_LISTED = """## Were the included studies listed along with important characteristics and results of each study?
All included studies were listed in the review, along with descriptions of their key characteristics. This was presented either in narrative or table format.
"""

PUBLICATION_BIAS = """## Was publication bias assessed?
Publication bias is a term used when studies with positive results have a higher likelihood of being published, being published rapidly, being published in higher impact journals, being published in English, being published more than once, or being cited by others.425,426 Publication bias can be linked to favorable or unfavorable treatment of research findings due to investigators, editors, industry, commercial interests, or peer reviewers. To minimize the potential for publication bias, researchers can conduct a comprehensive literature search that includes the strategies discussed in Question 3.
A funnel plot–a scatter plot of component studies in a meta-analysis–is a commonly used graphical method for detecting publication bias. If there is no significant publication bias, the graph looks like a symmetrical inverted funnel.
Reviewers assessed and clearly described the likelihood of publication bias.
"""

HETEROGENEITY = """## Was heterogeneity assessed? (This question applies only to meta-analyses.)
Heterogeneity is used to describe important differences in studies included in a meta-analysis that may make it inappropriate to combine the studies. Heterogeneity can be clinical (e.g., important differences between study participants, baseline disease severity, and interventions); methodological (e.g., important differences in the design and conduct of the study); or statistical (e.g., important differences in the quantitative results or reported effects).
Researchers usually assess clinical or methodological heterogeneity qualitatively by determining whether it makes sense to combine studies. For example:
Should a study evaluating the effects of an intervention on CVD risk that involves elderly male smokers with hypertension be combined with a study that involves healthy adults ages 18 to 40? (Clinical Heterogeneity)
Should a study that uses a randomized controlled trial (RCT) design be combined with a study that uses a case-control study design? (Methodological Heterogeneity)
Statistical heterogeneity describes the degree of variation in the effect estimates from a set of studies; it is assessed quantitatively. The two most common methods used to assess statistical heterogeneity are the Q test (also known as the X2 or chi-square test) or I2 test.
Reviewers examined studies to determine if an assessment for heterogeneity was conducted and clearly described. If the studies are found to be heterogeneous, the investigators should explore and explain the causes of the heterogeneity, and determine what influence, if any, the study differences had on overall study results.
"""
QUESTIONS = (FOCUSED_QUESTION, ELIGIBILITTY_CRITERIA, LITERATURE_SEARCH_STRATEGY, 
             DUALLY_REVIEWED, QUALITY_RATED, STUDIES_LISTED, PUBLICATION_BIAS, HETEROGENEITY)

SYSTEM_PROMPT = """You are an expert in meta-analysis appraisal.
You will be given a research paper to appraise for meta-analysis quality.
You will be given a list of criteria to evaluate the research paper.
Please evaluate the research paper according to those criteria.
Take time to consider each criterion carefully and provide a well reasoned evaluation.
Here is the text of the research paper: <start paper> {metaanalysistext} <end paper>
"""

REPORT_PROMPT="""You will write a report on the quality of the research paper according to the criteria.
For each criterion, you will write a paragraph evaluating the quality of the research paper.
You MUST write your report in APA format
"""

import time
import logging
from medai.tools.pdf import parse_pdf


import asyncio
#import nest_asyncio
#nest_asyncio.apply()


appraiser_logger = logging.getLogger('Appraisals')
appraiser_logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler = logging.StreamHandler()
handler.setFormatter(formatter)
appraiser_logger.addHandler(handler)

class Appraiser:
    def __init__(self, 
                 metaanalysistext, 
                 llm, 
                 questions=QUESTIONS, 
                 criteria = METAANALYSIS_APPRAISAL_CRITERIA,
                 system_prompt=SYSTEM_PROMPT):
        """
	    Fetches a list of publications from medrxiv from start_date to end_date
	
	    :metaanalysistext: str, the text to be appraised. Either a pdf file or a string containig the text
        :llm: , the large language model instance to use for inference
        :questions: tuple, a tuple of strings representing the appraisal criteria
        :system_prompt: str, the system prompt for the appraiser LLM
        """
        if metaanalysistext.endswith('.pdf'):
            appraiser_logger.info(f"Parsing PDF file: {metaanalysistext}")
            self.metaanalysistext =  asyncio.run(parse_pdf(metaanalysistext))
            appraiser_logger.info(f"PDF file parsed successfully: {metaanalysistext[:50]}...")
        else:
            self.metaanalysistext = metaanalysistext
        self.llm = llm
        self.questions = questions
        self.system_prompt = system_prompt.format(metaanalysistext=metaanalysistext)
        self.responses = []
        self.criteria=criteria.split('\n')
    
    def evaluate(self, question) -> str:
        """Evaluates a single question using the LLM
        :question: str, the question to evaluate
        :returns: str, the response from the LLM
        """
        question_title = question.split('\n')[1] #every question starts with a newline then the heading  
        appraiser_logger.info(f"Evaluating: {question_title}")  
        start_time= time.time()
        response = self.llm.generate(question)
        end_time = time.time()
        appraiser_logger.info(f"EVAL: {response}")
        appraiser_logger.info(f"Time taken for evaluation: {end_time - start_time} seconds")
        return response
        
            
    def appraise(self):
        """Processes the list of questions one by one and generates a response for each
        The responses are stored in self.responses"""    
        all_start_time= time.time()
        i=0
        print(f">>>{self.questions} [{len(self.questions)}] TYPE: {type(self.questions)} <<<") 
        for question in self.questions:
            i+=1
            response = self.evaluate(question)
            self.responses.append(response)
            appraiser_logger.info(f"\nAppraisal complete, response = {response}, L={len(self.responses)}\n")
        all_end_time = time.time()
        appraiser_logger.info(f"Time taken for whole appraisal: {all_end_time - all_start_time} seconds")
    
    def write_report(self):
        """Writes a report based on the responses to the questions
        :returns: str, the report
        """
        report = ""
        for i in range(len(self.criteria)-1):
            report += f"Criterion : {self.criteria[i]}\n"
            report += f"Response: {self.responses[i]}\n\n"
        return report


if __name__ == "__main__":
    # get the pdf filename from the command line
    import argparse
    arg_parser = argparse.ArgumentParser(description='Appraise a meta-analysis paper.')
    arg_parser.add_argument('FileName', metavar='filename', type=str, help='the name of the PDF file to process')
    args = arg_parser.parse_args()

    # create a LLM instance, 
    from LLM import LLM
    llm = LLM()
    
    # Process the PDF file into markdown text
    #from medai.tools.pdf import extract_text_from_pdf
    #meta = asyncio.run(extract_text_from_pdf(args.FileName))

    # get the meta-analysis appraisal report
    #with open(args.FileName, 'r') as f:
    #with open('meta_B.md', 'r') as f:
    #    meta = f.read() 
    #appraiser = Appraiser(meta, llm)

    appraiser = Appraiser(args.FileName, llm)
    appraiser.appraise()
    report = appraiser.write_report()
    print(report)