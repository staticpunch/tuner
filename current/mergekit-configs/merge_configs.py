from dataclasses import dataclass


@dataclass(frozen=True)  # frozen=True makes it immutable like Enum
class Checkpoints:
    BASE: str = "llama-70B-base"
    INSTRUCT: str = "llama-70B-instruct"
    REASONER: str = "distill-r1"
    CKPT_1: str = "0.5epoch"
    CKPT_2: str = "1.0epoch"
    CKPT_3: str = "1.5epoch"


checkpoints = Checkpoints()

# 1. Merge multiple checkpoints during the training runs.
OUTPUT_00a = "exp_00a"
CONFIG_00a = f"""
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

output_dir: {OUTPUT_00a}
""".strip()

OUTPUT_00b = "exp_00b"
CONFIG_00b = f"""
models:
  - model: {checkpoints.INSTRUCT}
    parameters:
      weight: 1
  - model: {OUTPUT_00a}
    parameters:
      weight: 1

merge_method: linear
parameters:
  normalize: true
dtype: bfloat16

output_dir: {OUTPUT_00b}
"""

OUTPUT_00c = "exp_00c"
CONFIG_00c = f"""
models:
  - model: {checkpoints.INSTRUCT}
  - model: {OUTPUT_00a}

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

output_dir: {OUTPUT_00c}
"""


# 2. First TIES multiple checkpoits, then merge back with the BASE.
OUTPUT_01a = "exp_01a"
CONFIG_01a = """
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

output_dir: {OUTPUT_01a}
"""

OUTPUT_01b = "exp_01b"
CONFIG_01b = """
models:
  - model: {checkpoints.INSTRUCT}
    parameters:
      weight: 1.0
  - model: {OUTPUT_01a}
    parameters:
      weight: 1.0

merge_method: ties
base_model: {checkpoints.BASE}
parameters:
  normalize: true
dtype: bfloat16

output_dir: {OUTPUT_01b}
"""


OUTPUT_01c = "exp_01c"
CONFIG_01c = """
models:
  - model: {checkpoints.INSTRUCT}
  - model: {OUTPUT_01a}

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

output_dir: {OUTPUT_01c}
"""

# 3. Maybe SCE. The fusion method.
