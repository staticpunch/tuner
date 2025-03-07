from mmengine.config import read_base

with read_base():
    # Read the required dataset configurations directly from the preset dataset configurations
    from opencompass.configs.datasets.mmlu.mmlu_gen import mmlu_datasets
    from opencompass.configs.datasets.gsm8k.gsm8k_gen import gsm8k_datasets
    from opencompass.configs.datasets.mmlu_pro.mmlu_pro_gen_cdbebf import mmlu_pro_datasets
    from opencompass.configs.datasets.MathBench.mathbench_gen import mathbench_datasets
    from opencompass.configs.datasets.IFEval.IFEval_gen import ifeval_datasets
    from opencompass.configs.datasets.ARC_e.ARC_e_gen import ARC_e_datasets
    from opencompass.configs.datasets.ARC_c.ARC_c_gen import ARC_c_datasets
    from opencompass.configs.datasets.humaneval.deprecated_humaneval_gen_a82cae import humaneval_datasets
    from opencompass.configs.datasets.mbpp.mbpp_gen import mbpp_datasets
    from opencompass.configs.datasets.livecodebench.livecodebench_gen import LCB_datasets

# Concatenate the datasets to be evaluated into the datasets field
# datasets = gsm8k_datasets + math_datasets
arc_template = """
Explain your reasoning for this multiple choice question. After your explanation, you must end with EXACTLY this phrase: "The correct answer is: [letter]" where [letter] is either A, B, C, or D.

Question: {question}
A. {textA}
B. {textB}
C. {textC}
D. {textD}
""".strip()


for i in range(len(ARC_e_datasets)):
    ARC_e_datasets[i]["infer_cfg"]["prompt_template"]["template"] = dict(
        round=[{"role": "HUMAN", "prompt": arc_template}]
    )
    
for i in range(len(ARC_c_datasets)):
    ARC_c_datasets[i]["infer_cfg"]["prompt_template"]["template"] = dict(
        round=[{"role": "HUMAN", "prompt": arc_template}]
    )

mathbench_datasets_en = [
    x for x in mathbench_datasets 
    if (
        "_cn" not in x["abbr"]
        and "cloze" in x["abbr"]
    )
]
mmlu_math = [x for x in mmlu_datasets if any(
    k in x["name"].lower() for k in ("math", "algebra", "calculus")
)] 

mbpp_template=dict(
    round=[
        dict(role='SYSTEM', prompt='You are an expert Python programmer'),
        dict(role='HUMAN', prompt='Write a function to find the similar elements from the given two tuple lists. Your code should pass these tests:\n\n assert similar_elements((3, 4, 5, 6),(5, 7, 4, 10)) == (4, 5)\nassert similar_elements((1, 2, 3, 4),(5, 4, 3, 7)) == (3, 4) \nassert similar_elements((11, 12, 14, 13),(17, 15, 14, 13)) == (13, 14) \n'),
        dict(role='BOT', prompt="[BEGIN]\n 'def similar_elements(test_tup1, test_tup2):\r\n  res = tuple(set(test_tup1) & set(test_tup2))\r\n  return (res)' \n[DONE] \n\n "),

        dict(role='HUMAN', prompt='Write a python function to identify non-prime numbers. Your code should pass these tests:\n\n assert is_not_prime(2) == False \nassert is_not_prime(10) == True \nassert is_not_prime(35) == True \n'),
        dict(role='BOT', prompt="[BEGIN]\n 'import math\r\ndef is_not_prime(n):\r\n    result = False\r\n    for i in range(2,int(math.sqrt(n)) + 1):\r\n        if n % i == 0:\r\n            result = True\r\n    return result' \n[DONE] \n\n "),

        dict(role='HUMAN', prompt='Write a function to find the largest integers from a given list of numbers using heap queue algorithm. Your code should pass these tests:\n\n assert heap_queue_largest( [25, 35, 22, 85, 14, 65, 75, 22, 58],3)==[85, 75, 65] \nassert heap_queue_largest( [25, 35, 22, 85, 14, 65, 75, 22, 58],2)==[85, 75] \nassert heap_queue_largest( [25, 35, 22, 85, 14, 65, 75, 22, 58],5)==[85, 75, 65, 58, 35] \n'),
        dict(role='BOT', prompt="[BEGIN]\n 'import heapq as hq\r\ndef heap_queue_largest(nums,n):\r\n  largest_nums = hq.nlargest(n, nums)\r\n  return largest_nums' \n[DONE] \n\n "),
        dict(role='HUMAN', prompt='{text} Your code should pass these tests:\n\n {test_list}  \n'),
        # dict(role='BOT', prompt='[BEGIN]\n'),
    ],
)
for dataset in mbpp_datasets:
    dataset["infer_cfg"]["prompt_template"]["template"] = mbpp_template

    
datasets = ([]
    + gsm8k_datasets[:] 
    + mathbench_datasets_en
    + mbpp_datasets[:]
    + LCB_datasets
    # + mmlu_math
    + ifeval_datasets[:] 
    + mmlu_datasets[:]
    # + mmlu_pro_datasets[:]
    # + triviaqa_datasets
    # + simpleqa_datasets
    + ARC_e_datasets
    + ARC_c_datasets   
)

# Evaluate models supported by HuggingFace's `AutoModelForCausalLM` using `HuggingFaceCausalLM`
from opencompass.models import HuggingFacewithChatTemplate, VLLMwithChatTemplate

configs_0 = [
    # ("/mnt/md0data/hiennm/logits/logits-guided-merger/results/run_ada", "merge_ada"),
    # ("/mnt/md0data/hiennm/logits/models/baselines/acl-slerp", "usual-slerp"),
    # ("/mnt/md0data/hiennm/logits/models/experts/llama-3.2-3b-base-expert-code/checkpoint-651", "expert-code-3b"),
    # ("/mnt/md0data/hiennm/logits/models/experts/llama-3.2-3b-base-expert-math/checkpoint-540", "expert-math-3b"),
    ("/mnt/md0data/hiennm/logits/models/experts/llama-3.2-3b-wizard-expert-math/checkpoint-264", "math200k-3b"),
    ("/mnt/md0data/hiennm/logits/models/experts/llama-3.2-3b-wizard-expert-math-100k/checkpoint-264", "math100k-3b"),
    # ("/mnt/md0data/hiennm/logits/models/Llama-3.2-3B-Instruct", "it-3b")
    # ("/mnt/md0data/hiennm/logits/logits-guided-merger/results/run_02", "merge_#02"),
    ("/mnt/md0data/hiennm/logits/models/llama-3.2-3b-wizard", "instruct-3b"),
    ("/mnt/md0data/hiennm/logits/models/llama-3.2-3b-math", "numina-3b"),
    # ("/mnt/md0data/hiennm/logits/logits-guided-merger/results/run-math-50k-uniform", "uniform-3b"),
    # ("/mnt/md0data/hiennm/logits/logits-guided-merger/results/run-math-50k-blend", "blend-3b"),
]


configs_1 = [
    ("/mnt/md0data/hiennm/logits/logits-guided-merger/results/run-math-50k-blend-out", "blend-out-3b"),
    ("/mnt/md0data/hiennm/logits/logits-guided-merger/results/run-math-50k-uniform-out", "uniform-out-3b")
]

configs_2 = [
    # ("/mnt/md0data/hiennm/logits/logits-guided-merger/results/run-math-50k-uniform", "uniform-3b"),
    # ("/mnt/md0data/hiennm/logits/logits-guided-merger/results/run-math-50k-blend", "blend-3b"),
    # ('/mnt/md0data/hiennm/logits/logits-guided-merger/results/run-math-50k-uniform-with20k', "uniform-20k-3b")
    ('/mnt/md0data/hiennm/logits/logits-guided-merger/results/run-math-50k-uniform-37', 'uniform-3b-37'),
    ("/mnt/md0data/hiennm/logits/logits-guided-merger/results/sythetic/merge-math-3b-uniform", "synthetic-3b"),
]

configs_3 = [
    # ("/mnt/md0data/hiennm/logits/logits-guided-merger/results/baselines/task_arithmetic", "ta-3b"),
    # ("/mnt/md0data/hiennm/logits/logits-guided-merger/results/baselines/ties_topK_0.1", "ties-3b"),
    # ("/mnt/md0data/hiennm/logits/logits-guided-merger/results/baselines/ties_weight_0.1", "ties-0.1-3b"),
    # ("/mnt/md0data/hiennm/logits/logits-guided-merger/results/baselines/ties_weight_0.2", "ties-0.2-3b"),
    # ("/mnt/md0data/hiennm/logits/logits-guided-merger/results/baselines/ties_weight_0.3", "ties-0.3-3b"),
    # ("/mnt/md0data/hiennm/logits/logits-guided-merger/results/baselines/ties_weight_0.4", "ties-0.4-3b"),
    # ("/mnt/md0data/hiennm/logits/logits-guided-merger/results/baselines/ties_weight_0.5", "ties-0.5-3b"),
    ("/mnt/md0data/hiennm/logits/logits-guided-merger/results/sythetic/merge-math-3b-uniform", "synthetic-3b"),
    ("/mnt/md0data/hiennm/logits/logits-guided-merger/results/sythetic/merge-math-3b-uniform-v2", "synthetic-3b-v2"),
]

configs_4 = [
    ("/mnt/md0data/hiennm/logits/models/llama-3.1-8b-wizard/checkpoint-200", "wizard-8b"),
    # ("/mnt/md0data/hiennm/logits/models/experts/llama-3.1-8b-wizard-expert-math-100k/checkpoint-135", "math-8b"),
    # ("/mnt/md0data/hiennm/logits/logits-guided-merger/results/sythetic/merge-math-8b-uniform", "synthetic-8b"),
]

configs_5 = [
    # ("/mnt/md0data/hiennm/logits/models/llama-3.2-3b-smol", "instruct-3b"),
    ("/mnt/md0data/hiennm/logits/models/smol-experts/llama-3.2-3b-expert-math", "math-3b"),
    ("/mnt/md0data/hiennm/logits/models/smol-experts/llama-3.2-3b-expert-code", "code-3b"),
    ("/mnt/md0data/hiennm/logits/automerger/results/mathcode/merge-math-code-3b-u55", "mathcode-55")
    # ("/mnt/md0data/hiennm/logits/automerger/results/sythetic/merge-math-3b-u19", "IM-3b-u19"),
    # ("/mnt/md0data/hiennm/logits/automerger/results/sythetic/merge-math-3b-u28", "IM-3b-u28"),
    # ("/mnt/md0data/hiennm/logits/automerger/results/sythetic/merge-math-3b-u37", "IM-3b-u37"),
    # ("/mnt/md0data/hiennm/logits/automerger/results/sythetic/merge-math-3b-u46", "IM-3b-u46"),
    # ("/mnt/md0data/hiennm/logits/automerger/results/sythetic/merge-math-3b-u55", "IM-3b-u55"),
]


model_configs = configs_5

models = [
    dict(
        # type=HuggingFacewithChatTemplate,
        type=VLLMwithChatTemplate,
        abbr=model_configs[i][1],
        path=model_configs[i][0],
        # tokenizer_path=model_configs[i][0],
        # tokenizer_kwargs=dict(padding_side='left', truncation_side='left'),
        max_out_len=1024,
        batch_size=200,
        run_cfg=dict(num_gpus=1, ),
        stop_words=['<|end_of_text|>', '<|eot_id|>', '00000'],
        generation_kwargs=dict(temperature=0),
        model_kwargs=dict(tensor_parallel_size=1, gpu_memory_utilization=0.5),
    ) for i in range(len(model_configs))
]