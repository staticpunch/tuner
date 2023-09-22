from transformers import LlamaForCausalLM, LlamaTokenizer, LlamaConfig
from datasets import load_dataset
import torch
import os
import pandas as pd
import json
from peft import PeftModel
from axolotl.prompters import AlpacaPrompter, PromptStyle

torch_dtype = torch.bfloat16
device_map = {"": 0}

# model_id = "NousResearch/Llama-2-7b-hf"
# model_id = "nguyenthanhdo/vhac_model"
model_id = "minhbui/viettel_v1_mix_100k"
# peft_dolphin = "nguyenthanhdo/dolphin_noprob"

tokenizer = LlamaTokenizer.from_pretrained(model_id)
model = LlamaForCausalLM.from_pretrained(
    model_id,
    config=LlamaConfig.from_pretrained(model_id),
    device_map=device_map,
    torch_dtype=torch_dtype,
    load_in_8bit=True
)
# model = PeftModel.from_pretrained(model, peft_dolphin)
# model = model.merge_and_unload()

from transformers import GenerationConfig, TextStreamer
def get_answer(prompt, max_new_tokens=1024):
    input_ids = tokenizer(prompt, return_tensors="pt")["input_ids"].to(model.device)
    model.eval()
    with torch.no_grad():
        generation_config = GenerationConfig(
            repetition_penalty=1.13,
            max_new_tokens=max_new_tokens,
            temperature=0.4,
            top_p=0.95,
            # top_k=20,
            # bos_token_id=tokenizer.bos_token_id,
            # eos_token_id=tokenizer.eos_token_id,
            # eos_token_id=0, # for open-end generation.
            pad_token_id=tokenizer.pad_token_id,
            do_sample=False,
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

qvi = pd.read_csv("../data/data_public_question.csv")["question"].to_list()
retrieved = load_dataset("json", data_files="../data/retrieved_300_en_sbert.jsonl")["train"]

prompter = AlpacaPrompter(prompt_style=PromptStyle.INSTRUCT.value)
instruction = 'You are an AI assistant. Provide a answer in detailed length that user don’t need to search outside to understand the answer. The answer should be exact and extractive.'
input_template = "Hỏi: {question}\n{context}\nĐáp: "

with open("../data/results.jsonl", "w") as f:
    for i, rtr in enumerate(retrieved):
        question, context, _ = rtr.values()
        input = input_tempalte.format(question=question, context=context)
        prompt = prompter.build_prompt(instruction=instruction, input=input, output="").__next__()
        output = get_answer(prompt)
        d = json.dumps(dict(quest_id=i, answer_predict=output)) + "\n"
        f.write(d)
      
