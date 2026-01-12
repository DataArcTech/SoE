from openai import OpenAI

def gptqa(prompt: str,
          openai_model_name: str,
          system_message: str,
          json_format: bool = False,
          temp: float = 1.0):
    if 'gpt' in openai_model_name:
        api_key = "" # your chatgpt keys
        base_url = "https://api.gptsapi.net/v1"
    elif 'deepseek' in openai_model_name:
        api_key = "" # your deepseek keys
        base_url = "https://api.deepseek.com/v1"
        openai_model_name = "deepseek-v3-241226"
    client = OpenAI(api_key=api_key, base_url=base_url)

    if json_format:
        completion = client.chat.completions.create(
            model=openai_model_name,
            temperature=0,
            top_p=0.7,
            response_format={ "type": "json_object" },
            messages=[
                {"role": "system",
                "content": system_message},
                {"role": "user",
                "content": prompt},
            ])
    else:
        completion = client.chat.completions.create(
            model=openai_model_name,
            temperature=0,
            top_p=0.7,
            messages=[
                {"role": "system",
                "content": system_message},
                {"role": "user",
                "content": prompt},
            ])
    if completion is not None:
        res = completion.choices[0].message.content
    else:
        res = "### No response"

    return res