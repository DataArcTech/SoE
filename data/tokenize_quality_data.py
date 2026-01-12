# Adopted from https://github.com/zitongyang/synthetic_continued_pretraining
"""
tokenize the original text or encrypted orginal text for CPT
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from typing import List
import numpy as np
from transformers import AutoTokenizer
import random
import glob
from tqdm import tqdm
from utils.io_utils import jload
from tasks.quality import QuALITY
from tasks.judge_zh import Judge
from crypto.anonymizer import analyze_text, anonymize, set_key, Entity_Analyzer
from crypto.crypto_entity import crypto_key

def get_tokenizer(tokenizer_model_name: str)-> AutoTokenizer:
    # loading tokenizer
    tokenizer = AutoTokenizer.from_pretrained(tokenizer_model_name, use_fast=True)
    tokenizer.model_max_length=2**20 # this is to hide the token_len>128K wraning
    return tokenizer

def encrypt_data(_data):
    set_key(crypto_key)
    lang = "en"
    converted_row = []
    detect_entities = ["PERSON"] 
    entity_analyzer = Entity_Analyzer(lang,entities)

    for text in _data:
        analyzer_results = entity_analyzer.analyze_text(text)
        result = anonymize(analyzer_results, text)
        converted_row.append(result.text)
    return converted_row

def tokenize_list(text_list: List[str], task_name='quality') -> List[int]:
    """
    Tokenize the text and return the tokenized text
    """
    random.shuffle(text_list)
    if task_name == "quality":
        tokenizer = get_tokenizer("meta-llama/Meta-Llama-3-8B")
    elif task_name == "judge":
        tokenizer = get_tokenizer("Qwen/Qwen2.5-7B")

    all_ids = []
    for text in tqdm(text_list):
        if text:
            ids = tokenizer.encode(text) # add_special_tokens=True to add BOS token
            ids.append(tokenizer.eos_token_id) # add the end of text token
            all_ids.extend(ids)
    return all_ids

def write_to_memmap_single(ids: List[int], filename: str):
    filename = f'data/dataset/bins/{filename}'
    print(f'Writing to {filename} with length {len(ids)}')
    dtype = np.int32
    ids_arr = np.array(ids, dtype=dtype)
    arr_len = len(ids_arr)
    arr = np.memmap(filename, dtype=dtype, mode='w+', shape=(arr_len,))
    arr[:] = ids_arr
    arr.flush()

def _glob_all_json(dir_name: str) -> List[str]:
    return glob.glob(f'{dir_name}/*.json') + glob.glob(f'{dir_name}/.*.json')


def _get_quality_data(document_indices, document_titles, encrypt = False):
    task = QuALITY('cur')
    documents = [task.documents[i] for i in document_indices]
    article_text = []
    for doc in documents:
        assert doc.title in document_titles
        article_text.append(doc.text) 
    print(type(article_text[0]))
    if encrypt:
        article_text = encrypt_data(article_text)
    return article_text

def tokenize_quality(model_name: str, encrypt = False):
    # model_name = model_name.split('/')[-1]
    cur_doc_titles = [
        ' Defining Decay Down',
        ' Fight Clubbed',
        ' It\'s Time To Keelhaul U-Haul!',
        ' My Father\'s Estate',
        '"Phone Me in Central Park"',
        '...After a Few Words...',
        '...And It Comes Out Here'
    ]
    article_ids = [0,1,3,4,5,6,7]
    quality = _get_quality_data(article_ids, cur_doc_titles, True)
    
    write_to_memmap_single(tokenize_list(quality), f'quality_all-entigraph{model_name}.bin')

def tokenize_judge(model_name: str, encrypt = False):
    task = Judge()
    documents = task.documents
    article_text = []
    for document in documents:
        if encrypt:
            content, encrypted_entity = document.get_encrypted_content(['person','loc'])
        else:
            content = document.content
        # print(type(content))
        article_text.extend(content) 
    write_to_memmap_single(tokenize_list(article_text,task_name="judge"), f'qwen-judge-entigraph{model_name}.bin')


if __name__ == '__main__':
    # Writing to data/dataset/bins/quality_all-graphgpt-4-turbo.bin with length 599385906 (599M)
    # tokenize_quality('gpt-4o-mini')
    tokenize_judge("deepseek-chat", encrypt=True)