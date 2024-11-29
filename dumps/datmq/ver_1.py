#### SEP ####
import os
import re
import sys
import json
import logging
import asyncio
import aiohttp
import pickle
import numpy as np
import nest_asyncio

from tqdm.auto import tqdm
from dotenv import load_dotenv
from datasets import Dataset
from datasets import load_dataset
from collections import defaultdict
from langchain_openai import ChatOpenAI

#### SEP ####
## UltraChat

file_path = "/workspace/home/NLP_CORE/llm_instruct/data_ready_to_train/09_08_24/en_ultrachat_50k/en_ultrachat_50k.jsonl"
data = [json.loads(line) for line in open(file_path, "r")]
dataset = Dataset.from_list(data)

def preprocess(examples):
    results = defaultdict(list)
    results['messages'] = examples['messages']
    messages = examples['messages']
    for message in messages:
        if message[0]['role'] == 'user':
            results['instruction'].append(message[0]['content'])
            results['length'].append(len(message[0]['content']))
        if message[1]['role'] == 'assistant':
            results['answer'].append(message[1]['content'])
        results['turns_count'].append(len(message))
    return results

base_dataset = dataset.map(preprocess, batched=True, remove_columns=dataset.column_names)
eval_dataset = base_dataset.sort(column_names=['length'], reverse=True).select(range(25))
base_dataset, eval_dataset

#### SEP ####
data = [json.loads(line) for line in open("alpaca.jsonl")]
dataset = Dataset.from_dict(new_data)
base_dataset = dataset
eval_dataset = base_dataset.shuffle().select(range(25))
base_dataset, eval_dataset
base_dataset.shuffle()[0]['instruction']

#### SEP ####
BASE_PLAN = """You are an Instruction Generator that creates completely new instruction in Vietnamese language based on a provided example instruction. 
Please follow the steps below to generate the new instruction in Vietnamese.

Step 1: Carefully read the "Example Instruction." List all possible ways to create a new instruction that matches or exceeds the difficulty level, ensuring that the context and language are in Vietnamese, easily understandable for a Vietnamese audience and in the same domain with the "Example Instruction". If the "Example Instruction" includes any additional context, the new instruction must also incorporate generated context in Vietnamese.

Step 2: Please create a detailed plan using the "Methods List" generated in Step 1 to create the "New Instruction". The plan should incorporate multiple methods from the "Methods List".

Step 3: Please execute the plan step by step and provide the "New Instruction".

Step 4: Please carefully review the "New Instruction" and identify any unreasonable parts. Ensure that the "New Instruction" is a question or a tasks for the AI assistant to fullfill, is a completely new version but still in the same domain with the "Example Instruction" and in Vietnamese. Just provide the finally new instruction without any explanation."""

FORMAT_NEW_INSTRUCTION = """Please provide the details for each step in English, adhering strictly to the following format. The finally new instruction MUST be a question or a tasks for the AI assistant to fullfill and be enclosed between <Finally New Instruction> and </Finally New Instruction>:
<Step n>Description of step n here in English</Step n>
<Finally New Instruction>The final new instruction here in Vietnamese, with appropriate Vietnamese context</Finally New Instruction>"""

FEEDBACK_PROMPT = """The following list presents cases where an instruction has been transformed into a completely different Vietnamese version. For each case, ##Example Instruction## refers to the original example, and ##New Instruction## is the newly generated Vietnamese instruction.

Please identify which cases succeeded or failed in generating new instructions, including their case IDs and reasons for their status in English. For each case, analyze any failures by providing a detailed explanation in English.
- A case is successful if the new instructions are in Vietnamese, contain relevant context, in the same domain but DIFFER entirely from the ##Example Instruction##, match or exceed the example's difficulty, and can be effectively addressed by the AI assistant.
- A case is considered a failure if the new instructions are merely translations, are overly simplified, contain irrelevant Vietnamese context, not in the same domain with the example instruction or lack sufficient information for the AI assistant to complete the task.
Additionally, please provide a bullet point list of changes needed to address any issues in the cases in English. If there are no issues, please suggest some improvements to enhance the overall quality.

Please response in English and strictly follow this format:
##Case##: <Case id here>
##Reason##: <The reason for the failure or success here in english>

...

##Need to change##:
<Things need to improve here in ENGLISH>

##List of cases##:"""

OPTIMIZE_PROMPT = """I will provide you with the method for generate the above Vietnamese instructions. You need to optimize this method using the #Need to change# provided, ensuring it does not negatively affect performance in other cases, and that the instruction generated by the optimized method is at least as effective as the original method.
The optimized method must adhere strictly to the same format as the original method and the optimized method can only add 30 to 50 words into the orginal method.
Please provide the optimized method in English, following the format below. 
```Optimized Method\n<English Optimized Method Here>\n```

#Original method#:"""

EVALUATE_PROMPT = """You are a Teacher with the task of evaluating the correctness of the instruction and its corresponding answer. There are 50 cases, and for each case, you are given an instruction and its corresponding answer. Assign a score of -1 or 1 for each case using the following stricter rules:
- Assign a score of 0 if the Instruction has any issues. An instruction is considered a failure if it cannot be solved fully in the Answer, lacks sufficient information, contains unnecessary or irrelevant details, is ambiguous, or cannot be clearly understood by a Vietnamese person. Even minor issues should lead to a score of 0.
- Assign a score of 1 only if the case is flawless. A case is successful if the instruction is clearly written in Vietnamese and the answer fully and accurately solves the problem without any confusion or missing information. Even minor flaws should prevent a score of 1.
Please reply strictly in the following format without any explanation:
##Case n##: Score here without any explaination

##List of cases##:"""
