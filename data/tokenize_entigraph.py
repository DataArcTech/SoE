# Adopted from https://github.com/zitongyang/synthetic_continued_pretraining

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

def get_tokenizer(tokenizer_model_name: str)-> AutoTokenizer:
    # loading tokenizer
    tokenizer = AutoTokenizer.from_pretrained(tokenizer_model_name, use_fast=True)
    tokenizer.model_max_length=2**20 # this is to hide the token_len>128K wraning
    return tokenizer

def tokenize_list(text_list: List[str], tokenizer_name: str) -> List[int]:
    """
    Tokenize the text and return the tokenized text
        "meta-llama/Meta-Llama-3-8B"
        "Qwen/Qwen2.5-7B"
    """
    random.shuffle(text_list)
    tokenizer = get_tokenizer(tokenizer_name)
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

def _get_quality_graph(model_name: str, task_type: str, data_type='txt', data_folder=None) -> List[str]:
    result = []
    if data_type == 'txt':
        data_path = f'data/dataset/raw/{task_type}_entigraph_{model_name}_crypto-pl-v1/' # revise the dir accordingly
        article_names_all = os.listdir(data_path)
        for file in article_names_all:
            with open(data_path+file, "r", encoding="utf-8") as file:
                text = file.read()
                content = text.split('$$$@@@---')
                result.extend(content)
    else:
        if data_folder is None:
            data_folder = f"data/dataset/raw/judge_weighted_edge_entigraph_deepseek-chat-v2/6" # revise the dir accordingly
        files = _glob_all_json(data_folder)
        for file in files:
            content = jload(file)
            result.extend(content[1:])
    return result

def load_original_content(task_type):
    if task_type == 'quality':
        task = QuALITY('cur')
    elif task_type == 'judge':
        task = Judge()
    result = []
    for document in task.documents:
        content = document.content
        result.extend([content])
    # jdump(result,f"data/dataset/raw/{task_type}_original_content.json")
    return result

def tokenize_quality_graph(model_name: str, task_type: str, tokenizer_name="meta-llama/Meta-Llama-3-8B", synthesized = True, data_type='json', data_folder=None):
    bin_sub_name = ''
    if synthesized:
        text = _get_quality_graph(model_name, task_type, data_type, data_folder)
        bin_sub_name = 'syn'
    else:
        text = load_original_content(task_type)
        bin_sub_name = 'ori'
    write_to_memmap_single(tokenize_list(text,tokenizer_name), f'{task_type}-{bin_sub_name}-all-entigraph{model_name}.bin')

if __name__ == '__main__':
    # Writing to data/dataset/bins/quality_all-graphgpt-4-turbo.bin with length 599385906 (599M)
    # meta-llama/Meta-Llama-3-8B Qwen/Qwen2.5-7B
    tokenizer_name = "Qwen/Qwen2.5-7B"
    data_folder = "data/dataset/raw/judge_weighted_edge_entigraph_deepseek-chat-v2/6"
    tokenize_quality_graph('deepseek-chat', 'judge', tokenizer_name=tokenizer_name, synthesized= True, data_type = 'json', data_folder = data_folder)