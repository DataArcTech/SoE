import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from crypto.anonymizer import analyze_text, anonymize, set_key, Entity_Analyzer
import argparse
import os
from crypto.utils import jdump, jload
from tqdm import tqdm
from crypto.predefined_recognizer.transformer_recognizer_zh import TransformerNERRecognizer
from presidio_analyzer import RecognizerResult

parser = argparse.ArgumentParser(description='Short sample app')
parser.add_argument('--start', help="start point", type=int, required=True)
parser.add_argument('--end', help="end point", type=int, required=True)
parser.add_argument('--lang', help="language", type=str, default='en')

NUM_THREADS = 16

def recognize_entities(synth_data, entities):
    recog = TransformerNERRecognizer()
    results = []
    for text in tqdm(synth_data[1:]):
        text = text.replace("\\n",'\n')
        ts = [line + '\n' for line in text.split('\n')]
        final_result = []
        for t in ts:
            cur_result = recog.analyze(t,entities)
            final_result.append(cur_result)
        results.append(final_result)
    return results

def pre_recognize_launcher_zh(article_path, article_names, entities):
    # ["TRANS_PER","TRANS_LOC","CN_DATE","CN_PHONE_NUMB","CN_ID_CARD_NUMB","CN_CREDIT_CARD"]
    for article_name in article_names:
        # print(article_name)
        # article_name = 'crypto/data/test.json'
        # if os.path.isfile("outputs/"+ "analyzed_" + article_name):
        #     return
        if 'json' in article_name:
            with open(article_path+article_name, "r", encoding='utf-8') as f:
                # synth_data = f.readlines() 
                synth_data = jload(f)
        elif 'txt' in article_name:
            with open(article_path+article_name, "r", encoding='utf-8') as f:
                synth_data = f.readlines()
                synth_data = [""]+synth_data
        analyzed_results = recognize_entities(synth_data, entities)
        output_path = "outputs/"+ "analyzed_" + article_name
        with open(output_path,"w") as f:
            jdump(analyzed_results,f)

def get_recog_results(recog_results):
    coverted_results = []
    for recog_string in recog_results:
        if isinstance(recog_string, RecognizerResult):
            return recog_results
        dict_items = recog_string.split(", ")
        result_dict = {}

        for item in dict_items:
            key, value= item.split(": ")
            # value = item.split(": ")[1]
            result_dict[key] = value
        result_dict['start'] = int(result_dict['start'])
        result_dict['end'] = int(result_dict['end'])
        result_dict['score'] = float(result_dict['end'])

        coverted_results.append(RecognizerResult(
                        entity_type=result_dict['type'],
                        start=result_dict['start'],
                        end=result_dict['end'],
                        score=result_dict['score']
                    ))
    return coverted_results
        

from multiprocessing import Manager, Process
from multiprocessing import Pool, Lock
from functools import partial
# file_lock = Lock()
def worker(idx, article_name, lock, analyzed_results, synth_data):
    num_lines = len(synth_data)
    num_workers = NUM_THREADS
    num = num_lines // num_workers
    start = idx*num
    if idx == num_workers - 1:
        num = num_lines - (num_workers-1)*num
    # cur_worker_encrypt_res = []
    detect_entities = ["CN_DATE","CN_PHONE_NUMB","CN_ID_CARD_NUMB","CN_CREDIT_CARD"]
    entity_analyzer = Entity_Analyzer(lang,detect_entities)
    
    for i in tqdm(range(num), desc=f"idx: {idx}"):
        cur_r = analyzed_results[start+i]
        text = synth_data[start+i]
        text = text.replace("\\n",'\n')
        ts = [line + '\n' for line in text.split('\n')]
        final_result = ''
        for t, r in zip(ts, cur_r):
            r = get_recog_results(r)
            if len(detect_entities):
                analyzer_results = entity_analyzer.analyze_text(t)
            else:
                analyzer_results = []
            analyzer_results.extend(r)
            result = anonymize(analyzer_results, t, lang = "zh_CN", type = "encrypt")
            final_result = final_result + result.text
        with lock:
            with open(f'{article_name}.txt', 'a') as f:
                final_result = '$$$@@@---'+final_result
                f.write(final_result)
                f.flush()

        # cur_worker_encrypt_res.append(final_result)
    with lock:
        print(f'Worker {idx} has processed and put result in queue')
    # return cur_worker_encrypt_res

def recog_encrypt_content_zh(content, analyzed_results, lang, entities, tasks=None, task_id=None, list_filter=None):
    converted_row = []
    
    detect_entities = entities
    encrypt_entity = False
    if not encrypt_entity:
        content = [""] + content
    
    count = 1
    total = len(content) - 1
    entity_analyzer = Entity_Analyzer(lang,detect_entities)

    for text, cur_r in zip(content[1:], analyzed_results):
        process_info = f'Encryption {count} out of {total}...'
        print(process_info)
        if tasks:
            tasks[task_id]["status"] = process_info
            tasks[task_id]['progress'] = count/total
        count += 1
        text = text.replace("\\n",'\n')
        ts = [line + '\n' for line in text.split('\n')]
        final_result = ''
        for t, r in zip(ts, cur_r):
            r = get_recog_results(r)
            if len(detect_entities):
                analyzer_results = entity_analyzer.analyze_text(t)
            else:
                analyzer_results = []
            # print(list_filter)
            if list_filter is not None:
                r = [r_info for r_info in r if t[r_info.start:r_info.end] in list_filter ]
            analyzer_results.extend(r)
            result = anonymize(analyzer_results, t, lang = "zh_CN", type = "encrypt")
            final_result = final_result + result.text
        converted_row.append(final_result)
    return converted_row

def recog_encrypt_zh(article_path, article_names, lang, entities, parallel=False, tasks=None, task_id=None):
    all_result = []
    for article_name in article_names:
        print(article_name)
        # article_name = 'crypto/data/test.json'
        with open(f"outputs/analyzed_{article_name}", "r") as f:
            # synth_data = f.readlines() 
            analyzed_results = jload(f)
        if 'json' in article_name:
            with open(article_path+article_name, "r") as f:
                synth_data = jload(f)
        elif 'txt' in article_name:
            with open(article_path+article_name, "r") as f:
                synth_data = f.readlines() 
        
        detect_entities = ["TRANS_PER","TRANS_LOC","CN_DATE","CN_PHONE_NUMB","CN_ID_CARD_NUMB","CN_CREDIT_CARD"]
        converted_row = []
        
        detect_entities = entities
        encrypt_entity = False
        if not encrypt_entity:
            synth_data = [""] + synth_data
        if not parallel:
            converted_row = recog_encrypt_content_zh(synth_data[1:], analyzed_results, lang, entities, tasks=tasks, task_id=task_id)
            
            output_path = 'outputs/' + "encrypt_" + article_name
            with open(output_path,"w") as f:
                jdump(converted_row,f)
            all_result.append(converted_row)
        else:
            text_syth = synth_data[1:]
            
            with Pool(NUM_THREADS) as pool, Manager() as manager:
                shared_lock = manager.Lock()
                pool.map(partial(worker, article_name=article_name, lock=shared_lock, analyzed_results=analyzed_results, synth_data=text_syth), range(NUM_THREADS))
             
            output_path = "outputs/" + article_name
    return all_result

def recog_encrypt_content_en(content, analyzed_results, lang, entities):
    converted_row = []
    content = [""] + content
    total = len(content) - 1
    count = 0
    entity_analyzer = Entity_Analyzer(lang,entities)
    
    for text in tqdm(content[1:]):
        print(f"Encryption {count} out of {total}...")
        count += 1
        text = text.replace("\\n",'\n')

        ts = [line + '\n' for line in text.split('\n')]
        final_result = ''
        for t in ts:
            analyzer_results = entity_analyzer(t, lang, entities)
            result = anonymize(analyzer_results, t, lang = lang, type = "encrypt")
            final_result = final_result + result.text
        
        converted_row.append(final_result)
    return converted_row

def recog_encrypt_en(article_path, article_names, lang, cur_entities):
    for article_name in article_names:
        print(article_name)
        # article_name = 'crypto/data/test.json'
        
        if 'json' in article_name:
            with open(article_path+article_name, "r") as f:
                # synth_data = f.readlines() 
                synth_data = jload(f)
        elif 'txt' in article_name:
            with open(article_path+article_name, "r") as f:
                synth_data = f.readlines()
        converted_row = []
        total = len(synth_data) - 1
        count = 0
        entity_analyzer = Entity_Analyzer(lang,cur_entities)

        for text in tqdm(synth_data[1:]):
            print(f"Encryption {count} out of {total}...")
            count += 1
            text = text.replace("\\n",'\n')

            ts = [line + '\n' for line in text.split('\n')]
            final_result = ''
            for t in ts:
                analyzer_results = entity_analyzer.analyze_text(t)
                result = anonymize(analyzer_results, t, lang = lang, type = "encrypt")
                final_result = final_result + result.text
            
            converted_row.append(final_result)
        
        output_path = "outputs/"+ "encrypt_" + article_name

        with open(output_path,"w") as f:
            jdump(converted_row,f)

def decrypt_entities(entity_list, key, lang):
    if key is not None:
        set_key(key)
    entities = ['ENCRYPT']
    entity_analyzer = Entity_Analyzer('en',entities)
    converted_row = []
    for text in entity_list:
        analyze_results = entity_analyzer.analyze_text(text)
        try:
            result = anonymize(analyze_results, text, lang, 'decrypt')
            result = result.text
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
        converted_row.append(result)
    return converted_row

def encryption_pipeline(article_path, article_names, lang, entities, parallel=False, content=None, key=None, tasks=None, task_id=None, list_filter=None):
    if key is not None:
        set_key(key)
    # ["TRANS_PER","TRANS_LOC","CN_DATE","CN_PHONE_NUMB","CN_ID_CARD_NUMB","CN_CREDIT_CARD"]
    if lang == 'zh':
        recog_name_dict = {
            "person": 'TRANS_PER',
            "loc": "TRANS_LOC",
            "date": "CN_DATE",
            "phone": "CN_PHONE_NUMB",
            "id": "CN_ID_CARD_NUMB",
            "bank": "CN_CREDIT_CARD"
        }
        cur_entities = [recog_name_dict[x] for x in entities]
        # if 'TRANS_PER' in cur_entities:
        #     cur_entities.remove('TRANS_PER')
        # if 'TRANS_LOC' in cur_entities:
        #     cur_entities.remove('TRANS_LOC')
        # print(cur_entities)
        if content:
            analyzed_results = recognize_entities([""] + content, cur_entities)
            encrypted_results = recog_encrypt_content_zh(content, analyzed_results, lang, cur_entities, list_filter=list_filter)
        else:
            pre_recognize_launcher_zh(article_path, article_names, cur_entities)
            encrypted_results = recog_encrypt_zh(article_path, article_names, lang, cur_entities, parallel=parallel, tasks=tasks, task_id=task_id)
    elif lang == 'en':
        recog_name_dict = {
            "person": 'PERSON',
            "loc": "LOCATION",
            "date": "DATE_TIME",
            "phone": "PHONE_NUMBER",
            "email": "EMAIL_ADDRESS",
            "bank": "CREDIT_CARD"
        }
        cur_entities = [recog_name_dict[x] for x in entities]
        if content:
            encrypted_results = recog_encrypt_content_en(content, analyzed_results, lang, entities)
        else:
            encrypted_results = recog_encrypt_en(article_path, article_names, lang, cur_entities)
    print("Finished.")
    return encrypted_results

def decryption_pipeline(article_path, article_names, lang, parallel=False, content=None, key=None, tasks=None, task_id=None):
    if key is not None:
        set_key(key)
    entities = ['ENCRYPT']
    all_result = []
    for article_name in article_names:
        print(article_name)
        # article_name = 'crypto/data/test.json'
        converted_row = []
        if 'json' in article_name:
            with open(article_path+article_name, "r") as f:
                # synth_data = f.readlines() 
                synth_data = jload(f)
        elif 'txt' in article_name:
            with open(article_path+article_name, "r") as f:
                synth_data = f.readlines()
        total = len(synth_data)
        count = 1
        entity_analyzer = Entity_Analyzer('en',entities)

        for text in synth_data:
            process_info = f"Decryption {count} out of {total}..."
            print(process_info)
            # print(tasks)
            if tasks:
                tasks[task_id]["status"] = process_info
                tasks[task_id]['progress'] = count/total
            count += 1
            analyze_results = entity_analyzer.analyze_text(text)
            try:
                result = anonymize(analyze_results, text, lang, 'decrypt')
                result = result.text
            except Exception as e:
                print(f"An unexpected error occurred: {e}")
                result = f'(Cannot be decrypted, ciphertext is ) {text}'
            converted_row.append(result)
        all_result.append(converted_row)
    print("Finshed.")
    return all_result

if __name__ == "__main__":
    from crypto_entity import crypto_key

    set_key(crypto_key)
    article_path = "data/dataset/raw/judge_entigraph_deepseek-chat/"
    article_path = "crypto/data/test_folder/"
    article_names_all = os.listdir(article_path)
    entities = ["person","location","date"]
    args = parser.parse_args()
    # article_names = article_names_all[args.start:args.end]
    lang = args.lang
    # encryption_pipeline(article_path, article_names, lang, entities, False)
    article_path = "data/dataset/raw/judge_synthesis2encryption_counterpart/"
    article_names_all = os.listdir(article_path)
    decryption_pipeline(article_path, article_names_all, lang, False, None, crypto_key)
    # if False:
    #     recognize_launcher(article_path, article_names, lang)
    # else:
    #     recog_encrypt(article_path, article_names, True)