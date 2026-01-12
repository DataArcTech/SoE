"""
Entity number sampling
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from utils.io_utils import jload, jdump
import random


def get_num_question_sentences(sentences):
    for i, s in enumerate(sentences[1:]):
        if s[:6] != '### 关于':
            return i
        
    

def get_sentences_question(e, sentences):
    sub_content = f"### 关于{e}在"
    # print(sub_content)
    for i, sen in enumerate(sentences):
        if sub_content in sen:
            return sen
    return None

def get_sentences_relation(e1, e2, sentences, start = 0):
    sub_content = f"{e1}与{e2}的互动分析"
    sub_content2 = f"{e1}和{e2}的互动分析"
    # print(sub_content)
    for i, sen in enumerate(sentences[start:]):
        if sub_content in sen or sub_content2 in sen:
            return start+i, sen
    return start, None

def get_sentence_triple_relation(e1, e2, e3, sentences, start=0):
    sub_content = f"{e1}、{e2}与{e3}的互动分析"
    sub_content2 = f"{e1}、{e2}和{e3}的互动分析"
    # print(sub_content)
    for i, sen in enumerate(sentences[start:]):
        if sub_content in sen or sub_content2 in sen:
            return start+i, sen
    return start, None

def data_selection(data_path, ratio, save_path):
    with open(data_path, 'r') as f:
        synthesized_data = jload(f)
    entities = synthesized_data[0]
    k = int(ratio*len(entities))
    sythnesized_data = synthesized_data[1:]
    indices = [i for i in range(len(entities))]
    random.seed(0)
    indices = sorted(random.sample(indices, k=k))
    # print(indices)
    selected_entities = [entities[i] for i in indices]
    selected_data = []
    selected_data.append(selected_entities)
    print(data_path)
    print(f'Number of selected entities {len(selected_entities)}')

    offset = get_num_question_sentences(sythnesized_data)
    # entity questions
    for e in selected_entities:
        content = get_sentences_question(e, sythnesized_data[:offset+1])
        if content is not None:
            selected_data.append(content)
    num_questions = len(selected_data)-1
    print(f'Number of selected questions {num_questions}')

    
    # pairwise content
    pair_list = []
    # iterate over pairs of entities and generate relations
    for i in range(len(selected_entities)):
        for j in range(i+1, len(selected_entities)):
            pair = (selected_entities[i], selected_entities[j])
            pair_list.append(pair)
    start = 0
    for entity1, entity2 in pair_list:
        start, content = get_sentences_relation(entity1, entity2, sythnesized_data, 0)
        if content is not None:
            selected_data.append(content)
        # print(start, content)
    num_seleted_paris = len(selected_data)-1-num_questions
    print(f'Number of pairs {len(pair_list)}')
    print(f'Number of selected pairs {num_seleted_paris}')
    
    jdump(selected_data, save_path)

    ## triple content
    triple_list = []
    for i in range(len(selected_entities)):
        for j in range(i+1, len(selected_entities)):
            for k in range(j+1, len(selected_entities)):
                triple = (selected_entities[i], selected_entities[j], selected_entities[k])
                triple_list.append(triple)
    random.shuffle(triple_list)
    for entity1, entity2, entity3 in triple_list:
        _, content = get_sentence_triple_relation(entity1, entity2, entity3, sythnesized_data, start=start)
        if content is not None:
            selected_data.append(content)
    num_triplet = len(selected_data)- 1 - num_questions - num_seleted_paris
    print(f'Number of triplets {len(triple_list)}')
    print(f'Number of selected triplets {num_triplet}')

    jdump(selected_data, save_path)
    

def truncate_tokens(filenames, tokenizer_name, max_tokens):
    """
    Truncates text so that the total number of tokens does not exceed the specified max_tokens.
    Default percentage among articles based on NumEnti
    """
    from transformers import AutoTokenizer
    tokenizer = AutoTokenizer.from_pretrained(tokenizer_name, use_fast=True)
    data_list = []
    ratio_list = []
    ntoken_list = []
    for name in filenames:
        # load data from file
        data = jload(name)
        data_list.append(data)
        ratio_list.append(len(data[0]))

    ratio_list = [n/sum(ratio_list) for n in ratio_list]
    ntoken_list = [int(r*max_tokens) for r in ratio_list]

    for name, data, nt in zip(filenames, data_list, ntoken_list):
        n = 0
        end = 1
        for text in data[1:]:
            if text and n < nt:
                ids = tokenizer.encode(text) # add_special_tokens=True to add BOS token
                n += len(ids)
                end += 1
        jdump(data[:end], name)

    return

def entity_data_sampling(data_path, ratio, max_tokens=None, tokenizer_name=''):
    
    article_names_all = os.listdir(data_path + '1/')
    result = []
    filenames = []
    for file in article_names_all:
        file_path = data_path + '1/' + file
        save_path = f'{data_path}{ratio}/{file}'
        if not os.path.exists(save_path): 
            data_selection(file_path, ratio, save_path)
        if max_tokens:
            filenames.append(save_path)
    if max_tokens:
        truncate_tokens(filenames, tokenizer_name, max_tokens)

if __name__ == "__main__":
    data_path = f'data/dataset/raw/judge_entigraph_number_st_deepseek-chat/'
    ratio = 0.4
    entity_data_sampling(data_path, ratio, 20000000, tokenizer_name="ckpts/Qwen2.5-7B")