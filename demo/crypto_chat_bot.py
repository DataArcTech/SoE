import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
import random
import time
import re
import gradio as gr
from vllm import LLM
from inference.llama import llama_forward
from crypto.anonymizer import analyze_text, anonymize, set_key, Entity_Analyzer
from crypto.crypto_entity import decrypt_aes_ecb
from utils.prompt_utils_zh import generate_all_answer_strings
from utils.prompt_utils_zh import JUDGE_TOOLS_PROMPT, JUDGE_SHORT_ANSWER_QUESTION, JUDGE_CHAT_PROMPT, JUDGE_FEW_SHOT_COT_PROMPT

USER_KEY = ""
model_path = 'llm_models/llama_factory/qwen2.5_7b_encrypt_judge_all_zh_v1'
tokenizer_model_name = 'Qwen/Qwen2.5-7B'
MODEL = LLM(model=model_path, tokenizer=tokenizer_model_name, tensor_parallel_size=1)
### Model selection

### prompt encryption
def multiple_choice_question_format(question, choices):
    formatted = "### 问题\n"

    formatted += f"{question} 仅有一个正确选项。\n"
    
    formatted += f"### 选项\n"
    formatted += choices

    formatted += "\n### 思路及答案\n"
    formatted += "思路: "
    # formatted += "\n### 推理、行动及答案\n"
    # formatted += "推理: "
    return formatted

def short_answer_question_format(question):
    formatted = "### 问题\n"

    formatted += f"{question}\n"

    formatted += "### 推理及答案\n"
    formatted += "推理: "
    return formatted

def chat_question_format(question):
    formatted = "### 问题\n"

    formatted += f"{question}\n"

    formatted += "### 回答\n"
    formatted += "答案: "
    return formatted

def get_encryped_prompts(prompts, lang):
    encrypted_prompts = []
    detect_entities = ["TRANS_PER","TRANS_LOC","CN_DATE","CN_PHONE_NUMB","CN_ID_CARD_NUMB","CN_CREDIT_CARD"]
    # detect_entities = ["TRANS_PER","TRANS_LOC","CN_DATE"]
    # detect_entities = ["TRANS_PER","TRANS_LOC"]
    entity_analyzer = Entity_Analyzer(lang,detect_entities)
    for text in prompts:
        
        analyzer_results = entity_analyzer.analyze_text(text)
        try:
            result = anonymize(analyzer_results, text)
            encrypted_prompts.append(result.text)
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            result = f'XXX，无法加密'

    return encrypted_prompts

def get_prompt(question_type, content):
    if question_type == 'multiple_choice':
        question, choices = content['question'].split('\n\n')
        prompt = multiple_choice_question_format(question, choices)
        system_message = JUDGE_FEW_SHOT_COT_PROMPT
        stop_words = generate_all_answer_strings() + ['行动: 解密']
    elif question_type == 'short_answer':
        prompt = short_answer_question_format(content["question"])
        system_message = JUDGE_SHORT_ANSWER_QUESTION
        stop_words = ['行动: 解密','### 问题', '\n\n', '## 示例']
    elif question_type == 'chat':
        prompt = chat_question_format(content["question"])
        system_message = JUDGE_CHAT_PROMPT
        stop_words = ['### 问题', '\n\n', '## 示例']
    return (prompt, system_message, stop_words)

### response decryption
def decrypt_pii_mapping(text, lang):
    mapping_text = f""
    mapping_list = []
    entities = ['ENCRYPT']
    analyze_results = analyze_text(text, 'en', entities)
    for r in analyze_results:
        content = text[r.start:r.end]
        if content in mapping_list:
            continue
        mapping_list.append(content)
        offset = len(content.split('_[')[0])+2
        try:
            de_text = decrypt_aes_ecb(USER_KEY, content[offset:-1])
            result = de_text.decode('utf-8')
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            result = f'XXX，无法解密'
        mapping_text += f"{content}对应于{result}；"
    # result = anonymize(r, text, lang, 'decrypt')
    return mapping_text

def decrypt_pii(text, lang):
    entities = ['ENCRYPT']
    analyze_results = analyze_text(text, 'en', entities)
    try:
        result = anonymize(analyze_results, text, lang, 'decrypt')
        result = result.text
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        result = f'不能解密，密文为 {text}'
    return result

def get_response(message, question_type, prompt=None, system_message=None, stop_words=None):
    # content = {"question": "谁是人物_[aHBES5WxmZLwZIYuolLBtA==]？"}
    content = {"question": message}
    if not (prompt and system_message and stop_words):
        prompt, system_message, stop_words = get_prompt(question_type, content)
    print(system_message)
    print(prompt)
    # print(stop_words)
    outputs = llama_forward(
        model=MODEL,
        prefix_or_prefixes=system_message,
        n_gpus = 1,
        prompts=[prompt],
        max_length = 1024,
        stop_words = stop_words
    )
    if len(outputs[0]):
        output = outputs[0][0]
    else:
        output = '答案: 没有满足条件的答案'
    print(output)
    if output[-2:] == '解密':
        # call decryption
        suffix = '，推理中包含密文，需要解密回答。\n解密: '
        # content
        response = decrypt_pii_mapping(output[:-2], 'zh')
        response = output+suffix+response+'\n推理: '
        keep_inference = True
    elif (output[-2:] == '\n\n') and '答案' in output:
        response = output
        keep_inference = False
    elif output[-6:] in ['### 问题', '## 示例:']:
        response = output[:-5]
        keep_inference = False
    else:
        response = output
        keep_inference = False
    return response, keep_inference, [prompt, system_message, stop_words]

def echo(message, history, box_choice, dropdown_choice, key):
    # response = f"System prompt: {system_prompt}\n Message: {message}."
    global USER_KEY
    USER_KEY = key
    set_key(USER_KEY)
    keep_inference = True
    response = ""
    infer_info = ["", None, None]
    if '加密' == box_choice:
        message = get_encryped_prompts([message], 'zh')[0]
        history.append({'role': 'assistant', 'content': message})
    if dropdown_choice == '简答题':
        question_type = 'short_answer'
    elif dropdown_choice == '选择题':
        question_type = 'multiple_choice'
    elif dropdown_choice == '对话':
        question_type = 'chat'
    while keep_inference:
        response, keep_inference, infer_info = get_response(message, question_type, infer_info[0]+response, infer_info[1], infer_info[2])
        for i in range(len(response)):
            time.sleep(0.05)
            yield response[: i+1]
        print('-------')
        print(history)
    if question_type == 'multiple_choice':
        text = decrypt_pii(response, 'zh')
        for i in range(len(response)):
            time.sleep(0.05)
            yield text[: i+1]
    final_result = re.split('答案', response)[-1]
    final_result = "答案 " + decrypt_pii(final_result, 'zh')
    for i in range(len(final_result)):
        time.sleep(0.05)
        yield final_result[: i+1]

with gr.Blocks() as demo:
    key = gr.Textbox("WmZq4t7w!z%C&F)J", label="Key")
    # slider = gr.Slider(10, 100, render=False)
    checkbox = gr.Radio(
        choices=["原文", "加密"],
        
        label="问题处理"
    )
    dropdown = gr.Dropdown(
        choices=["简答题", "选择题", "对话"],
        label="问题类型"
    )
    gr.ChatInterface(
        echo, additional_inputs=[checkbox, dropdown, key], type="messages"
    )

demo.launch()
# get_response('')