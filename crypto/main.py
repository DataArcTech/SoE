from utils import get_synthesized_data_from_json, revise_synthesized_enti_json
from anonymizer import analyze_text, anonymize, set_key, Entity_Analyzer
import argparse
import os
from tqdm import tqdm
from utils import jdump, jload

parser = argparse.ArgumentParser(description='Encryption')
parser.add_argument('--start', help="start point", type=int, required=True)
parser.add_argument('--end', help="end point", type=int, required=True)
parser.add_argument('--lang', help="language", type=str, default='en')


if __name__ == "__main__":

    aritcle_path = "data/dataset/raw/judge_weighted_edge_entigraph_deepseek-chat-v2/10/" # article path
    save_folder = "data/dataset/raw/judge_weighted_encrypt_edge_entigraph_deepseek-chat/10/" # path for encrypted articles 
    article_names_all = os.listdir(aritcle_path)
    
    args = parser.parse_args()
    article_names = article_names_all[args.start:args.end]
    from crypto_entity import crypto_key
    set_key(crypto_key)
    detect_entities = ["TRANS_PER","TRANS_LOC","CN_DATE","CN_PHONE_NUMB","CN_ID_CARD_NUMB","CN_CREDIT_CARD"]
    detect_entities = ["TRANS_PER","TRANS_LOC"]

    entity_analyzer = Entity_Analyzer(args.lang,detect_entities)

    for article_name in article_names:
        print(article_name)
        with open(aritcle_path+article_name, "r") as f:
            # synth_data = f.readlines() 
            synth_data = jload(f)
        lang = args.lang
        # f = open("data/"+ "pi_v3_encrypt" + article_name, 'a')
        converted_row = []
        # entities = synth_data[0]
        # detect_entities = ["TRANS_PER","TRANS_LOC","CN_DATE","CN_PHONE_NUMB","CN_ID_CARD_NUMB","CN_CREDIT_CARD"]
        entity_list = []
        for entity in synth_data[0]:
            analyzer_results = entity_analyzer.analyze_text(entity)
            result = anonymize(analyzer_results, entity, lang = "zh_CN", type = "encrypt")
            entity_list.append(result.text)
        converted_row.append(entity_list)
        # f.write(str(entity_list))
        # f.close()
        for text in tqdm(synth_data[1:]):
            # f = open(save_folder + article_name, 'a')
            ts = [line + '\n' for line in text.split('\n')]
            final_result = ''
            for t in ts:
                analyzer_results = entity_analyzer.analyze_text(t)
                result = anonymize(analyzer_results, t, lang = "zh_CN", type = "encrypt")
                final_result = final_result + result.text
            
            converted_row.append(final_result)
            # f.write(final_result)
            # f.close()
        output_path = save_folder+ article_name
        # jdump(converted_row)
        with open(output_path,"w") as f:
            jdump(converted_row,f)

            # for row in converted_row:
        #         f.write(row)
        # revise_synthesized_enti_json(aritcle_path+article_name, aritcle_path+'revised_'+article_name)
        print(f"finished {article_name}")