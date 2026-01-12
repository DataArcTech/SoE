# 1. is cipher entity decryptable
from utils.io_utils import jload, jdump
from crypto.crypto_entity import decrypt_aes_ecb
import re
class Cipher_Eval():
    def __init__(self, data_path, response_path):
        self.data_path = data_path
        self.response_path = response_path
        self.cipher_entities = []
        self.response_entities = []
        self.response_cipher_num = 0
        self.exceptional_num = 0
        self.name="中山市万驰照明有限公司与上海寻梦信息技术有限公司、农勇军侵害外观设计专利权纠纷一审民事判决书 受理于 上海知识产权法院"

    def load_cipher_entities(self):
        entities = []
        if 'txt' not in self.data_path:
            synt_data = jload(self.data_path)
            docs = synt_data[1:]
            docs.extend(synt_data[0])
        else:
            with open(self.data_path, 'r') as f:
                docs = f.readlines()

        for text in docs:
            custom_regex_pattern = r"_\[([A-Za-z0-9+/=]+)\]"
            matches = re.findall(custom_regex_pattern, text)
            for m in matches:
                if m not in entities:
                    entities.append(m)
        self.cipher_entities = entities
        # self.cipher_entities["entity"] = entities
        jdump(self.cipher_entities,f'outputs/exceptions/cipher_entity_all{self.name}.json')

    def load_reasoning_response(self):
        responses = jload(self.response_path)
        for resp in responses:
            if resp['title'] not in self.data_path:
                continue
            questions = resp["questions"]
            for ques in questions:
                attempt = ques["attempts"]
                for atte in attempt:
                    text = atte["reasoning"]
                    custom_regex_pattern = r"_\[([A-Za-z0-9+/=]+)\]"
                    matches = re.findall(custom_regex_pattern, text)
                    for m in matches:
                        self.response_cipher_num += 1
                        if m not in self.cipher_entities:
                            self.exceptional_num += 1
                        if m not in self.response_entities:
                            self.response_entities.append(m)
        print(f"Total number of cipher entites in response: {self.response_cipher_num}, exceptional number: {self.exceptional_num}")
        jdump(self.response_entities,f'outputs/exceptions/resp_entity_all{self.name}.json')
        
    
    def get_exceptional_cipher(self, crypto_key):
        exceptional_entities = []
        for e in self.response_entities:
            if e not in self.cipher_entities:
                try:
                    dec = decrypt_aes_ecb(crypto_key, e).decode()
                    e = e+' '+dec
                    exceptional_entities.append(e)
                except:
                    exceptional_entities.append('error: '+e)
        jdump(exceptional_entities,f'outputs/exceptions/except_entity_all{self.name}.json')

if __name__ == '__main__':
    from crypto.crypto_entity import crypto_key
    crypto_key = crypto_key

    data_path = "/data/entigraph_data/judge_entigraph_deepseek-chat_crypto-pl-v1/中山市万驰照明有限公司与上海寻梦信息技术有限公司、农勇军侵害外观设计专利权纠纷一审民事判决书 受理于 上海知识产权法院.json.txt"
    response_path = 'outputs/token-train_judgeqa-synthesis-non-context-encryption-qwen2.5_7b_encrypt_judge_pl_v1.json'
    eval = Cipher_Eval(data_path, response_path)
    eval.load_cipher_entities()
    eval.load_reasoning_response()
    eval.get_exceptional_cipher(crypto_key)