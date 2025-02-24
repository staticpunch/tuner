# exp_00a.py
from checkpoints import checkpoints

OUTPUT_DIR = "exp_00a"
CONFIG = f"""
models:
  - model: {checkpoints.CKPT_1}
    parameters:
      weight: 1
  - model: {checkpoints.CKPT_2}
    parameters:
      weight: 1
  - model: {checkpoints.CKPT_3}
    parameters:
      weight: 1

merge_method: linear
parameters:
  normalize: true
dtype: bfloat16

output_dir: {OUTPUT_DIR}
""".strip()

print(CONFIG)
