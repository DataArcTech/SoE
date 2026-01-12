# Adopted from https://github.com/zitongyang/synthetic_continued_pretraining
import torch
from typing import Sequence, Optional, Union, Iterable
from vllm import LLM, SamplingParams

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from utils import python_utils
from utils.prompt_utils import generate_all_answer_strings as generate_all_answer_strings_en
from utils.prompt_utils_zh import generate_all_answer_strings as generate_all_answer_strings_zh

sys.setrecursionlimit(1500)
def llama_forward(
    prefix_or_prefixes: Optional[Union[str, Iterable[str]]],
    prompts: Sequence[str],
    model: Optional[torch.nn.Module] = None,
    model_path: Optional[str] = None,
    max_length: int = 300,  # Generation length
    temperature: float = 0.1,
    n_samples: int = 8,
    n_gpus: int = 8,
    stop_words = None,
    tokenizer_model_name: Optional[str] = None
) -> Optional[Sequence[str]]:
    assert model is not None or model_path is not None, "model or model_path must be provided"

    if isinstance(prefix_or_prefixes, str):
        prompts = [prefix_or_prefixes + prompt for prompt in prompts]
    elif isinstance(prefix_or_prefixes, Sequence):
        prompts = [prefix + prompt for prefix, prompt in python_utils.zip_(prefix_or_prefixes, prompts)]
    elif prefix_or_prefixes is not None:
        raise ValueError(
            f"prefix_or_prefixes must be None, a string, or a sequence of strings, not {type(prefix_or_prefixes)}")

    if temperature == 0.0:
        # best_of must be 1 when using greedy decoding
        n_samples = 1

    if stop_words is None:
        if 'qwen' in model_path.lower():
            stop_words = generate_all_answer_strings_zh()
        elif 'llama' in model_path.lower():
            stop_words = generate_all_answer_strings_en()


    sampling_params = SamplingParams(n=n_samples,
                                     temperature=temperature,
                                     max_tokens=max_length,
                                     stop=stop_words)

    # Create an LLM.
    if model is None:
        model = LLM(
            model=model_path, tokenizer=tokenizer_model_name, tensor_parallel_size=n_gpus, swap_space=8)

    outputs = model.generate(prompts=prompts, sampling_params=sampling_params)

    result = []
    print("Geting results....")
    count = 0
    for output in outputs:
        attempts = []
        for ith_output in output.outputs:
            answer = ith_output.stop_reason
            if answer:
                attempts.append(ith_output.text + answer)
            else:
                # attempts.append(ith_output.text)
                # print(ith_output.text)
                count = count + 1
        if len(attempts) == 0:
            print("No required response...")
        result.append(attempts)
    print(f"Number of reponses not following the instruction: {count}.")
    return result

if __name__ == '__main__':
    print("Testing ...")
    result = llama_forward(None, prompts=["Hello"], model_path="ckpts/LLMs/Meta-Llama-3-8B", n_gpus=2)
    print(result)