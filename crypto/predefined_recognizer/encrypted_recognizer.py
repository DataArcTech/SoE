import re

from presidio_analyzer import Pattern, PatternRecognizer, EntityRecognizer, RecognizerResult

class EncryptedRecognizer(EntityRecognizer):
    def __init__(self):
        super().__init__(supported_entities="CUSTOM_ENTITY")
        # self.context_words = ["keyword1", "keyword2", "context_word"]

    def analyze(self, text, entities, nlp_artifacts):
        results = []
        pattern = r"^Person_\[[A-Za-z0-9+/=]+\]$"
        regex = re.compile(pattern)
        
        # Using regex to find a specific pattern:
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

def get_encrypted_person_recognizer():

    # Create a Pattern object
    custom_regex_pattern = r"Person_\[[A-Za-z0-9+/=]+\]"
    custom_pattern = Pattern(name="person_encrypted_pattern", regex=custom_regex_pattern, score=0.85)
    custom_regex_pattern_zh = r"人物_\[[A-Za-z0-9+/=]+\]"
    custom_pattern_zh = Pattern(name="person_encrypted_pattern_zh", regex=custom_regex_pattern_zh, score=0.85)
    
    # Define the custom recognizer using PatternRecognizer
    custom_recognizer = PatternRecognizer(
        supported_entity="ENCRYPT_PERSON",  # Custom entity name
        patterns=[custom_pattern, custom_pattern_zh],  # Pass the Pattern object here
        # supported_language="en"
    )
    return custom_recognizer

def get_encrypted_location_recognizer():

    # Create a Pattern object
    custom_regex_pattern = r"Location_\[[A-Za-z0-9+/=]+\]"
    custom_pattern = Pattern(name="location_encrypted_pattern", regex=custom_regex_pattern, score=0.85)
    custom_regex_pattern_zh = r"地点_\[[A-Za-z0-9+/=]+\]"
    custom_pattern_zh = Pattern(name="location_encrypted_pattern_zh", regex=custom_regex_pattern_zh, score=0.85)

    # Define the custom recognizer using PatternRecognizer
    custom_recognizer = PatternRecognizer(
        supported_entity="ENCRYPT_LOCATION",  # Custom entity name
        patterns=[custom_pattern, custom_pattern_zh],  # Pass the Pattern object here
        # supported_language="en"
    )
    return custom_recognizer

def get_encrypted_date_recognizer():

    # Create a Pattern object
    custom_regex_pattern = r"date_\[[A-Za-z0-9+/=]+\]"
    custom_pattern = Pattern(name="date_encrypted_pattern", regex=custom_regex_pattern, score=0.85)
    custom_regex_pattern_zh = r"日期_\[[A-Za-z0-9+/=]+\]"
    custom_pattern_zh = Pattern(name="location_encrypted_pattern_zh", regex=custom_regex_pattern_zh, score=0.85)

    # Define the custom recognizer using PatternRecognizer
    custom_recognizer = PatternRecognizer(
        supported_entity="ENCRYPT_DATE",  # Custom entity name
        patterns=[custom_pattern, custom_pattern_zh],  # Pass the Pattern object here
        # supported_language="en"
    )
    return custom_recognizer

def get_encrypted_recognizer(type='all'):

    # Create a Pattern object
    patterns = []
    # Configurations for pattern names and regex
    configs = [
        ("person", [r"Person_\[[A-Za-z0-9+/=]+\]", r"人物_\[[A-Za-z0-9+/=]+\]"]),
        ("location", [r"Location_\[[A-Za-z0-9+/=]+\]", r"地点_\[[A-Za-z0-9+/=]+\]"]),
        ("date", [r"Date_\[[A-Za-z0-9+/=]+\]", r"日期_\[[A-Za-z0-9+/=]+\]"]) if type in ['all', 'pld'] else None,
        ("phone", [r"Phone_number_\[[A-Za-z0-9+/=]+\]", r"电话号码_\[[A-Za-z0-9+/=]+\]"]) if type == 'all' else None,
        ("bank", [r"Bank_card_\[[A-Za-z0-9+/=]+\]", r"银行卡号码_\[[A-Za-z0-9+/=]+\]"]) if type == 'all' else None,
        ("id", [r"ID_number_\[[A-Za-z0-9+/=]+\]", r"身份证号码_\[[A-Za-z0-9+/=]+\]"]) if type == 'all' else None
    ]
    # Construct patterns
    for config in filter(None, configs):  # Skip None configurations
        name_prefix, regex_list = config
        for regex in regex_list:
            patterns.append(Pattern(name=f"{name_prefix}_encrypted_pattern", regex=regex, score=0.85))
    # Define the custom recognizer using PatternRecognizer
    custom_recognizer = PatternRecognizer(
        supported_entity="ENCRYPT",  # Custom entity name
        patterns=patterns,  # Pass the Pattern object here
        # supported_language="en"
    )
    return custom_recognizer

if __name__ == '__main__':
    pattern = r"Person_\[[A-Za-z0-9+/=]+\]"
    test_string = "Person_[12345x]"  # This will match any length of digits

    if re.match(pattern, test_string):
        print("The string matches the format.")
    else:
        print("The string does not match the format.")