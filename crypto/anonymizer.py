import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from presidio_analyzer import AnalyzerEngine
from presidio_anonymizer import AnonymizerEngine
from presidio_anonymizer.entities import RecognizerResult, OperatorConfig
from presidio_analyzer.nlp_engine import NlpEngineProvider, NlpEngine
from crypto.predefined_recognizer import get_customed_recognizers
from crypto.crypto_entity import encrypt_aes_ecb, decrypt_aes_ecb, replace_base64_with_tokens
from faker import Faker
import pandas

crypto_key = ''
def set_key(key):
    global crypto_key
    crypto_key = key

# Set up the engine, loads the NLP module (spaCy model by default) and other PII recognizers
NLP_ENGINE="spacy"
NLP_MODELS=[
    {"lang_code": "en", "model_name": "en_core_web_lg"},
    {"lang_code": "zh", "model_name": "zh_core_web_lg"}
]
LANGUAGES_CONFIG_FILE = "crypto/language_config.yml"
PRINT_RESULT = False

def encrypt_pii(key, text, prefix):
    ciphertext = encrypt_aes_ecb(key, text)
    return f"{prefix}_["+ciphertext+"]"

def decrypt_pii(key, ciphertext):
    if ciphertext == 'PII':
        return ''
    prefix = ciphertext.split('_[')[0]
    offset = len(prefix) + 2
    ciphertext = ciphertext[offset:-1]
    text = decrypt_aes_ecb(key, ciphertext)
    return text.decode('utf-8')

def cipher_token_replace(ciphertext):
    if ciphertext == 'PII':
        return ''
    prefix = ciphertext.split('_[')[0]
    offset = len(prefix) + 2
    ciphertext = ciphertext[offset:-1]
    ciphertext = replace_base64_with_tokens(ciphertext)
    return prefix+'_['+ciphertext+']'

class Entity_Analyzer:
    def __init__(self, lang, entities):
        # nlp_configuration={
        #             "nlp_engine_name": NLP_ENGINE,
        #             "models": NLP_MODELS}
        self.entities = entities
        self.lang = lang
        self.analyzer = AnalyzerEngine(
            nlp_engine=NlpEngineProvider(
            conf_file=LANGUAGES_CONFIG_FILE
            ).create_engine(),
            supported_languages=[lang]
        )

        custom_recognizers = get_customed_recognizers(entities)
        for cr in custom_recognizers:
            self.analyzer.registry.add_recognizer(cr)
        
        if PRINT_RESULT:
            print("Registered Recognizers:")
            for recognizer in self.analyzer.registry.get_recognizers(language='zh',entities=['TRANS_PER']):
                print(f"- {recognizer.__class__.__name__}, Supported Entities: {recognizer.supported_entities}")

    def analyze_text(self, text):
        """
        Analyze the text, detect the locations of entities
        Entity types: ["PERSON","EMAIL_ADDRESS","LOCATION","PHONE_NUMBER", "CREDIT_CARD_CN"]
        """
        # Call analyzer to get results
        analyzer_results = self.analyzer.analyze(text=text,
                                entities=self.entities,
                                language=self.lang)

        if PRINT_RESULT:
            print(analyzer_results)
        return analyzer_results

def analyze_text(text, lang, entities):
    """
    Analyze the text, detect the locations of entities
    Entity types: ["PERSON","EMAIL_ADDRESS","LOCATION","PHONE_NUMBER", "CREDIT_CARD_CN"]
    """
    
    nlp_configuration={
                "nlp_engine_name": NLP_ENGINE,
                "models": NLP_MODELS}
    analyzer = AnalyzerEngine(
        nlp_engine=NlpEngineProvider(
        conf_file=LANGUAGES_CONFIG_FILE
        ).create_engine(),
        supported_languages=[lang]
    )

    custom_recognizers = get_customed_recognizers(entities)
    for cr in custom_recognizers:
        analyzer.registry.add_recognizer(cr)
    
    if PRINT_RESULT:
        print("Registered Recognizers:")
        for recognizer in analyzer.registry.get_recognizers(language='zh',entities=['TRANS_PER']):
            print(f"- {recognizer.__class__.__name__}, Supported Entities: {recognizer.supported_entities}")

    
    # Call analyzer to get results
    analyzer_results = analyzer.analyze(text=text,
                            entities=entities,
                            language=lang)
    for recog in analyzer.registry.recognizers:
        del recog
    del analyzer

    if PRINT_RESULT:
        print(analyzer_results)
    return analyzer_results

def get_operation_config(lang="zh_CN", type="encrypt"):
    """
    Operators to get the anonymization output, supported operators:
        - Replace: OperatorConfig(operator_name="replace", params={"new_value": "REPLACED_NAME"})
        - Mask: OperatorConfig(operator_name="mask", params={'chars_to_mask': 10, 'masking_char': '*', 'from_end': True})
        - Encrypt: OperatorConfig("encrypt", {"key": crypto_key})
    Faker - generating the fake information
    """
    if type == "encrypt":
        if lang=='zh_CN':
            prefix_dict = {
                "person": "人物",
                "loc": "地点",
                "date": "日期",
                "phone": "电话号码",
                "id": "身份证号码",
                "bank": "银行卡号码",
                'org': "机构"
            }
        elif lang == 'en':
            prefix_dict = {
                "person": "Person",
                "loc": "Location",
                "date": "Date",
                "phone": "Phone_number",
                "id": "ID_number",
                "bank": "Bank_card"
            }
        operators={
            "PERSON": OperatorConfig("custom", {"lambda": lambda x: encrypt_pii(crypto_key,x,prefix_dict["person"])}),
            "LOCATION": OperatorConfig("custom", {"lambda": lambda x: encrypt_pii(crypto_key,x,prefix_dict["loc"])}),
            "ORGANIZATION": OperatorConfig("custom", {"lambda": lambda x: encrypt_pii(crypto_key,x,prefix_dict["org"])}),
            "CN_DATE": OperatorConfig("custom", {"lambda": lambda x: encrypt_pii(crypto_key,x,prefix_dict["date"])}),
            "CN_PHONE_NUMB": OperatorConfig("custom", {"lambda": lambda x: encrypt_pii(crypto_key,x,prefix_dict["phone"])}),
            "CN_ID_CARD_NUMB": OperatorConfig("custom", {"lambda": lambda x: encrypt_pii(crypto_key,x,prefix_dict["id"])}),
            "CN_CREDIT_CARD": OperatorConfig("custom", {"lambda": lambda x: encrypt_pii(crypto_key,x,prefix_dict["bank"])}),
            "DEFAULT": OperatorConfig(operator_name="mask", 
                                        params={'chars_to_mask': 10, 
                                                'masking_char': '*',
                                                'from_end': False})
        }
    elif type == "decrypt":
        operators={
            "ENCRYPT_PERSON": OperatorConfig("custom", {"lambda": lambda x: decrypt_pii(crypto_key,x)}),
            "ENCRYPT": OperatorConfig("custom", {"lambda": lambda x: decrypt_pii(crypto_key,x)}),
            "DEFAULT": OperatorConfig(operator_name="mask", 
                            params={'chars_to_mask': 10, 
                                    'masking_char': '*',
                                    'from_end': False}),}
    elif type == "cipher_token":
        operators={
            "ENCRYPT": OperatorConfig("custom", {"lambda": lambda x: cipher_token_replace(x)}),
            "DEFAULT": OperatorConfig(operator_name="mask", 
                            params={'chars_to_mask': 10, 
                                    'masking_char': '*',
                                    'from_end': False}),}
    elif type == "fake":
        fake = Faker(lang)
        operators = {
            "PERSON": OperatorConfig("custom", {"lambda": lambda x: fake.name()}),
            "PHONE_NUMBER": OperatorConfig("custom", {"lambda": lambda x: fake.phone_number()}),
            "EMAIL_ADDRESS": OperatorConfig("custom", {"lambda": lambda x: fake.email()}),
            "LOCATION": OperatorConfig("custom", {"lambda": lambda x: fake.address()}),
            "CREDIT_CARD_CN": OperatorConfig("custom", {"lambda": lambda x: fake.credit_card_number("visa16")}),
            "DEFAULT": OperatorConfig(operator_name="mask", 
                                    params={'chars_to_mask': 10, 
                                            'masking_char': '*',
                                            'from_end': False}),
        }
    else:
        raise  NotImplementedError(f"The {type} type not supported yet")
    return operators

def anonymize(analyzer_results, text, lang = "zh_CN", type = "encrypt"):
        
    # Initialize the engine:
    engine = AnonymizerEngine()

    # Invoke the anonymize function with the text, 
    # analyzer results (potentially coming from presidio-analyzer) and
    operators = get_operation_config(lang, type)
    if PRINT_RESULT:
        print(f'Original text: {text}')
    result = engine.anonymize(
        text=text,
        analyzer_results=analyzer_results,
        operators=operators,
    )
    if PRINT_RESULT:
        print(f"Coverted text: {result.text}")
    del engine
    return result

if __name__ == "__main__":
    table_rows = []
    # write_file = False
    with open("crypto/data/pii.csv", "r") as f:
        table_rows = f.readlines()
    lang = "zh"
    converted_row = []
    for text in table_rows[1:]:
        analyzer_results = analyze_text(text, lang, ["PERSON"])
        print(analyzer_results)
        print(type(analyzer_results[0]))
        result = anonymize(analyzer_results, text)
        converted_row.append(result.text)
    
    with open("crypto/data/anony_pii.csv","w") as f:
        f.write(table_rows[0])
        for row in converted_row:
            f.write(row)
    
    org_df = pandas.read_csv("crypto/data/pii.csv")
    converted_df = pandas.read_csv("crypto/data/anony_pii.csv")
    print(org_df.head())
    print(converted_df.head())
    