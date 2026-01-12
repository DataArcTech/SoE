from transformers import AutoTokenizer, AutoModel
from crypto_entity import replace_base64_with_tokens
from anonymizer import analyze_text, anonymize, Entity_Analyzer
from utils import jdump
import os
from tqdm import tqdm

def load_synthesized_data(task_type, model_name):
    # data_path = f'data/dataset/raw/{task_type}_entigraph_{model_name}_crypto-txt_v1/'
    data_path = f'crypto/data/test_folder/'
    article_names_all = os.listdir(data_path)
    result = []
    for file in article_names_all:
        with open(data_path+file, "r", encoding="utf-8") as file:
            text = file.read()
            content = text.split('$$$@@@---')
            result.extend(content)
    return result

from multiprocessing import Manager, Process
from multiprocessing import Pool, Lock
from functools import partial
# file_lock = Lock()
NUM_THREADS = 2
def worker(idx, task_type, lang, lock, synth_data):
    num_lines = len(synth_data)
    num_workers = NUM_THREADS
    num = num_lines // num_workers
    start = idx*num
    if idx == num_workers - 1:
        num = num_lines - (num_workers-1)*num
    print(num,idx)
    cur_worker_encrypt_res = []
    result = []
    entity_analyzer = Entity_Analyzer('en',entities)
    
    for i in tqdm(range(num), desc=f"idx: {idx}"):
        sd = synth_data[start+i]
        entities = ['ENCRYPT']
        analyze_results = entity_analyzer.analyze_text(sd)
        try:
            new_ciphertext = anonymize(analyze_results, sd, lang, 'cipher_token')
            new_ciphertext = new_ciphertext.text
            result.append(new_ciphertext)
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
    
    for i in range(len(result)):
        text_dict = {}
        text_dict["text"] = result[i]
        result[i] = text_dict
    with lock:
        # with open(f'data/encrypt_{task_type}_qwen2.57B_et.json', 'a') as f:
        jdump(result, f'data/encrypt_{task_type}_qwen2.57B_et.json', 'a')

def ciphertext2newexp(task_type, synth_data, lang, parallel=False):
    result = []
    if parallel:
        with Pool(NUM_THREADS) as pool, Manager() as manager:
            shared_lock = manager.Lock()
            pool.map(partial(worker, task_type=task_type, lang=lang, lock=shared_lock, synth_data=synth_data), range(NUM_THREADS))
        print(len(result))  
    else:
        entity_analyzer = Entity_Analyzer('en',entities)

        for sd in tqdm(synth_data):
            entities = ['ENCRYPT']
            analyze_results = entity_analyzer.analyze_text(sd)
            try:
                new_ciphertext = anonymize(analyze_results, sd, lang, 'cipher_token')
                new_ciphertext = new_ciphertext.text
                result.append(new_ciphertext)
            except Exception as e:
                print(f"An unexpected error occurred: {e}")
        
        for i in range(len(result)):
            text_dict = {}
            text_dict["text"] = result[i]
            result[i] = text_dict
        with open(f'data/encrypt_{task_type}_qwen2.57B_et.json','w') as f:
            jdump(result, f)
    print('Finshed')

def token_extention(model_path, output_path):
    """
    model_path = Qwen/Qwen2.5-7B
    output_path = ckps/LLMs/Cipher-Qwen2.5-7B
    """
    # pick the model type
    tokenizer = AutoTokenizer.from_pretrained(model_path)
    model = AutoModel.from_pretrained(model_path)

    # add new characters
    new_tokens = ["ci_start", "ci_end"]

    # check if the tokens are already in the vocabulary
    new_tokens = set(new_tokens) - set(tokenizer.vocab.keys())
    print(new_tokens)

    print(len(tokenizer))
    # add the tokens to the tokenizer vocabulary
    num_added_tokens = tokenizer.add_tokens(list(new_tokens))
    print(f"Number of new tokens added: {num_added_tokens}")  # Output: 65
    print(len(tokenizer))

    # Resize the model embeddings to accommodate the new tokens
    model.resize_token_embeddings(len(tokenizer))
    model.save_pretrained(output_path)
    tokenizer.save_pretrained(output_path)

if __name__ == "__main__":
    # synth_data = load_synthesized_data('judge', 'deepseek-chat')
    # ciphertext2newexp('judge', synth_data, 'zh', True)
    output_path = "ckps/LLMs/Cipher-Qwen2.5-7B"
    tokenizer = AutoTokenizer.from_pretrained(output_path)
    ids = tokenizer.encode("人物_[ci_wci_Aci_Hci_8ci_nci_uci_6ci_bci_lci_aci_kci_lci_4ci_Nci_Rci_gci_Eci_tci_uci_rci_Cci_Aci_=ci_=]与被告江河公司之间不是借贷关系，原告不具有债权人资格，其主体不适格，应当依法驳回其起诉。被告江河公司与第三人宏立城公司之间的款项往来是本案的关键争议点之一。")
    print(ids)
    for i in ids:
        print(tokenizer.decode(i))
