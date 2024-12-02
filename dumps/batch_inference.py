import json
import os
import requests
import aiohttp
import asyncio
import traceback

from tqdm.asyncio import tqdm

from transformers import AutoTokenizer, AutoConfig, LlamaTokenizer
from transformers import GenerationConfig, TextStreamer

from datasets import load_from_disk, Dataset


os.environ["http_proxy"] = ""
os.environ["https_proxy"] = ""

print("="*56)
print("="*20+" LFG TGI "+"="*20)
print("="*56)

tgi_ip = "http://localhost:9002/"

def get_tokenizer(tgi_ip: str):
    print("TGI_ADDRESS: "+ tgi_ip)
    # tokenizer
    info = requests.get(tgi_ip+"info")
    info.raise_for_status()
    if info.headers["content-type"].strip().startswith("application/json"):
        info = info.json()
    if "checkpoint" in info["model_id"]:
        model_name = "/".join(info["model_id"].split("/")[-2:])
    else: 
        model_name = info["model_id"].split("/")[-1]
    model_id = "/home/NLP_CORE/HUB_LLM/" + model_name
    print("MODEL_PATH: "+model_id)
    tokenizer = AutoTokenizer.from_pretrained(
        model_id,
        trust_remote_code=True
    )
    return model_name, tokenizer

model_name, tokenizer = get_tokenizer(tgi_ip)
tokenizer.eos_token = "<|eot_id|>" # for llama3-Instruct only

max_seq_len = 4096
max_input_len = 8192
max_new_tokens = 4096

print(f"MAX_SEQ_LEN: {max_seq_len}")
print(f"MAX_INPUT_LEN: {max_input_len}")
print(f"MAX_NEW_TOKENS: {max_new_tokens}")

DEFAULT_SYS_MES = "Bạn là một chatbot hữu ích. Hãy luôn trả lời bằng tiếng Việt."
DEFAULT_ASSISTANT_PREFIX = ""
async def generate(
    session, 
    user_message,
    system_prompt=DEFAULT_SYS_MES,
    assistant_prefix=DEFAULT_ASSISTANT_PREFIX,
    max_new_tokens=1024
):
    prompt = tokenizer.apply_chat_template([
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_message},
        {"role": "assistants", "content": assistant_prefix},
    ], tokenize=False).strip().removesuffix(tokenizer.eos_token)

    headers = {
        "Content-Type": "application/json",
    }
    data = {
        'inputs': prompt,
        'parameters': {
            'max_new_tokens': max_new_tokens,
            'repetition_penalty': 1.0,
            'do_sample': False,
            'use_cache': True,
            'stop': [
                "<|start_header_id|>", 
                "<|end_header_id|>", 
                "<|eot_id|>", 
                "<|reserved_special_token|>"
            ], # for llama3-instruct
        },
    }
    try:
        async with session.post(
            tgi_ip + 'generate', 
            headers=headers, 
            json=data, 
            timeout=600
        ) as resp:
            resp = await resp.json()
            return prompt, resp
    except Exception as err:
        error_str = "Failed: " + str(traceback.format_exc())
        return prompt, error_str


async def batch_inference(prompts):
    async with asyncio.BoundedSemaphore(128):
        session_timeout = aiohttp.ClientTimeout(total=None)
        async with aiohttp.ClientSession(timeout=session_timeout) as session:
            tasks = []
            for prompt in prompts:
                tasks.append(asyncio.ensure_future(
                    generate(
                        session, 
                        user_message=prompt,
                        max_new_tokens=4096
                    )
                ))
            results = await asyncio.gather(*tasks)
            # results = await tqdm.gather(*tasks)
    return results
