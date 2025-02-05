#!/bin/bash#
python3 finetune.py --data_path "data/vi_merged.jsonl" --base_model "bigscience/bloom-7b1" --model_family "bloom" \
  --finetune_method "qlora" --lora_r 8 --lora_alpha 32 --output_dir "output" \
    --batch_size=128 --micro_batch_size 4 --cutoff_len 512 --num_epochs 1 --kbit "4bit" \
