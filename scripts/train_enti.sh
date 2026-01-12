chmod 777 scripts/train.sh
export HF_HOME=huggingface_cache_folder
./scripts/train.sh \
    --lr 5e-06 \
    --rr 0.1 \
    --epochs 2 \
    --bs 16 \
    --wd 0.01 \
    --warmup 0.05 \
    --task_name judge