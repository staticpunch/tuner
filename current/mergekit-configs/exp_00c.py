# exp_00c.py
from checkpoints import checkpoints

OUTPUT_DIR = "exp_00c"
EXP_00a_DIR = "exp_00a"
CONFIG = f"""
models:
  - model: {checkpoints.INSTRUCT}
  - model: {EXP_00a_DIR}

merge_method: slerp
base_model: {checkpoints.INSTRUCT}
parameters:
  t:
    - filter: self_attn
      value: [0, 0.3, 0.5, 0.7, 1]
    - filter: mlp
      value: [1, 0.7, 0.5, 0.3, 0]
    - value: 0.5
dtype: bfloat16

output_dir: {OUTPUT_DIR}
""".strip()

print(CONFIG)
