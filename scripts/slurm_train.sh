#!/bin/bash
#SBATCH --job-name Train-Crypto-Enti
#SBATCH --output outputs/slurm_result.out   ## filename of the output; the %j is equivalent to jobID; default is slurm-[jobID].out
#SBATCH -e outputs/slurm_result.err   
#SBATCH --partition=batch  ## the partitions to run in (comma seperated)
#SBATCH --ntasks=1  ## number of tasks (analyses) to run
#SBATCH --gpus-per-task=1 # number of gpus per task
#SBATCH --gres=gpu:8
#SBATCH --mem-per-gpu=100000M # Memory allocated for the job
#SBATCH --time=1-00:00:00  ## time for analysis (day-hour:min:sec)
#SBATCH --cpus-per-task=256 

source /home/liuhonghao/anaconda/etc/profile.d/conda.sh
conda activate scp

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