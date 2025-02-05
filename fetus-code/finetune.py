import os 
os.environ["CUDA_DEVICE"] = os.environ.get("CUDA_DEVICE") or "0"

import sys
import fire
import torch
import transformers
from datasets import load_dataset

from peft import (
    TaskType,
    LoraConfig,
    PrefixTuningConfig,
    get_peft_model,
    get_peft_model_state_dict,
    prepare_model_for_kbit_training,
    set_peft_model_state_dict,
)
from peft.utils.other import TRANSFORMERS_MODELS_TO_LORA_TARGET_MODULES_MAPPING as MODULES_MAPPING
from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig
from transformers.trainer_utils import PREFIX_CHECKPOINT_DIR
from transformers.trainer_callback import TrainerCallback
from transformers.trainer_utils import PREFIX_CHECKPOINT_DIR

class SavePeftModelCallback(TrainerCallback):
    def on_save(self, args, state, control, **kwargs):
        checkpoint_folder = os.path.join(
            args.output_dir, f"{PREFIX_CHECKPOINT_DIR}-{state.global_step}"
        )       

        peft_model_path = os.path.join(checkpoint_folder, "adapter_model")
        kwargs["model"].save_pretrained(peft_model_path)

        pytorch_model_path = os.path.join(checkpoint_folder, "pytorch_model.bin")
        if os.path.exists(pytorch_model_path):
            os.remove(pytorch_model_path)
        return control

class SavePeftModelCallback(transformers.TrainerCallback):
    def save_model(self, args, state, kwargs):
        if state.best_model_checkpoint is not None:
            checkpoint_folder = os.path.join(state.best_model_checkpoint, "pt_lora_model")
        else:
            checkpoint_folder = os.path.join(args.output_dir, f"{PREFIX_CHECKPOINT_DIR}-{state.global_step}")

        peft_model_path = os.path.join(checkpoint_folder, "pt_lora_model")
        kwargs["model"].save_pretrained(peft_model_path)
#         kwargs["tokenizer"].save_pretrained(peft_model_path)

    def on_save(self, args, state, control, **kwargs):
        self.save_model(args, state, kwargs)
        return control

    def on_train_end(self, args, state, control, **kwargs):
        peft_model_path = os.path.join(args.output_dir, "pt_lora_model")
        kwargs["model"].save_pretrained(peft_model_path)
#         kwargs["tokenizer"].save_pretrained(peft_model_path)

def make_prompt(instruction):
    prompt = f"""Hãy viết một phản hồi thích hợp cho chỉ dẫn dưới đây.

### Instruction:
{instruction}

### Response:"""
    return prompt

def generate_prompt(data_point):
    question = data_point["prompt"].strip()
    answer = data_point["response"].strip()
    return f"{make_prompt(question)}\n{answer}"

def train(
    data_path: str = "data/vi_merged.jsonl",
    base_model: str = "VietAI/gpt-j-6B-vietnamese-news",
    output_dir: str = "ChitChat",

    # training hyperparams
    batch_size: int = 128,
    micro_batch_size: int = 2,
    num_epochs: int = 1,
    learning_rate: float = 3e-4,
    cutoff_len: int = 256,
    val_set_size: int = 0,

    ## Select finetune method
    finetune_method: str = "qlora", # lora prefix

    # prefix tuning hyperparams
    # Tham khảo https://github.com/huggingface/peft/blob/main/examples/causal_language_modeling/peft_prefix_tuning_clm.ipynb
    num_virtual_tokens: int = 32,

    # lora hyperparams
    lora_r: int = 8,
    lora_alpha: int = 32,
    lora_dropout: float = 0.05,
    # lora_target_modules: str = MODULES_MAPPING["gptj"], # gpt-3
    model_family: str = "gptj",

    # llm hyperparams
    bf16: bool = True, # whether to use bf16 (preferred on A100's).
    # load_in_8bit: bool = True, # 8 bit sẽ giảm vram nhưng chậm tốc độ huấn luyện đi nhiều lần
    kbit: str = "8bit",
    group_by_length: bool = False,  # faster, but produces an odd training loss curve
    resume_from_checkpoint: str = None,  # either training checkpoint or final adapter
):
    
    ## Quantization configs
    bnb_config = BitsAndBytesConfig() ## default 
    if kbit == "4bit":
        print(
            f"Quantization 4 bit"
        )
        bnb_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_use_double_quant=True,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_compute_dtype=torch.bfloat16
        )
    elif kbit == "8bit":
        print(
            f"Quantization 8 bit"
        )
        bnb_config = BitsAndBytesConfig(
            load_in_8bit=True,
        )
    
    ## Parameter efficient finetuning configs
    lora_target_modules = MODULES_MAPPING[model_family]
    if finetune_method in ["lora", "qlora"]:
        config = LoraConfig(
            r=lora_r,
            lora_alpha=lora_alpha,
            target_modules=lora_target_modules, # phân tách str thành list
            lora_dropout=lora_dropout,
            bias="none",
            task_type=TaskType.CAUSAL_LM,
        )
        print(
            f"Training LoRA model with params:\n"
            f"lora_r: {lora_r}\n"
            f"lora_alpha: {lora_alpha}\n"
            f"lora_dropout: {lora_dropout}\n"
            f"lora_target_modules: {lora_target_modules}\n"
        )
    elif finetune_method == "prefix":
        config = PrefixTuningConfig(
            task_type=TaskType.CAUSAL_LM,
            num_virtual_tokens=num_virtual_tokens
        )
        print(
            f"Training Prefix-tuning model with params:\n"
            f"num_virtual_tokens: {num_virtual_tokens}\n"
        )
    else:
        assert False, "Hiện tại chỉ hỗ trợ lora và prefix tuning"

    assert (
        base_model
    ), "Please specify a --base_model, e.g. --base_model='VietAI/gpt-j-6B-vietnamese-news'"
    
    ## Load model and tokenizer
    device_map = {"": int(os.environ.get("CUDA_DEVICE") or 0)}
    model = AutoModelForCausalLM.from_pretrained(
        base_model, 
        quantization_config=bnb_config, 
        device_map=device_map,
    )
    model.gradient_checkpointing_enable()
    model = prepare_model_for_kbit_training(model)
    model = get_peft_model(model, config)
    if resume_from_checkpoint:
        # Check the available weights and load them
        checkpoint_name = os.path.join(
            resume_from_checkpoint, "pytorch_model.bin"
        )  # Full checkpoint
        if not os.path.exists(checkpoint_name):
            checkpoint_name = os.path.join(
                resume_from_checkpoint, "adapter_model.bin"
            )  # only LoRA model - LoRA config above has to fit
            resume_from_checkpoint = (
                False  # So the trainer won't try loading its state
            )
        # The two files above have a different name depending on how they were saved, but are actually the same.
        if os.path.exists(checkpoint_name):
            print(f"Restarting from {checkpoint_name}")
            adapters_weights = torch.load(checkpoint_name)
            set_peft_model_state_dict(model, adapters_weights)
        else:
            print(f"Checkpoint {checkpoint_name} not found")
    # Be more transparent about the % of trainable params.
    model.print_trainable_parameters()
    
    tokenizer = AutoTokenizer.from_pretrained(base_model)
    tokenizer.pad_token_id = 0 # unk. we want this to be different from the eos token
    tokenizer.padding_side = "left"  # Allow batched inference
            
            
    ## Load data       
    # Helper functions
    def tokenize(prompt, add_eos_token=True):
        result = tokenizer(
            prompt,
            truncation=True,
            max_length=cutoff_len,
            padding=False,
            return_tensors=None,
        )
        if (
            result["input_ids"][-1] != tokenizer.eos_token_id
            and len(result["input_ids"]) < cutoff_len
            and add_eos_token
        ):
            result["input_ids"].append(tokenizer.eos_token_id)
            result["attention_mask"].append(1)

        result["prompt"] = prompt
        result["labels"] = result["input_ids"].copy()
        return result

    def generate_and_tokenize_prompt(data_point):
        full_prompt = generate_prompt(data_point)
        return tokenize(full_prompt)
    # -----------------------------------------
    
    if data_path.endswith(".jsonl"):
        data = load_dataset("json", data_files=data_path)
    else:
        data = load_dataset(data_path)
    if val_set_size > 0:
        train_val = data["train"].train_test_split(test_size=val_set_size, shuffle=True, seed=42)
        train_data = train_val["train"].shuffle().map(generate_and_tokenize_prompt)
        val_data = train_val["test"].shuffle().map(generate_and_tokenize_prompt)
    else:
        train_data = data["train"].shuffle(seed=71).map(generate_and_tokenize_prompt)
        val_data = None
    
    ## Prepare trainer
    gradient_accumulation_steps = batch_size // micro_batch_size
    if kbit == "8bit": bf16 = False # nếu load 8 bit thì buộc phải dùng bf16
    world_size = int(os.environ.get("WORLD_SIZE", 1))
    ddp = world_size != 1

    if ddp: # huấn luyện đa GPUs
        device_map = {"": int(os.environ.get("LOCAL_RANK") or 0)}
        gradient_accumulation_steps = gradient_accumulation_steps // world_size
        
    training_args = transformers.TrainingArguments(
            fp16=(not bf16), # tốt cho GPUs đời cũ và training 8-bit
            bf16=bf16, # tốt cho GPUs đời mới và không dùng 8-bit
            per_device_train_batch_size=micro_batch_size,
            gradient_accumulation_steps=gradient_accumulation_steps,
            warmup_steps=100,
            num_train_epochs=num_epochs,
            learning_rate=learning_rate,
            logging_steps=5,
            optim="paged_adamw_8bit",
            evaluation_strategy="steps" if val_set_size > 0 else "no",
            save_strategy="steps",
            eval_steps=200 if val_set_size > 0 else None,
            save_steps=100,
            output_dir=output_dir,
            save_total_limit=3,
            load_best_model_at_end=True if val_set_size > 0 else False,
            ddp_find_unused_parameters=False if ddp else None,
            group_by_length=group_by_length,
            report_to="none", # không sử dụng wandb (default option)
            run_name=None,
    )
    data_collator = transformers.DataCollatorForSeq2Seq(
        tokenizer, 
        pad_to_multiple_of=8, 
        return_tensors="pt", 
        padding=True
    )
    trainer = transformers.Trainer(
        model=model,
        train_dataset=train_data,
        eval_dataset=val_data,
        args=training_args,
        data_collator=data_collator,
        callbacks=[SavePeftModelCallback]
    )
    
    model.config.use_cache = False

    # old_state_dict = model.state_dict
    # model.state_dict = (
    #     lambda self, *_, **__: get_peft_model_state_dict(self, old_state_dict())
    # ).__get__(model, type(model))

    if torch.__version__ >= "2" and sys.platform != "win32":
        model = torch.compile(model)
        
    ## Trainer goes brrrrr
    trainer.train(resume_from_checkpoint=resume_from_checkpoint)
    model = model.to("cuda")
    model.save_pretrained(output_dir)

if __name__ == "__main__":
    fire.Fire(train)
