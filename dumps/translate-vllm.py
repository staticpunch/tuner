import json
from tqdm import tqdm
import re
import argparse
import os

from typing import List, Any, Union
from typing import TYPE_CHECKING
from distilabel.steps import (
    LoadDataFromHub, 
    KeepColumns,
    Step, StepInput,
    LoadDataFromFileSystem,
    make_generator_step
)

from distilabel.pipeline import Pipeline
from distilabel.llms import TogetherLLM
from distilabel.steps.tasks import TextGeneration

from datasets import Dataset, load_dataset
from prompts import GEN_PROMPT, VERIFY_PROMPT

if TYPE_CHECKING:
    from distilabel.steps.typing import StepColumns, StepOutput

api_key ='API_KEY'
llm = TogetherLLM(
	model="meta-llama/Meta-Llama-3.1-405B-Instruct-Turbo",
	# model="Qwen/Qwen2.5-72B-Instruct-Turbo",
	api_key=api_key,
)
llm.load()

def extract_tags(text, left="<>", right="</>"):
    escaped_left = re.escape(left)
    escaped_right = re.escape(right)
    pattern = rf"{escaped_left}(.*?){escaped_right}"
    match = re.search(pattern, text, re.DOTALL)
    
    return match.group(1).strip() if match else text

# Concatenate all conversation turns in the specified format
def concat_conversation(row):
    conversation = []
    for message in row['messages']:
        role = message['role'].upper()
        content = message['content'].replace("\n", "\\n")  # Escape newlines in content
        conversation.append(f"<<{role}>>{content}")  # Use unique markers
    return "\n".join(conversation)

# Parse the translated conversation back to the original format
def parse_translated_conversation(translated_text):
    # Use a regex to match roles and content
    matches = re.findall(r"<<(USER|ASSISTANT|SYSTEM)>>(.+?)(?=<<|$)", translated_text, re.DOTALL)
    parsed_messages = []
    for role, content in matches:
        parsed_messages.append({
            "role": role.lower(),
            "content": content.replace("\\n", "\n").strip()  # Restore newlines and trim spaces
        })
    return {"messages": parsed_messages}


# Translate text using LLM API
def translate_to_vietnamese(texts):
    generation_kwargs = {
        "temperature": 0.8,
        "top_p": 1.0,
        "max_new_tokens": 8192,
        "stop": [
            "<|eot_id|>",
            "<|end_of_text|>",
            "<|start_header_id|>",
            "<|end_header_id|>",
        ],
    }
    SYSTEM_PROMPT = "You are a helpful assistant."
    PROMPT = (
        "Translate the following text to Vietnamese, ensuring it sounds natural and fluent. "
        "Preserve the format and not translate the markers <<USER>>, <<ASSISTANT>>, and <<SYSTEM>>. "
        "You must wrap the translation within the <TRANSLATION> </TRANSLATION> tags. "
        "Text:\n\n"
        "{text}"
    )
    
    output = llm.generate_outputs(
        inputs=[
            [{"role": "system", "content": SYSTEM_PROMPT}, 
			 {"role": "user", "content": PROMPT.format(text=text)}]
        for text in texts],
        **generation_kwargs
    )
    translations = [extract_tags(x[0], left="<TRANSLATION>", right="</TRANSLATION>") for x in output]
    return translations

def process_dataset(dataset, output_file, batch_size):
    """
    Processes a dataset, translating it batch by batch and appending results to an output file incrementally.

    Args:
        dataset (list of dict): The dataset to process.
        output_file (str): The path to the JSONL output file.
        batch_size (int): The size of each batch for translation.
    """
    # Ensure dataset is a list of dictionaries
    if not isinstance(dataset, list):
        raise ValueError("Dataset must be a list of dictionaries.")
    
    # Open the output file in append mode
    with open(output_file, "a", encoding="utf-8") as f:
        # Iterate over the dataset in batches
        for i in tqdm(range(0, len(dataset), batch_size), desc="trasnlating data"):
            batch = dataset[i:i + batch_size]
            batch_results = []  # Store results with success status
            
            # Concatenate conversations for each row in the batch
            concatenated_texts = [concat_conversation(row) for row in batch]
            
            try:
                # Translate the batch
                translated_texts = translate_to_vietnamese(concatenated_texts)
                # return translated_texts
                # Parse back to original format and mark success
                for original, translated in zip(batch, translated_texts):
                    try:
                        translated_row = parse_translated_conversation(translated)
                        batch_results.append({
                            "original": original,
                            "translated": translated_row,
                            "success": True
                        })
                    except Exception as parse_error:
                        print(f"Error parsing translation: {parse_error}")
                        batch_results.append({
                            "original": original,
                            "translated": None,
                            "success": False
                        })
            
            except Exception as translation_error:
                print(f"Error processing batch {i // batch_size + 1}: {translation_error}")
                # Mark entire batch as failed
                for original in batch:
                    batch_results.append({
                        "original": original,
                        "translated": None,
                        "success": False
                    })
            
            # Write results (success and failure) to the file
            for result in batch_results:
                f.write(json.dumps(result, ensure_ascii=False) + "\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Download files from a Hugging Face repository."
    )
    parser.add_argument("--data_file", type=str, 
        help="The name of the repository in the format 'username/repo'",
        default="wiki10k.jsonl"
    )
    parser.add_argument("--out_file", type=str, 
        help="The name of the repository in the format 'username/repo'",
        default="wiki_questions.jsonl"
    )
    parser.add_argument(
        "--reset", 
        action="store_true",
        help="Overwrite the the output file if true, otherwise append it."
    )
    data = load_dataset(
        "json",
        data_files=[args.data_file],
        split="train"
    )
    linecount = sum(1 for _ in open(out_file, "r")) if os.path.exists(out_file) else 0

    data = data.select(range(linecount, len(wiki), 1))
    data = data.to_list()
    print(f"total: {len(wiki)}, processed: {linecount}, remain: {len(data)}")
  
    process_dataset(
      dataset=data,
      output_file=args.output_file,
      batch_size=4
    )
