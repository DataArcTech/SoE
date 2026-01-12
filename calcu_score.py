import os
import io
import json
from utils.io_utils import jload, jdump
import argparse
parser = argparse.ArgumentParser(description='Calcualte Score..')
parser.add_argument('--path', help="result path", type=str, required=True)

def save_reasoning_logs(output_path, loaded_articles_data, personal_question_index_list, question_filter=True):
    # output_path = "outputs/noncontext-nonencrypt_q_syndata_pii_questions.json"
    critical_artices = []
    article_count = 0
    for article in loaded_articles_data:
        
        if article["title"] in cur_doc_titles:
            critical_artice = {}
            print(article["title"])
            questions = article["questions"]
        
            critical_quesions = []
            count = 0
            pred_answers = []
            answers = []
            for i,question in enumerate(questions):
                
                statement = question["statement"]
                answer = question["answer"]
                ishard = question["ishard"]
                if i not in personal_question_index_list[article_count] and question_filter:
                    continue
                critical_quesion = {}
                critical_quesion['statement'] = question["statement"]
                critical_quesion['answer'] = question["answer"]
                critical_quesion['ishard'] = question["ishard"]
                critical_quesion['attempts'] = question["attempts"]
                critical_quesion['formatted_prompt'] = question["formatted_prompt"]
                critical_quesions.append(critical_quesion)
            article_count = article_count + 1
            if len(critical_quesions):
                critical_artice["title"] = article["title"]
                critical_artice["author"] = article["author"]
                critical_artice["year"] = article["year"]
                critical_artice["questions"] = critical_quesions
                critical_artices.append(critical_artice)

    jdump(critical_artices,output_path)
    
def get_vote_answer(attempts):
    ans = [0,0,0,0]
    for attempt in attempts:
        ca = attempt["answer_index"]
        ans[ca] = ans[ca] + 1
    mid = 0
    for i,tmp_a in enumerate(ans):
        if ans[mid] < tmp_a:
            mid = i
    return mid

def calculate_score(file_name, cur_doc_titles, loaded_articles_data, personal_question_index_list, 
                    question_filter=True):

    id2aph = ['A','B','C','D']
    detect_entities = ["PERSON"]

    article_count = 0
    count_sum = 0
    question_sum = 0
    critical_sum = 0
    for article in loaded_articles_data:
        if article["title"] in cur_doc_titles or True:
            questions = article["questions"]
            critial_quesions = []
            count = 0
            pred_answers = []
            answers = []
            for i,question in enumerate(questions):
                # print(question["statement"])
                statement = question["statement"]
                if i not in personal_question_index_list[article_count] and question_filter:
                    continue
                
                critial_quesions.append(i)
                pred_ans = id2aph[get_vote_answer(question["attempts"])]
                answers.append(question["answer"])
                pred_answers.append(pred_ans)
                if pred_ans == question["answer"]:
                    count = count + 1
            count_sum = count_sum + count
            question_sum = question_sum + len(questions)
            critical_sum = critical_sum + len(critial_quesions)
            print('--------------------')
            print(article["title"])
            print(f"Answers:\n{answers}")
            print(f"Prediction:\n{pred_answers}")
            if len(critial_quesions):
                print(f"{count}/{len(critial_quesions)} = {count/len(critial_quesions)}")
            print(critial_quesions)
            article_count = article_count + 1
            # break
    print(f"Total ratio: {count_sum}/{critical_sum} = {count_sum/critical_sum}")


if __name__ == '__main__':
    cur_doc_titles = [
        ' Defining Decay Down',
        ' Fight Clubbed',
        ' It\'s Time To Keelhaul U-Haul!',
        ' My Father\'s Estate',
        '"Phone Me in Central Park"',
        '...After a Few Words...',
        '...And It Comes Out Here'
    ]
    args = parser.parse_args()
    file_name = args.path
    # file_name = "outputs/token-train_judgeqa-synthesis-non-context-encryption-crypto-judge-lr5e-06-rr0.1-epochs2-bs16-wd0.01-warmup0.05-Qwen2.57B.json"
    loaded_articles_data = jload(file_name)

    personal_question_index_list = [ [],[4,15],[12],[19],[0, 1, 3, 4, 6, 8, 9, 11, 14, 16],[0, 1, 2, 3, 5, 6, 8, 9, 11, 12, 13, 15, 17],[0, 1, 2, 3, 4, 7, 8]]
    calculate_score(file_name, cur_doc_titles, loaded_articles_data, personal_question_index_list, question_filter=False)