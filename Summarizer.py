from medai.LLM import answer_this

class Summarizer:
    def __init__(self, modelname='ollama/Llama3_8b_Instruct_32k:latest'):
        
        self.modelname=modelname
        #print(f"Summarizer initialized with texttype: {texttype}, using model: {model.modelname}")


    def summarize(self, text: str, n_sentences: int = 5) -> str:
        prompt=f"""Summarize the following document into a maximum of {n_sentences} sentences, 
        making sure you capture the essence and key points of the text. 
        Respond with only the summary of the text in dot points and nothing else: 
        <begin text> {text} <end text>""",
        #return self.llm.generate(prompt)
        return answer_this(prompt, modelname=self.modelname)


if __name__ == "__main__":
        
    text= """Artificial Intelligence in Diabetes Care: 
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

    summarizer=Summarizer()
    print(summarizer.summarize(text, n_sentences=3))
        