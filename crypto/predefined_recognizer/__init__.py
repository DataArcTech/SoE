from crypto.predefined_recognizer.encrypted_recognizer import get_encrypted_person_recognizer, get_encrypted_recognizer
from crypto.predefined_recognizer.recognizer_zh import get_bank_number_recognizer, get_cn_id_card_recognizer, get_amount_recognizer, get_date_recognizer, get_phone_recognizer
from crypto.predefined_recognizer.transformer_recognizer_zh import get_transformer_ner, get_transformer_ner_org

def get_customed_recognizers(entities):
    c_recognizers = []
    if 'ENCRYPT_PERSON' in entities:
        recog = get_encrypted_person_recognizer()
        c_recognizers.append(recog)
    if 'ENCRYPT' in entities:
        recog = get_encrypted_recognizer()
        c_recognizers.append(recog)
    if 'CN_CREDIT_CARD' in entities:
        recog = get_bank_number_recognizer()
        c_recognizers.append(recog)
    if 'CN_ID_CARD_NUMB' in entities:
        recog = get_cn_id_card_recognizer()
        c_recognizers.append(recog)
    if 'CN_AMOUNT' in entities:
        recog = get_amount_recognizer()
        c_recognizers.append(recog)
    if 'CN_DATE' in entities:
        recog = get_date_recognizer()
        c_recognizers.append(recog)
    if 'CN_PHONE_NUMB' in entities:
        recog = get_phone_recognizer()
        c_recognizers.append(recog)
    if 'ORGANIZATION' in entities:
        recog = get_transformer_ner_org()
        c_recognizers.append(recog)
    elif 'TRANS_PER' in entities:
        recog = get_transformer_ner()
        c_recognizers.append(recog)

    
    return c_recognizers