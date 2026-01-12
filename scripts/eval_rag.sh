export CUDA_VISIBLE_DEVICES=6
export HF_HOME=huggingface_cache_folder
export VLLM_WORKER_MULTIPROC_METHOD=spawn

task_type=quality
ecpt=1
top_k=16
prompt_path=outputs/prompt_quality_zh.json

python evaluation.py \
    --eval_func eval_quality_qa_with_rag \
    --model_path ckpts/llm_models/crypto_quality-lr5e-06-rr0.1-epochs2-bs16-wd0.01-warmup0.05-MetaLlama38B \
    --tokenizer_model_name ckpts/llm_models/Meta-Llama-3-8B \
    --eval_temperature 0.1 \
    --embedding_model_path sentence-transformers/all-MiniLM-L6-v2 \
    --text_split_strategy recursive \
    --chunk_size 1024 \
    --chunk_overlap 0 \
    --retrieval_max_k 128 \
    --retrieval_top_k 128 \
    --rerank_model_path mixedbread-ai/mxbai-rerank-large-v1 \
    --rerank_top_k ${top_k} \
    --retrieved_chunk_order best_last \
    --task_type ${task_type} \
    --synthesized True \
    --encrypt ${ecpt} \
    --prompt_path ${prompt_path} \
    --num_gpu 1