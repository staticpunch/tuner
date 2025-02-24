# exp_00b.py
from checkpoints import checkpoints

EXP_00a_DIR = "exp_00a"
OUTPUT_DIR = "exp_00b"
CONFIG = f"""
models:
  - model: {checkpoints.INSTRUCT}
    parameters:
      weight: 1
  - model: {EXP_00a_DIR}
    parameters:
      weight: 1

merge_method: linear
parameters:
  normalize: true
dtype: bfloat16

output_dir: {OUTPUT_DIR}
""".strip()

print(CONFIG)
