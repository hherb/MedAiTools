import os
from datetime import datetime
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.spatial.distance import cosine
import networkx as nx
from networkx.algorithms import community

#from langchain import OpenAI
from langchain_openai import OpenAI
from langchain.prompts import PromptTemplate
from langchain.chains.llm import LLMChain
#from langchain.embeddings import OpenAIEmbeddings
from langchain_community.embeddings import OpenAIEmbeddings
from langchain.docstore.document import Document
from langchain.chains.summarize import load_summarize_chain

"""
curl http://localhost:11434/v1/chat/completions \
-H "Content-Type: application/json" \
-d '{ 
  "model": "lmstudio-community/Meta-Llama-3-8B-Instruct-GGUF/Meta-Llama-3-8B-Instruct-Q8_0.gguf",
  "messages": [ 
    { "role": "system", "content": "Always answer in rhymes." },
    { "role": "user", "content": "Introduce yourself." }
  ], 
  "temperature": 0.7, 
  "max_tokens": -1,
  "stream": true
}'
"""

"""
curl http://localhost:11434/v1/completions \
-H "Content-Type: application/json" \
-d '{ 
  "model": "microsoft/Phi-3-mini-4k-instruct-gguf/Phi-3-mini-4k-instruct-fp16.gguf",
  "messages": [ 
    { "role": "system", "content": "Always answer in rhymes." },
    { "role": "user", "content": "Introduce yourself." }
  ], 
  "temperature": 0.7, 
  "max_tokens": -1,
  "stream": true
}'
"""

class SemanticTextSummarizer:
    def __init__(self, text, 
                 openai_base_url="http://localhost:11434/v1/", 
                 openai_api_key="lm-studio", 
                 #modelname="microsoft/Phi-3-mini-4k-instruct-gguf/Phi-3-mini-4k-instruct-fp16.gguf"):
                 modelname="PrunaAI/Phi-3-mini-128k-instruct-GGUF-Imatrix-smashed"):
        self.text = text
        self._openai_base_url=openai_base_url
        self._openai_api_key=openai_api_key
        self._modelname=modelname
        self.segments = self.preprocess_text(text)
        self.sentences = self.create_sentences(self.segments, MIN_WORDS=20, MAX_WORDS=80)
        self.chunks = self.create_chunks(self.sentences, CHUNK_LENGTH=5, STRIDE=1)
        self.chunks_text = [chunk['text'] for chunk in self.chunks]
        self._reduce_llm = OpenAI(openai_api_base= self._openai_base_url, openai_api_key=self._openai_api_key, temperature=0, model_name=self._modelname, max_tokens=-1)
        self._map_llm = OpenAI(openai_api_base= self._openai_base_url, openai_api_key=self._openai_api_key, temperature=0, model_name=self._modelname)

    def preprocess_text(self, text):
        # Get segments from txt by splitting on .
        segments = text.split('.')
        # Put the . back in
        segments = [segment + '.' for segment in segments]
        # Further split by comma
        segments = [segment.split(',') for segment in segments]
        # Flatten
        segments = [item for sublist in segments for item in sublist]
        return segments

    def create_sentences(self, segments, MIN_WORDS, MAX_WORDS):
        # Combine the non-sentences together
        sentences = []

        is_new_sentence = True
        sentence_length = 0
        sentence_num = 0
        sentence_segments = []

        for i in range(len(segments)):
            if is_new_sentence == True:
                is_new_sentence = False
            # Append the segment
            sentence_segments.append(segments[i])
            segment_words = segments[i].split(' ')
            sentence_length += len(segment_words)

            # If exceed MAX_WORDS, then stop at the end of the segment
            # Only consider it a sentence if the length is at least MIN_WORDS
            if (sentence_length >= MIN_WORDS and (i == len(segments) - 1) or segments[i].endswith('.')) or sentence_length >= MAX_WORDS:
                sentence = ' '.join(sentence_segments)
                sentences.append({
                    'sentence_num': sentence_num,
                    'text': sentence,
                    'sentence_length': sentence_length
                })
                # Reset
                is_new_sentence = True
                sentence_length = 0
                sentence_segments = []
                sentence_num += 1

        return sentences

    def create_chunks(self, sentences, CHUNK_LENGTH, STRIDE):
        sentences_df = pd.DataFrame(sentences)

        chunks = []
        for i in range(0, len(sentences_df), (CHUNK_LENGTH - STRIDE)):
            chunk = sentences_df.iloc[i:i+CHUNK_LENGTH]
            chunk_text = ' '.join(chunk['text'].tolist())

            chunks.append({
                'start_sentence_num': chunk['sentence_num'].iloc[0],
                'end_sentence_num': chunk['sentence_num'].iloc[-1],
                'text': chunk_text,
                'num_words': len(chunk_text.split(' '))
            })

        chunks_df = pd.DataFrame(chunks)
        return chunks_df.to_dict('records')

    def summarize(self, MAX_WORDS=250):

        combine_prompt_template = f'Write a {MAX_WORDS}-word summary of the following, removing irrelevant information. Finish your answer:\n{{text}}\n{MAX_WORDS}-WORD SUMMARY:'
        combine_prompt = PromptTemplate(template=combine_prompt_template, input_variables=["text"])
        map_prompt_template = """Firstly, give the following text an informative title. Then, on a new line, write a 75-100 word summary of the following text:
        {text}

        Return your answer in the following format:
        Title | Summary...
        e.g. 
        Why Artificial Intelligence is Good | AI can make humans more productive by automating many repetitive processes.

        TITLE AND CONCISE SUMMARY:"""

        map_prompt = PromptTemplate(template=map_prompt_template, input_variables=["text"]) 
        #print(map_prompt)
        docs = [Document(page_content=t) for t in self.chunks_text]
        #chain = load_summarize_chain(combine_prompt=combine_prompt, llm=llm, reduce_llm=reduce_llm)
        chain = load_summarize_chain(chain_type="map_reduce", map_prompt = map_prompt, combine_prompt = combine_prompt, return_intermediate_steps = True,
                              llm = self._map_llm, reduce_llm = self._reduce_llm)
        output = chain.invoke({"input_documents": docs}, return_only_outputs=True)
        final_summary = output['output_text']

        return final_summary
    
if __name__ == "__main__":
    txt_path = 'llmsherpa.text'
    with open(txt_path, 'r') as f:
        text = f.read()
    summarizer = SemanticTextSummarizer(text)
    print(text[:100])
    summary = summarizer.summarize()
    print(summary)