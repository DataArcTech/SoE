from torch.utils.data import Dataset
from typing import Dict
import numpy as np
import torch

def _get_bin(task_name: str, split: str, model_name='deepseek-chat', synthesized = False):
    assert task_name in ['quality', 'rehersal', 'instruct', 'judge']
    bin_data_dir = 'data/dataset/bins'
    if synthesized:
        bin_type='syn'
    else:
        bin_type='ori'
    implemented_quality_split = {
        'entigraph': f'{bin_data_dir}/quality_all-entigraphgpt-4o-mini.bin',
    }
    implemented_judge_split = {
        'entigraph': f'{bin_data_dir}/{task_name}-{bin_type}-all-entigraph{model_name}.bin',
    }
    implemented_rehersal_split = {
        'rpj-train': f'{bin_data_dir}/_datasets_togethercomputer___red_pajama_data_1_t_sample_train.bin',
        'rpj-test': f'{bin_data_dir}/_datasets_togethercomputer___red_pajama_data_1_t_sample_test.bin'
    }
    implemented_instruct_split = {
        'ultrachat-train': f'{bin_data_dir}/ultrachat_train.bin',
        'ultrachat-test': f'{bin_data_dir}/ultrachat_test.bin'
    }
    if task_name == 'quality':
        assert split in implemented_quality_split
        return implemented_quality_split[split]
    elif task_name == 'rehersal':
        assert split in implemented_rehersal_split
        return implemented_rehersal_split[split]
    elif task_name == 'instruct':
        assert split in implemented_instruct_split
        return implemented_instruct_split[split]
    if task_name == 'judge':
        print(implemented_judge_split[split])
        assert split in implemented_judge_split
        return implemented_judge_split[split]
    else:
        raise NotImplementedError(f"Task {task_name} is not implemented")


class _MemmapDataset(Dataset):
    def __init__(self, block_size: int, bin_file: str, subsample_ratio: float):
        self.block_size = block_size
        self.ids = np.memmap(bin_file, dtype=np.int32, mode='r')
        self.ids = self.ids[:int(len(self.ids)*subsample_ratio)]

    def __len__(self):
        return int(len(self.ids)/self.block_size)

    def __getitem__(self, i) -> Dict[str, torch.Tensor]:
        assert i < len(self)
        start_ind = i*self.block_size
        end_ind = (i+1)*self.block_size
        x_id = self.ids[start_ind:end_ind].copy()
        return dict(input_ids=torch.from_numpy(x_id).long(),
                    labels=torch.from_numpy(x_id).long())

class CPTDataset(_MemmapDataset):
    def __init__ (self, block_size: int, rehersal_rate: float,
                 subsample_ratio: float, task_name:str, model_name='gpt-mini-4o', synthesized=True):
        assert rehersal_rate <= 1.0
        self.rehersal_rate = rehersal_rate
        self.rehersal_data = _MemmapDataset(block_size, _get_bin('rehersal', 'rpj-train'), 1.0)
        super().__init__(block_size,
                            _get_bin(task_name, 'entigraph', model_name, synthesized),
                            subsample_ratio)

    def __len__(self):
        return super().__len__()

    def __getitem__(self, i: int) -> Dict[str, torch.Tensor]:
        if np.random.rand() < self.rehersal_rate:
            idx = np.random.randint(len(self.rehersal_data))
            return self.rehersal_data[idx]
        else:
            return super().__getitem__(i)

def get_task_data_module(task_name: str,
                         block_size: int,
                         rehersal_rate: float,
                         subsample_ratio: float,
                         syn_model_name = 'gpt-mini-4o',
                         synthesized = True,
                         **kwargs):
    if task_name == 'quality':
        train = CPTDataset(block_size, rehersal_rate, subsample_ratio, task_name, syn_model_name, synthesized)
        val = _MemmapDataset(block_size, _get_bin('rehersal', 'rpj-test'), 1.0)
        return dict(train_dataset=train, eval_dataset=val)
    if task_name == 'instruct':
        train = _MemmapDataset(block_size, _get_bin('instruct', 'ultrachat-train'), 1.0)
        val = _MemmapDataset(block_size, _get_bin('instruct', 'ultrachat-test'), 1.0)
        return dict(train_dataset=train, eval_dataset=val)
    if task_name == 'judge':
        train = CPTDataset(block_size, rehersal_rate, subsample_ratio, task_name, syn_model_name, synthesized)
        val = _MemmapDataset(block_size, _get_bin('rehersal', 'rpj-test'), 1.0)
        return dict(train_dataset=train, eval_dataset=val)
    
    else:
        raise NotImplementedError(f"Task {task_name} is not implemented")


if __name__ == '__main__':
    from transformers import AutoTokenizer
    # Qwen/Qwen2.5-7B, meta-llama/Meta-Llama-3-8B
    tokenizer = AutoTokenizer.from_pretrained("Qwen/Qwen2.5-7B", use_fast=True)
    tokenizer.model_max_length=2**20 # this is to hide the token_len>128K wraning

    block_size = 2048
    rehersal_rate = 0.1
    subsample_ratio = 1.0
    task_name = 'judge'
    syn_model_name = 'deepseek-chat'
    data_module = get_task_data_module(task_name, block_size,
                                       rehersal_rate, subsample_ratio, syn_model_name, synthesized=True)
    for example in data_module['train_dataset']:
        print(tokenizer.decode(example['input_ids']))
        import pdb; pdb.set_trace()