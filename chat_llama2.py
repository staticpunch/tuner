import yaml
from axolotl.utils.dict import DictDefault
config_file = "../examples/llama-2/qlora.yml"
with open(config_file, encoding="utf-8") as file:
    cfg: DictDefault = DictDefault(yaml.safe_load(file))

from transformers import LlamaForCausalLM, LlamaTokenizer, LlamaConfig
import torch
import os
from peft import PeftModel

os.environ["CUDA_DEVICE_ORDER"]="PCI_BUS_ID"
os.environ["CUDA_VISIBLE_DEVICES"]="0,1"

torch_dtype = torch.bfloat16
device_map = {"": int(os.environ.get("CUDA_DEVICE") or 0)}

tokenizer = LlamaTokenizer.from_pretrained(
    cfg.base_model_config,
    trust_remote_code=cfg.trust_remote_code or False,
    use_fast=True,
)

model = LlamaForCausalLM.from_pretrained(
    cfg.base_model,
    config=LlamaConfig.from_pretrained(
        cfg.base_model_config,
    ),
    device_map=device_map,
    torch_dtype=torch_dtype
)
model = PeftModel.from_pretrained(model, cfg.output_dir)

from axolotl.prompters import ShareGPTPrompter, PromptStyle
from axolotl.prompters import IGNORE_TOKEN_ID
from axolotl.prompt_tokenizers import PromptTokenizingStrategy, ShareGPTPromptTokenizingStrategy
from axolotl.prompt_tokenizers import tokenize_prompt_default, parse_tokenized_to_result
from typing import Dict, List, Tuple, Union

class MyConversation:
    def __init__(self, convo=None, roles=["human", "gpt"]):
        self.convo = {"conversations": []}
        if convo: self.convo = convo
        self.roles = roles
            
    def add_turn(self, turn):
        assert all(x in turn.keys() for x in ["from", "value"]), "Wrong turn format"
        assert turn["from"] in self.roles, "Wrong role"
        self.convo["conversations"].append(turn)

    def get_conversations(self):
        return self.convo

    def update_assistant_turn(self, message):
        assert self.convo["conversations"][-1]["from"] == self.roles[1], "Only update assistant role"
        self.convo["conversations"][-1]["value"] = message
        
prompter = ShareGPTPrompter(prompt_style=PromptStyle.CHAT.value) # chat
tokenizer_strategy = ShareGPTPromptTokenizingStrategy(
    prompter, 
    tokenizer, 
    train_on_inputs=cfg.train_on_inputs,
    sequence_len=cfg.sequence_len,
)

from transformers import GenerationConfig, TextStreamer
def get_answer(dialog, max_new_tokens=1024):
    # input_ids = tokenizer(prompt, return_tensors="pt")["input_ids"].to(model.device)
    inputs = tokenizer_strategy.tokenize_prompt(dialog.get_conversations())
    input_ids = inputs["input_ids"]
    while input_ids[-1] == tokenizer.eos_token_id:
        input_ids.pop()
    space_token_id = tokenizer.encode(" ")[1]
    if input_ids[-1] != space_token_id:
        input_ids.append(space_token_id)
    input_ids = torch.tensor([input_ids], device=model.device)

    model.eval()
    with torch.no_grad():
        generation_config = GenerationConfig(
            repetition_penalty=1.1,
            max_new_tokens=max_new_tokens,
            temperature=0.2,
            top_p=0.95,
            top_k=40,
            # bos_token_id=tokenizer.bos_token_id,
            # eos_token_id=tokenizer.eos_token_id,
            # eos_token_id=0, # for open-end generation.
            pad_token_id=tokenizer.pad_token_id,
            do_sample=True,
            use_cache=True,
            return_dict_in_generate=True,
            output_attentions=False,
            output_hidden_states=False,
            output_scores=False,
        )
        streamer = TextStreamer(tokenizer, skip_prompt=True)
        generated = model.generate(
            inputs=input_ids,
            generation_config=generation_config,
            streamer=streamer,
        )
        
    gen_tokens = generated["sequences"].cpu()[:, len(input_ids[0]):]
    output = tokenizer.batch_decode(gen_tokens)[0]
    output = output.split(tokenizer.eos_token)[0]
    return output.strip()

def chat():
    dialog = MyConversation()
    while True:
        question = input("\nUSER:\n")
        dialog.add_turn({"from": dialog.roles[0], "value": question})
        dialog.add_turn({"from": dialog.roles[1], "value": " "})
        print("ASSISTANT: ", end="")
        message = get_answer(dialog)
        dialog.update_assistant_turn(message)

if __name__ == "__main__":
    chat()
