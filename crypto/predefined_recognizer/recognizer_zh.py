import re

from presidio_analyzer import Pattern, PatternRecognizer, EntityRecognizer, RecognizerResult

class CNCreditRecognizer(EntityRecognizer):
    def __init__(self):
        super().__init__(supported_entities="CUSTOM_ENTITY")
        # self.context_words = ["keyword1", "keyword2", "context_word"]

    def analyze(self, text, entities, nlp_artifacts):
        # print(11111)
        results = []
        regex = re.compile(r"\d{4}-\d{4}-\d{4}-\d{4}\b|\d{16}")
        # Your logic for pattern recognition
        # For example, using regex to find a specific pattern:
        regex_results = regex.findall(text) #error
        
        # Loop through found patterns
        for result in regex_results:
            # Check context (surrounding words or specific conditions)
            print(result)
            # Add result to list if context matches
            results.append(RecognizerResult(
                entity_type="CUSTOM_ENTITY",
                start=result.start,
                end=result.end,
                score=0.85  # Adjust the confidence score as needed
            ))
        return results

    # def _has_context(self, result, text):
        # Implement logic to check for context (keywords, nearby entities)
        # For example, checking if certain keywords appear within a few words of the match
        # surrounding_text = text[max(0, result.start-20):min(len(text), result.end+20)]
        # for word in self.context_words:
        #     if word in surrounding_text:
        #         return True
        # return False
        # pass

def custom_pattern_recognizer(regex_patterns, pattern_name, entity_name, score, lang='zh', context=[],):
    custom_patterns = []
    for pattern in regex_patterns:
        custom_pattern = Pattern(name=pattern_name, regex=pattern, score=score)
        custom_patterns.append(custom_pattern)

    # Define the custom recognizer using PatternRecognizer
    custom_recognizer = PatternRecognizer(
        supported_entity=entity_name,  # Custom entity name
        patterns=custom_patterns,  # Pass the Pattern object here
        supported_language=lang,
        context=context
    )
    return custom_recognizer

def get_bank_number_recognizer():
    
    # Create a Pattern object
    custom_regex_pattern = r"(?<!\d)(\d{4}-\d{4}-\d{4}-\d{4}|\d{16}|\d{19})(?!\d)"
    custom_pattern = Pattern(name="custom_credit_card_pattern", regex=custom_regex_pattern, score=0.4)

    # Define the custom recognizer using PatternRecognizer
    custom_recognizer = PatternRecognizer(
        supported_entity="CN_CREDIT_CARD",  # Custom entity name
        patterns=[custom_pattern],  # Pass the Pattern object here
        supported_language="zh"
    )
    return custom_recognizer

def get_cn_id_card_recognizer():
    """
    CN ID card
     Regex expression: "^[1-9]\\d{5}[1-9]\\d{3}((0\\d)|(1[0-2]))(([0|1|2]\\d)|3[0-1])\\d{3}([0-9Xx])$"
     "(^[1-9]\\d{5}(18|19|20)\\d{2}((0[1-9])|(10|11|12))(([0-2][1-9])|10|20|30|31)\\d{3}[0-9Xx]$)|" \
                            "(^[1-9]\\d{5}\\d{2}((0[1-9])|(10|11|12))(([0-2][1-9])|10|20|30|31)\\d{3}$)"
    """
    regex_pattern = r"(?<!\d)([1-9]\d{5}(18|19|20)\d{2}((0[1-9])|(10|11|12))(([0-2][1-9])|10|20|30|31)\d{3}[0-9Xx]|[1-9]\d{5}\d{2}((0[1-9])|(10|11|12))(([0-2][1-9])|10|20|30|31)\d{3})(?!\d)"
    context = ['身份证','号码','号','身份']
    id_card_recognizer = custom_pattern_recognizer([regex_pattern], "id_card_pattern", "CN_ID_CARD_NUMB", 0.4,
                                                    context=context)
    return id_card_recognizer

def get_date_recognizer():
    regex_pattern = r"((19|20)\d{2})年(0?[1-9]|1[0-2])月(0?[1-9]|[12]\d|3[01])日"
    date_recognizer = custom_pattern_recognizer([regex_pattern], "date_pattern", "CN_DATE", 0.8)
    return date_recognizer

def get_phone_recognizer():
    regex_patterns = [
        r"(?<!\d)1[3-9]\d{9}(?!\d)",
        r"(?<!\d)(\+?86)?1[3-9]\d{9}(?!\d)"
    ]
    phone_recognizer = custom_pattern_recognizer(regex_patterns, "phone_number_pattern", "CN_PHONE_NUMB", 0.8)
    return phone_recognizer

def get_amount_recognizer():
    ## Amount
    # error
    regex_pattern = "([0-9]+|[0-9]{1,3}(,[0-9]{3})*)(.[0-9]{1,2})?"
    context = ['元','万元','千元','块','万块']
    amount_recognizer = custom_pattern_recognizer([regex_pattern], "amount_pattern", "CN_AMOUNT", 0.2,
                                                    context=context)
    return amount_recognizer

if __name__ == '__main__':
    regex_pattern = re.compile(r"(?:(19|20)\d{2})年(?:(0?[1-9]|1[0-2])月(?:(0?[1-9]|[12]\d|3[01])日))")
    test_string = "2020年1月09日"

    if re.match(regex_pattern, test_string):
        print("The string matches the format.")
    else:
        print("The string does not match the format.")