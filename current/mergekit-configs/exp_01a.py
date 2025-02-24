# exp_01a.py
from checkpoints import checkpoints

OUTPUT_DIR = "exp_01a"
CONFIG = f"""
models:
  - model: {checkpoints.CKPT_1}
    parameters:
      weight: 1.0
  - model: {checkpoints.CKPT_2}
    parameters:
      weight: 1.0
  - model: {checkpoints.CKPT_3}
    parameters:
      weight: 1.0

merge_method: ties
base_model: {checkpoints.INSTRUCT}
parameters:
  normalize: true
dtype: bfloat16

output_dir: {OUTPUT_DIR}
""".strip()

print(CONFIG)
