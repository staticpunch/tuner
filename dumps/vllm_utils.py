import json
import os
import aiohttp
import asyncio
import traceback
from collections.abc import Iterable

from transformers import AutoTokenizer

from tqdm.asyncio import tqdm

from abc import ABC, abstractmethod

os.environ["http_proxy"] = ""
os.environ["https_proxy"] = ""



class BaseModel(ABC):
    
    model_hub = "/workspace/home/chieunq/LUAS-main/ckpts/full_models/"
    
    def __init__(
        self,
        endpoint_ip: str = "",
        model_name: str = "",
        eos_token: str = None,
        system_prompt: str = "",
        assistant_prompt_prefix: str = "",
    ):
        self.endpoint_ip = endpoint_ip
        self.model_name = model_name
        self.tokenizer = self.get_tokenizer()
        self.tokenizer.add_eos_token = False
        self.tokenizer.padding_side = "left"
        if eos_token:
            self.tokenizer.eos_token = eos_token

        self.system_prompt = system_prompt
        self.assistant_prompt_prefix = assistant_prompt_prefix
        
        
    def get_tokenizer(self):
        return AutoTokenizer.from_pretrained(
            os.path.join(self.model_hub, self.model_name),
            trust_remote_code=True
        )
    
    
    @abstractmethod
    def format_request_payload(self, prompt: str, max_len: int) -> dict:
        pass
    
    
    async def get_answer(
            self, 
            session, 
            user_prompt, 
            max_len=1024):
        
        if self.system_prompt:
            prompt = self.tokenizer.apply_chat_template(
                [
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": user_prompt},
                ], tokenize=False, add_generation_prompt=True
            ) + self.assistant_prompt_prefix
        else:
            prompt = self.tokenizer.apply_chat_template(
                [
                    {"role": "user", "content": user_prompt},
                ], tokenize=False, add_generation_prompt=True
            ) + self.assistant_prompt_prefix

        headers = {
            "Content-Type": "application/json",
        }
        data = self.format_request_payload(prompt, max_len)
        try:
            async with session.post(self.endpoint_ip, headers=headers, json=data, timeout=600000) as resp:
                try:
                    resp = await resp.json()
                    # print(resp)
                    return prompt, resp["choices"][0]["text"]
                except:
                    resp = await resp.text()
                    return prompt, resp
        except:
            return prompt, "Failed: " + str(traceback.format_exc())
    
    
    async def generate_async(
        self, 
        user_prompts: Iterable[str],
        max_len: int = 1024,
        output_file: str = None,
    ):
        async with asyncio.BoundedSemaphore(8):
            session_timeout = aiohttp.ClientTimeout(total=None)
            async with aiohttp.ClientSession(timeout=session_timeout) as session:
                tasks = []
                for user_prompt in user_prompts:
                    tasks.append(asyncio.ensure_future(
                        self.get_answer(
                            session, 
                            user_prompt,
                            max_len)
                    ))
                results = await tqdm.gather(*tasks)

        if output_file:
            with open(output_file, "w") as f:
                for user_prompt, (model_input, model_output) in zip(dataset, results):
                    sample["model_output"] = output
                    sample["input_prompt"] = input_prompt
                    f.write(json.dumps({
                        "user_prompt": user_prompt,
                        "model_input": model_input,
                        "model_output": model_output
                    }, ensure_ascii=False)+"\n")

        return [model_output for _, model_output in results]
    
    
    
    


class VllmModel(BaseModel):

    def format_request_payload(self, prompt: str, max_len: int) -> dict:
        return {
            "model": self.model_name,
            "prompt": prompt, 
            "n": 1,
            "best_of": 1,
            "use_beam_search": False,
            "max_tokens": max_len,
            "repetition_penalty": 1.0,
            "temperature": 0,
            "top_p": 0.9,
            "top_k": -1,
            "stop": [self.tokenizer.eos_token]
        }
        # return {"model": self.model_name,
        #     "prompt": prompt, "temperature":0,
        #        "stop":["<|eot_id|>", "<|end_of_text|>"], "n":1, "max_tokens":2048}
