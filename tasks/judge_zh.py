from collections import Counter
from typing import List, Dict, Optional
import re
import numpy as np

from tasks.task_abc import Question, Document, Task
from utils.io_utils import jload_list, jload
from utils.prompt_utils import format_name, uncapitalize_first, second_last_character
# from utils.prompt_utils_zh import second_last_character
from utils.prompt_utils_zh import (
                                OPENAI_API_SYSTEM_JUDGE_GENERATE_ENTITIES,
                                OPENAI_API_SYSTEM_JUDGE_GENERATE_ENTITY_SPECIFIC_QUESTIONS,
                                OPENAI_API_SYSTEM_JUDGE_GENERATE_TWO_ENTITIES_CONNECTION_SCORE,
                                OPENAI_API_SYSTEM_JUDGE_GENERATE_TWO_ENTITY_RELATIONS,
                                OPENAI_API_SYSTEM_JUDGE_GENERATE_THREE_ENTITY_RELATIONS,
                                OPENAI_API_SYSTEM_JUDGE_GENERATE_K_ENTITY_RELATIONS,
                                JUDGE_FEW_SHOT_COT_PROMPT,
                                JUDGE_CHECK_ENTITY_LIST_PROMPT)

class JudgeQuestion(Question):
    def __init__(self,
                 statement: str,
                 options: List[str],
                 answer: str,
                 ishard: bool,
                 attempts: List[Dict]=[dict()],
                 **kwargs):
        statement_dict = dict(content=statement, options=options)
        super().__init__(statement_dict, answer, attempts)
        self.ishard = ishard

    def _formatted_choice(self):
        formatted = ""
        for i, option in enumerate(self.statement['options']):
            # Convert 0, 1, 2, 3, ... to A, B, C, D, ...
            letter = chr(65 + i)
            formatted += f"{letter}. {option}\n"
        return formatted

    def prompt(
            self,
            document_context: Optional[str],
            add_thought_process: bool,
            sep_after_question: str
    ):
        formatted = "### 问题\n"

        if document_context is None:
            formatted += f"{self.statement['content']} 仅有一个正确选项。{sep_after_question}"
        else:
            formatted += f"{document_context} {uncapitalize_first(self.statement['content'])} 仅有一个正确选项。{sep_after_question}"

        formatted += f"### 选项\n"
        formatted += self._formatted_choice()

        if add_thought_process:
            if sep_after_question == '\n\n':
                formatted += "\n"

            formatted += "### 思路及答案\n"
            formatted += "思路: "

        return formatted

    def llama_parse_answer(self, raw_output: str):
        if raw_output is None:
            return dict()
        else:
            answer_index = second_last_character(raw_output)
            if answer_index is not None:
                answer_content = self.statement['options'][answer_index]
            else:
                answer_content = None
            return dict(reasoning=raw_output,
                        answer_index=answer_index,
                        answer_content=answer_content)

    def _iscorrect(self, attempt: Dict):
        return self.answer == chr(attempt['answer_index'] + 65)

    def iscorrect(self, attempt_index: int = 0):
        return self._iscorrect(self.attempts[attempt_index])

    def asdict(self):
        return dict(
            statement=self.statement['content'],
            options=self.statement['options'],
            answer=self.answer,
            ishard=self.ishard,
            attempts=self.attempts,
            formatted_prompt=self.formatted_prompt
        )


class JudgeCase(Document):
    def __init__(self, judgeResult: str, questions: List[Dict],
                 title: str, courtName: str, date: str, judgeList: List[str], **kwargs):
        questions = [JudgeQuestion(**qdict) for qdict in questions]
        
        self.title = title
        self.courtName = courtName
        self.date = date
        self.judgeList = judgeList
        self.litigant = kwargs['litigant']
        self.caseIntroduction = kwargs['caseIntroduction']
        self.viewPoint = kwargs['viewPoint']
        self.judgeResult = judgeResult
        self.judge_content = JudgeCase.get_judge_content(title, courtName, date, self.litigant, 
                                self.caseIntroduction, self.viewPoint, judgeResult)
        super().__init__(self.judge_content, questions)
    
    @staticmethod
    def get_judge_content(title, courtName, date, litigant, caseIntroduction, viewPoint, judgeResult):
        """ Full article content """
        result = f"\"{title}\", {courtName}, {date}."
        result += f"\n {litigant} \n{caseIntroduction} \n{viewPoint} \n{judgeResult}"
        return result
    
    @property
    def uid(self):
        return ' 受理于 '.join([self.title, self.courtName])

    @property
    def content(self):
        """ Full article content """
        result = f"\"{self.title}\", {self.courtName}, {self.date}."
        result += f"\n {self.litigant} \n{self.caseIntroduction} \n{self.viewPoint} \n{self.judgeResult}"
        return result

    @property
    def _article_context(self):
        """ Context prefix for article free questioning"""
        return f"于{self.date}，{self.courtName}提交的\"{self.title}\"中"
    
    def get_encrypted_content(self, entities, key=None, pii_entities=None):
        from crypto.parallel_encryption import encryption_pipeline
        from crypto.anonymizer import set_key
        if key is None:
            from crypto.crypto_entity import crypto_key
            set_key(crypto_key)
        content = encryption_pipeline('','','zh',entities,False,[self.content],list_filter=pii_entities)
        patterns = {
            'person': r'人物_\[(.*?)\]',       
            'loc':  r'地点_\[(.*?)\]',    
            'date':  r'日期_\[(.*?)\]',  
            'phone':  r'电话号码_\[(.*?)\]',  
            'id':  r'身份证号码_\[(.*?)\]',  
            'bank':  r'银行卡号码_\[(.*?)\]'
        }
        prefix = {
            'person': '人物_[',       
            'loc':  '地点_[',    
            'date':  '日期_[',  
            'phone':  '电话号码_[',  
            'id':  '身份证号码_[',  
            'bank':  '银行卡号码_['
        }
        encrypted_entity = []
        for pattern_name, pattern in patterns.items():
            for text in content:
                matches = re.findall(pattern, text)
                matches = list(set(matches))
                matches = [prefix[pattern_name]+m+']' for m in matches]
                encrypted_entity.extend(matches)
        return content, encrypted_entity
    
    def get_pii_entities_by_decryption(self,entities,key=None):
        from crypto.parallel_encryption import decrypt_entities
        from crypto.anonymizer import set_key
        from crypto.crypto_entity import crypto_key
        if key is None:
            set_key(crypto_key)
        d_entities = decrypt_entities(entities, key, 'zh')
        return d_entities

    def get_pii_entities(self, entities):
        from crypto.anonymizer import analyze_text, Entity_Analyzer
        patterns = {
            "person": 'TRANS_PER',
            "loc": "TRANS_LOC",
            "date": "CN_DATE",
            "phone": "CN_PHONE_NUMB",
            "id": "CN_ID_CARD_NUMB",
            "bank": "CN_CREDIT_CARD",
            "org": "ORGANIZATION"
        }
        patterns = [patterns[x] for x in entities]
        text = self.content.replace("\\n",'\n')
        text_list = [line + '\n' for line in text.split('\n')]
        results = []
        entity_analyzer = Entity_Analyzer('zh', patterns)

        for text in text_list:
            analyzed_results = entity_analyzer.analyze_text(text)
            for r in analyzed_results:
                entity = text[r.start:r.end]
                if entity not in results:
                    results.append(entity)
        return results

    def question_prompts(self, add_document_context: bool, add_thought_process: bool, sep_after_question: str):
        """All questions for a given article.

        Args:
            add_document_context: bool, whether to prepend the article context to the questions.
                For example, we set this to False in our non-contextualized question evaluation.
            add_thought_process: bool, whether to add the thought process suffix to the questions.
                We set this to False in our query embeddings.
            sep_after_question: str, either '\n' or '\n\n' depending on the prompt format.

        Returns:
            List of questions.
         """
        prompts = []
        for q in self.questions:
            prompts.append(
                q.prompt(
                    self._article_context if add_document_context else None,
                    add_thought_process,
                    sep_after_question)
            )

        return prompts

    def asdict(self):
        return dict(title=self.title,
                    courtName=self.courtName,
                    date=self.date,
                    judgeList=self.judgeList,
                    content=self.judge_content,
                    questions=[q.asdict() for q in self.questions])

class Judge(Task):
    """
    >>> from task import *
    >>> judge_raw = Judge()
    >>> len(JUDGE_raw.articles)
    """
    openai_system_generate_entities = OPENAI_API_SYSTEM_JUDGE_GENERATE_ENTITIES
    openai_system_check_entities = JUDGE_CHECK_ENTITY_LIST_PROMPT
    openai_system_generate_entity_specific_questions = OPENAI_API_SYSTEM_JUDGE_GENERATE_ENTITY_SPECIFIC_QUESTIONS
    openai_system_generate_two_entity_connection_score = OPENAI_API_SYSTEM_JUDGE_GENERATE_TWO_ENTITIES_CONNECTION_SCORE
    openai_system_generate_two_entity_relations = OPENAI_API_SYSTEM_JUDGE_GENERATE_TWO_ENTITY_RELATIONS
    openai_system_generate_three_entity_relations = OPENAI_API_SYSTEM_JUDGE_GENERATE_THREE_ENTITY_RELATIONS
    openai_system_generate_k_entity_relations = OPENAI_API_SYSTEM_JUDGE_GENERATE_K_ENTITY_RELATIONS
    llama_cot_prompt = JUDGE_FEW_SHOT_COT_PROMPT

    def _create_documents(self):
        documents = []
        for adict in self._data:
            questions = []
            for qdict in adict['questions']:
                question = dict(statement=qdict['question'],
                                options=qdict['options'],
                                answer=qdict['gold_label'],
                                ishard=bool(qdict['difficult']))
                questions.append(question)
            questions = sorted(questions, key=lambda x: x['statement'])
            # questions = {}
            document = JudgeCase(
                              title=adict['title'],
                              courtName=adict['courtName'],
                              date=adict['dataDate'],
                              judgeList=adict['judgeList'],
                              litigant=adict['litigant'],
                              caseIntroduction=adict['caseIntroduction'],
                              viewPoint=adict['viewPoint'],
                              judgeResult=adict['judgeResult'],
                              questions=questions)
            documents.append(document)
        super().__init__('judge', sorted(documents, key=lambda x: x.title))

    def _dedup(self):
        deuped_documents = {}
        for document in self.documents:
            key = document.uid
            if key not in deuped_documents:
                deuped_documents[key] = document
            else:
                deuped_documents[key].questions += document.questions
        self.documents = list(deuped_documents.values())
    
    @staticmethod
    def load_case_json():
        path = "data/dataset/raw/JudgementQA_v2.json"
        return jload(path)

    def __init__(self):
        # self.split = split
        self._data = Judge.load_case_json()
        self._create_documents()
        self._dedup()

    def load_attempts_json(self, file_path: str):
        loaded_articles_data = jload(file_path)

        attempted_articles = []
        for adict in loaded_articles_data:
            article = JudgeCase(**adict)
            if article.title in self.cur_doc_titles:
                attempted_articles.append(article)
        super().__init__('JUDGE', sorted(attempted_articles, key=lambda x: x.title))

    def all_questions(self, add_document_context: bool, add_thought_process: bool, sep_after_question: str):
        prompts = []
        for document in self.documents:
            print(document.title)
            prompts += document.question_prompts(add_document_context, add_thought_process, sep_after_question)
        print(len(self.documents))
        return prompts
