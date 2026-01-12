export CUDA_VISIBLE_DEVICES=2
export HF_HOME=huggingface_cache_folder
export VLLM_WORKER_MULTIPROC_METHOD=spawn
model_name=llama_factory/qwen2.5_7b_encrypt_judge_all_v1.1
task_type=judge
syn=True
ecpt=1
cntxt=False
prompt_path=outputs/prompt_all_en.json
# Qwen/Qwen2.5-7B
model_path=ckpts/llm_models/org-judge-lr5e-06-rr0.1-epochs2-bs16-wd0.01-warmup0.05-Qwen2.57B
python evaluation.py \
    --model_path ckpts/llm_models/${model_name} \
    --tokenizer_model_name Qwen/Qwen2.5-7B \
    --task_type ${task_type} \
    --synthesized ${syn} \
    --encrypt ${ecpt} \
    --num_gpu 1 \
    --prompt_path ${prompt_path} \
    --with_context False
