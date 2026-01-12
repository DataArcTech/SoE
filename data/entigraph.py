# Ref: https://github.com/zitongyang/synthetic_continued_pretraining

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
import json
from tqdm import tqdm
import re
from inference.devapi import gptqa
from utils.io_utils import jload, jdump
from tasks.quality import QuALITY
from tasks.judge_zh import Judge
from utils.io_utils import set_openai_key
import random


def generate_entities(document_content: str,
                      system_message: str,
                      openai_model: str):
    prompt = f"""
    ### Document Content:
    {document_content}
    """
    can_read_entities = None
    while not can_read_entities:
        try:
            completion = gptqa(prompt,
                               openai_model,
                               system_message,
                               json_format=True)
            response = json.loads(completion)
            can_read_entities = response['entities']
        except Exception as e:
            print(f"Failed to generate entities: {str(e)}")
    return response


def generate_entity_specific_questions(document_content: str,
                                       entity: str,
                                       system_message: str,
                                       openai_model: str):
    prompt = f"""
    ### Document Content:
    {document_content}
    ### Entities:
    - {entity}
    """
    try:
        completion = gptqa(prompt,
                        openai_model,
                        system_message)
    except Exception as e:
        print(f"Failed to generate questions: {str(e)}")
        print(f"Entity: {entity}")
        completion = None
        print("--------------------------------------------")
    return completion


def generate_two_entity_relations(document_content: str,
                                  entity1: str,
                                  entity2: str,
                                  system_message: str,
                                  openai_model: str):
    prompt = f"""
    ### Document Content:
    {document_content}
    ### Entities:
    - {entity1}
    - {entity2}
    """
    try:
        completion = gptqa(prompt,
                        openai_model,
                        system_message)
    except Exception as e:
        print(f"Failed to generate pairwise relation: {str(e)}")
        print(f"Entities: {entity1}, {entity2}")
        completion = None
        print("--------------------------------------------")
    return completion

def generate_three_entity_relations(document_content: str,
                                    entity1: str,
                                    entity2: str,
                                    entity3: str,
                                    system_message: str,
                                    openai_model: str):
    prompt = f"""
    ### Document Content:
    {document_content}
    ### Entities:
    - {entity1}
    - {entity2}
    - {entity3}
    """
    try:
        completion = gptqa(prompt,
                        openai_model,
                        system_message)
    except Exception as e:
        print(f"Failed to generate triple relation: {str(e)}")
        print(f"Entities: {entity1}, {entity2}, {entity3}")
        completion = None
        print("--------------------------------------------")
    return completion

def generate_k_entity_relations(document_content: str,
                                    entity_list,
                                    system_message: str,
                                    openai_model: str,
                                    lang = 'en'):
    entities_str = ""
    for e in entity_list:
        entities_str = entities_str + "- "+e+'\n'
    if lang=='en':
        prompt = f"""
        ### Document Content:
        {document_content}
        ### Entities:
        {entities_str}
        """
    elif lang=='zh':
        prompt = f"""
        ### 文件内容:
        {document_content}
        ### 实体:
        {entities_str}
        """
    print(entities_str)
    try:
        completion = gptqa(prompt,
                        openai_model,
                        system_message)
    except Exception as e:
        print(f"Failed to generate relations: {str(e)}")
        print(f"Entities: {entity_list}")
        completion = None
        print("--------------------------------------------")
    return completion

def generate_synthetic_data_for_document(document_index: str, model_name: str, task_type: str, encryption: bool):
    random.seed(42)
    set_openai_key()
    if task_type == 'quality':
        task = QuALITY('all')
        lang ='en'
    elif task_type == 'judge':
        task = Judge()
        lang ='zh'
    print(len(task.documents))
    document = task.documents[document_index]
    print(f"Generating synthetic data for {document_index} article {document.uid}")
    output_path = f'data/dataset/raw/{task_type}_entigraph_{model_name}/{document.uid}.json'



    if os.path.exists(output_path):
        output = jload(output_path)
    else:
        output = [[]]

    content = document.content
    if encryption:
        # ['person','loc','date','phone','id','bank']
        content, encrypted_entity = document.get_encrypted_content(['person','loc','date','phone','id','bank'])
    print('Generating Entities...')
    # first check if entities are already generated
    if isinstance(output[0], list) and len(output[0])>0:
        entities = output[0]
    else:
        entities = generate_entities(
            content,
            task.openai_system_generate_entities,
            model_name)
        pii_entities=document.get_pii_entities(['person','loc','date','phone','id','bank'])

        output[0] = entities['entities']
        if encryption:
            output[0] = [ent for ent in output[0] if ent not in pii_entities]
            output[0].extend(encrypted_entity)
            output[0] = list(set(output[0]))
        else:
            output[0].extend(pii_entities)
            output[0] = list(set(output[0]))
            output.append(entities['summary'])
        jdump(output, output_path) # default encoding: UTF-8
        entities = output[0]
    print('Generating Entity Questions...')
    # iterate over entities and generate questions
    for entity in tqdm(entities):
        # if _entity_already_generated(entity, output):
        #     continue
        response = generate_entity_specific_questions(
            content, entity,
            task.openai_system_generate_entity_specific_questions,
            model_name)
        if response:
            output.append(response)
        jdump(output, output_path) # default encoding: UTF-8
    pair_list = []
    print('Generating Pairwise Relations...')
    # iterate over pairs of entities and generate relations
    for i in range(len(entities)):
        for j in range(i+1, len(entities)):
            pair = (entities[i], entities[j])
            pair_list.append(pair)
    
    for entity1, entity2 in tqdm(pair_list):
        # if _pair_already_generated(entity1, entity2, output):
        #     continue
        response = generate_two_entity_relations(
            content, entity1, entity2,
            task.openai_system_generate_two_entity_relations,
            model_name)
        if response:
            output.append(response)
        jdump(output, output_path) # default encoding: UTF-8
    print("Finished...")
if __name__ == '__main__':
    # seq 0 264 | xargs -P 265 -I {} sh -c 'python data/entigraph.py {} > data/dataset/log/log_gpt4turbo_{}.txt 2>&1'
    
    model_name = "deepseek-chat"
    task_type = "judge"
    encryption = False # Synthesize then encrypt
    document_index = int(sys.argv[1])
    generate_synthetic_data_for_document(document_index, model_name, task_type, encryption)