import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__))+'/..')
import torch
from transformers import AutoModelForTokenClassification,AutoTokenizer,pipeline
from presidio_analyzer import (
    RecognizerResult,
    EntityRecognizer,
    AnalysisExplanation,
)

class TransformerNERRecognizer(EntityRecognizer):
    def __init__(self):
        super().__init__(supported_entities=["TRANS_PER", "TRANS_LOC"], supported_language="zh")
        model_path = 'xiaxy/elastic-bert-chinese-ner'
        self.model = AutoModelForTokenClassification.from_pretrained(model_path)
        self.tokenizer = AutoTokenizer.from_pretrained(model_path)
        device = 0 if torch.cuda.is_available() else -1  # 0 for GPU, -1 for CPU
        self.ner_pipeline = pipeline('ner', model=self.model, tokenizer=self.tokenizer, aggregation_strategy="simple", device=device)
        
        # Load your transformer model here (e.g., using Hugging Face Transformers)
    
    def analyze(self, text, entities=None, **kwargs):
        results = []
        detected_list = []

        if entities is None:
            entities = ['TRANS_PER','TRANS_LOC']
        if 'TRANS_PER' in entities:
            detected_list.append("PER")
        if 'TRANS_LOC' in entities:
            detected_list.append("LOC")
        ner_results = self.ner_pipeline(text)
        full_type = {'PER':'PERSON', 'LOC':'LOCATION'}
        for ner in ner_results:
            entity_type = ner['entity_group']
            if entity_type in detected_list:
                results.append(
                    RecognizerResult(
                        entity_type=full_type[entity_type],
                        start=ner['start'],
                        end=ner['end'],
                        score=ner['score']
                    )
                )
        return results
    
    def __del__(self):
        del self.model
        del self.tokenizer
        del self.ner_pipeline

class TransformerNERRecognizerORG(EntityRecognizer):
    def __init__(self):
        super().__init__(supported_entities=["TRANS_PER", "TRANS_LOC", "ORGANIZATION"], supported_language="zh")
        model_path = 'uer/roberta-base-finetuned-cluener2020-chinese'
        self.model = AutoModelForTokenClassification.from_pretrained(model_path)
        self.tokenizer = AutoTokenizer.from_pretrained(model_path)
        device = 0 if torch.cuda.is_available() else -1  # 0 for GPU, -1 for CPU
        self.ner_pipeline = pipeline('ner', model=self.model, tokenizer=self.tokenizer,
                 aggregation_strategy="simple", device=device)
        
        # Load your transformer model here (e.g., using Hugging Face Transformers)
    
    def analyze(self, text, entities=None, **kwargs):
        results = []
        detected_list = []
        if entities is None:
            entities = ['TRANS_PER','TRANS_LOC','TRANS_ORG']
        if 'TRANS_PER' in entities:
            detected_list.append("name")
        if 'TRANS_LOC' in entities:
            detected_list.append("address")
        if 'TRANS_ORG' in entities:
            detected_list.append("organization")
        encoded_inputs = self.tokenizer(
            text,
            truncation=True,
            max_length=510,
            return_tensors="pt"
        )
        ner_results = self.ner_pipeline(self.tokenizer.decode(encoded_inputs["input_ids"][0]))
        full_type = {'name':'PERSON', 'address':'LOCATION', 'organization': 'ORGANIZATION'}
        
        for ner in ner_results:
            entity_type = ner['entity_group']
            if entity_type in detected_list:
                results.append(
                    RecognizerResult(
                        entity_type=full_type[entity_type],
                        start=ner['start'],
                        end=ner['end'],
                        score=ner['score']
                    )
                )
        return results

def get_transformer_ner():
    transformer_recognizer = TransformerNERRecognizer()
    return transformer_recognizer

def get_transformer_ner_org():
    transformer_recognizer = TransformerNERRecognizerORG()
    return transformer_recognizer

if __name__ == "__main__":
    # 'uer/roberta-base-finetuned-cluener2020-chinese' leonadase/bert-base-chinese-finetuned-ner xiaxy/elastic-bert-chinese-ner
    model_path = 'uer/roberta-base-finetuned-cluener2020-chinese'
    model = AutoModelForTokenClassification.from_pretrained(model_path)
    tokenizer = AutoTokenizer.from_pretrained(model_path)
    ner = pipeline('ner', model=model, tokenizer=tokenizer, aggregation_strategy="simple")
    r = ner(["郭健是一位博士，现任粤港澳大湾区数字经济研究院的署理院长，位于深圳市福田区。他负责公司的战略规划、融资和团队建设，并参与技术路线规划以推动公司的业务发展和市场落地。"])
    for r in r:
        print('--------------')
        print(r)
    
    from presidio_analyzer import AnalyzerEngine, RecognizerRegistry
    from presidio_analyzer.nlp_engine import NlpEngineProvider
    lang = 'zh'
    analyzer = AnalyzerEngine(
        nlp_engine=NlpEngineProvider(
        conf_file='crypto/language_config.yml'
        ).create_engine(),
        supported_languages=[lang]
    )

    # Add your transformer-based recognizer to the engine
    transformer_recognizer = TransformerNERRecognizerORG()
    analyzer.registry.add_recognizer(transformer_recognizer)
    # analyzer.registry.remove_recognizer("SpacyRecognizer")

    print("Registered Recognizers:")
    for recognizer in analyzer.registry.get_recognizers(language='zh',entities=['TRANS_PER']):
        print(f"- {recognizer.__class__.__name__}, Supported Entities: {recognizer.supported_entities}")

    # Now you can use the analyzer to recognize entities
    text = "郭健是一位博士，现任粤港澳大湾区数字经济研究院的署理院长，位于深圳市福田区。他负责公司的战略规划、融资和团队建设，并参与技术路线规划以推动公司的业务发展和市场落地。"
    results = analyzer.analyze(text=text, entities= ['TRANS_PER','TRANS_LOC','ORGANIZATION'], language="zh")

    print(results)
