# This code is mostly refactored from Isaac Tham's 
# https://github.com/thamsuppp/llm_summary_medium/blob/master/summarizing_llm.ipynb
# You can read the details about it at   
# https://towardsdatascience.com/summarize-podcast-transcripts-and-long-texts-better-with-nlp-and-ai-e04c89d3b2cb
#
# Changes:
# - refactored as reusable and configurable class
# - now allows alternative LLMs/embeddings other than OpenAI

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
curl http://localhost:11434/v1/chat/completions \
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

from datetime import datetime
import pandas as pd
import numpy as np
import json
import os
import matplotlib.pyplot as plt
from scipy.spatial.distance import cosine
import networkx as nx
from networkx.algorithms import community

from langchain import OpenAI
from langchain.prompts import PromptTemplate
from langchain.chains.llm import LLMChain
from langchain.embeddings import OpenAIEmbeddings
from langchain.docstore.document import Document
from langchain.chains.summarize import load_summarize_chain

class SemanticSummarizer:
    
    def __init__(self):
        pass

    def segment_text(self, text):
        # Get segments from txt by splitting on .
        segments =  text.split('.')
        # Put the . back in
        segments = [segment + '.' for segment in segments]
        # Further split by comma
        segments = [segment.split(',') for segment in segments]
        # Flatten
        segments = [item for sublist in segments for item in sublist]
        return segments


    def make_sentences(self, segments, MIN_WORDS=1, MAX_WORDS=50):
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
        if (sentence_length >= MIN_WORDS and segments[i][-1] == '.') or sentence_length >= MAX_WORDS:
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



    def create_chunks(sself, entences, CHUNK_LENGTH, STRIDE):

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



    def parse_title_summary_results(self, results):
        out = []
        for e in results:
            e = e.replace('\n', '')
            if '|' in e:
                processed = {'title': e.split('|')[0],
                            'summary': e.split('|')[1][1:]
                            }
            elif ':' in e:
                processed = {'title': e.split(':')[0],
                            'summary': e.split(':')[1][1:]
                            }
            elif '-' in e:
                processed = {'title': e.split('-')[0],
                            'summary': e.split('-')[1][1:]
                            }
            else:
                processed = {'title': '',
                            'summary': e
                            }
            out.append(processed)
        return out
    

    def summarize_stage_1(self, chunks_text):
  
        print(f'Start time: {datetime.now()}')

        # Prompt to get title and summary for each chunk
        map_prompt_template = """Firstly, give the following text an informative title. Then, on a new line, write a 75-100 word summary of the following text:
        {text}

        Return your answer in the following format:
        Title | Summary...
        e.g. 
        Why Artificial Intelligence is Good | AI can make humans more productive by automating many repetitive processes.

        TITLE AND CONCISE SUMMARY:"""

        map_prompt = PromptTemplate(template=map_prompt_template, input_variables=["text"])

        # Define the LLMs
        map_llm = OpenAI(temperature=0, model_name = 'text-davinci-003')   ###REPLACE WITH LOCAL LLM
        map_llm_chain = LLMChain(llm = map_llm, prompt = map_prompt)
        map_llm_chain_input = [{'text': t} for t in chunks_text]
        # Run the input through the LLM chain (works in parallel)
        map_llm_chain_results = map_llm_chain.apply(map_llm_chain_input)

        stage_1_outputs = parse_title_summary_results([e['text'] for e in map_llm_chain_results])

        print(f'Stage 1 done time {datetime.now()}')

        return {
            'stage_1_outputs': stage_1_outputs
        }