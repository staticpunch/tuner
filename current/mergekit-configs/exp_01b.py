# exp_01b.py
from checkpoints import checkpoints

OUTPUT_DIR = "exp_01b"
EXP_01a_DIR = "exp_01a"
CONFIG = f"""
models:
  - model: {checkpoints.INSTRUCT}
    parameters:
      weight: 1.0
  - model: {EXP_01a_DIR}
    parameters:
      weight: 1.0

merge_method: ties
base_model: {checkpoints.BASE}
parameters:
  normalize: true
dtype: bfloat16

output_dir: {OUTPUT_DIR}
""".strip()

print(CONFIG)
