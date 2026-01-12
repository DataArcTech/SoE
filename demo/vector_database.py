from sentence_transformers import SentenceTransformer
import chromadb
from openai import OpenAI
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
import random
import time
import re
import gradio as gr
from crypto.anonymizer import analyze_text, anonymize, set_key, Entity_Analyzer
from crypto.crypto_entity import decrypt_aes_ecb

def chat_with_llm(input_query, base_url, api_key, llm_type="gpt-4o-mini"):
    LLM_client = OpenAI(base_url=base_url, api_key=api_key)
    messages = [{"role": "system", "content": "你是一个人工智能助手。请回答用户的问题。"}]
    
    # 添加当前用户的问题
    messages.append({"role": "user", "content": input_query})

    try:
        completion = LLM_client.chat.completions.create(
            model=llm_type,
            messages=messages
        )
        answer = completion.choices[0].message.content
        return answer
    except Exception as e:
        print(e)
        return f"与LLM交互时发生错误，请稍后再试。{e}"
    
def get_retrieve_docs(vector_path, model_path, query):
    """
    vector_path = "/data/FinAi_Mapping_Knowledge/zhangliyu/tog3_datasets/markdown_processed_file/vector_data"
    model_path: "/data/FinAi_Mapping_Knowledge/chenmingzhen/conan-embedding"
    """
    #  vector database path
    # vector_path = "/data/FinAi_Mapping_Knowledge/zhangliyu/tog3_datasets/markdown_processed_file/vector_data"
    # embedding model
    model = SentenceTransformer(model_path)

    # load vector database
    client = chromadb.PersistentClient(path=vector_path)
    collection = client.get_collection(name="all_area")

    query_embedding = model.encode([query])

    results = collection.query(query_embeddings=query_embedding, n_results=10)
    documents = results.get("documents", [])

    retrieve_docs = "\n".join(doc for doc in documents[0])
    return retrieve_docs

USER_KEY = ""
# model_path = '/finance_ML/FinAi_Mapping_Knowledge/personal_data/liuhonghao/llm_models/llama_factory/qwen2.5_7b_encrypt_judge_all_zh_v1'
# tokenizer_model_name = 'Qwen/Qwen2.5-7B'
# MODEL = LLM(model=model_path, tokenizer=tokenizer_model_name, tensor_parallel_size=1)
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

    formatted += "### 推理、行动及答案\n"
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
    # detect_entities = ["TRANS_PER","TRANS_LOC","CN_DATE","CN_PHONE_NUMB","CN_ID_CARD_NUMB","CN_CREDIT_CARD"]
    # detect_entities = ["TRANS_PER","TRANS_LOC","CN_DATE"]
    detect_entities = ["TRANS_PER","TRANS_LOC","ORGANIZATION","CN_DATE"]
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

def get_response(message, question_type, encrypted=False, key_condition=False):
    # content = {"question": "谁是人物_[aHBES5WxmZLwZIYuolLBtA==]？"}
    base_url='https://api.gptsapi.net/v1'
    api_key="sk-T4275d8839105d2c0067c7c41eba59528ccf4fee63bDiRxw"
    llm_type="gpt-4o-mini"
    vector_path = "/data/FinAi_Mapping_Knowledge/zhangliyu/tog3_datasets/markdown_processed_file/vector_data"
    model_path = "/data/FinAi_Mapping_Knowledge/liuhonghao/models/conan-embedding"
    if encrypted and key_condition:
        retrieve_docs = get_retrieve_docs(vector_path, model_path, message)
        input_query = f"下面是用户的提问，请按照要求回复用户的问题：\n{message}" + f"下面是检索到的文档：\n{retrieve_docs}\n" + "请根据问题以及检索到的文档回答问题"
    else:
        input_query = message
    response = chat_with_llm(input_query, base_url, api_key, llm_type)
    return response

def echo(message, history, box_choice, dropdown_choice, key):
    # response = f"System prompt: {system_prompt}\n Message: {message}."
    global USER_KEY
    USER_KEY = key
    set_key(USER_KEY)
    keep_inference = True
    response = ""
    infer_info = ["", None, None]
    if dropdown_choice == '简答题':
        question_type = 'short_answer'
    elif dropdown_choice == '选择题':
        question_type = 'multiple_choice'
    elif dropdown_choice == '对话':
        question_type = 'chat'
    key_condition = False
    if key == "WmZq4t7w!z%C&F)J":
        key_condition = True
    if '加密' == box_choice:
        history.append(gr.ChatMessage("user", message))
        yield "", history
        encrypted_message = get_encryped_prompts([message], 'zh')[0]
        print(history)
        

        history.append(gr.ChatMessage("user", encrypted_message))
        # print(history)
        for i in range(len(encrypted_message)):
            time.sleep(0.05)
            history[-1] = gr.ChatMessage("user", encrypted_message[: i+1])
            yield "", history
        # yield history
        time.sleep(0.5)
        history.append(gr.ChatMessage("assistant", "检索信息、模型响应中..."))
        yield "", history
        response = get_response(message, question_type, True, key_condition)
        encrypted_response = get_encryped_prompts([response], 'zh')[0]
        history.append(gr.ChatMessage("assistant", encrypted_response))
        for i in range(len(encrypted_response)):
            time.sleep(0.05)
            history[-1] = gr.ChatMessage("assistant", encrypted_response[: i+1])
            yield "", history
        
        history.append(gr.ChatMessage("assistant", "解密中..."))
        yield "", history
        time.sleep(0.5)
        history.append(gr.ChatMessage("assistant", response))
        for i in range(len(response)):
            time.sleep(0.05)
            history[-1] = gr.ChatMessage("assistant", response[: i+1])
            yield "", history
        # history.append({'role': 'assistant', 'content': message})
        # print('-------')
        # print(history)
        # final_result = '加密问题: ' + encrypted_message + '\n' + '回答: ' + encrypted_response + '\n' + '解密回答: '+ response
        # yield final_result
    else:
        history.append(gr.ChatMessage("user", message))
        yield "", history
        response = get_response(message, question_type, False, key_condition)
        history.append(gr.ChatMessage("assistant", response))
        # print(history)
        for i in range(len(response)):
            time.sleep(0.05)
            history[-1] = gr.ChatMessage("assistant", response[: i+1])
            yield "", history

    # if question_type == 'multiple_choice':
    #     text = decrypt_pii(response, 'zh')
    #     for i in range(len(response)):
    #         time.sleep(0.05)
    #         yield text[: i+1]
    # final_result = re.split('答案', response)[-1]
    # final_result = "答案 " + decrypt_pii(final_result, 'zh')
    # for i in range(len(final_result)):
    #     time.sleep(0.05)
    #     yield final_result[: i+1]

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
    # gr.ChatInterface(
    #     echo, additional_inputs=[checkbox, dropdown, key], type = "messages"
    # )
    # Define the state for the chat history
    state = gr.State([])

    # Create the chatbot display area (with the same layout as ChatInterface)
    chatbot = gr.Chatbot(type="messages", height=300, show_copy_button=True)
    # with gr.Row():
    # Create the text input for the user message
    user_input = gr.Textbox(placeholder="输入信息...", label="输入框")

    # Create the send button
    send_button = gr.Button("发送")

    # Set up the interaction between input, button, and chatbot
    send_button.click(fn=echo, inputs=[user_input, state, checkbox, dropdown, key], outputs=[user_input, chatbot])
    user_input.submit(fn=echo, inputs=[user_input, state, checkbox, dropdown, key], outputs=[user_input, chatbot])
demo.launch(share=True)