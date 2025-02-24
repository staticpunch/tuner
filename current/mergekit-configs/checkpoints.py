# checkpoints.py
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
