import json
from tqdm import tqdm
import re
import argparse
import os
from datasets import load_dataset
from multiprocessing import Process, current_process
from datetime import datetime

# Initialize LLM
from distilabel.llms import ClientvLLM

api_key = 'API_KEY'
llm = ClientvLLM(
    base_url="http://localhost:8000/v1",
    tokenizer="meta-llama/Meta-Llama-3.1-405B-Instruct-Turbo"
)
llm.load()

# Helper functions
def extract_tags(text, left="<>", right="</>"):
    """Extract content between specified tags."""
    pattern = rf"{re.escape(left)}(.*?){re.escape(right)}"
    match = re.search(pattern, text, re.DOTALL)
    return match.group(1).strip() if match else text

def concat_conversation(row):
    """Concatenate all conversation turns into a single formatted string."""
    return "\n".join(
        [f"<<{msg['role'].upper()}>>{msg['content'].replace('\n', '\\n')}" for msg in row['messages']]
    )

def parse_translated_conversation(translated_text):
    """Parse the translated conversation back into the original format."""
    matches = re.findall(r"<<(USER|ASSISTANT|SYSTEM)>>(.+?)(?=<<|$)", translated_text, re.DOTALL)
    return {"messages": [{"role": role.lower(), "content": content.replace("\\n", "\n").strip()} for role, content in matches]}

def translate_to_vietnamese(texts):
    """Translate text to Vietnamese using the LLM API."""
    generation_kwargs = {
        "temperature": 0.8,
        "top_p": 1.0,
        "max_new_tokens": 8192,
    }
    SYSTEM_PROMPT = "You are a helpful assistant."
    PROMPT = (
        "Translate the following text to Vietnamese, ensuring it sounds natural and fluent. "
        "Preserve the format and not translate the markers <<USER>>, <<ASSISTANT>>, and <<SYSTEM>>. "
        "Wrap the translation within <TRANSLATION> </TRANSLATION> tags.\n\nText:\n\n{text}"
    )
    outputs = llm.generate_outputs(
        inputs=[
            [{"role": "system", "content": SYSTEM_PROMPT}, 
             {"role": "user", "content": PROMPT.format(text=text)}] for text in texts
        ],
        **generation_kwargs
    )
    result = [extract_tags(x[0], left="<TRANSLATION>", right="</TRANSLATION>") for x in outputs]
    return result

def process_dataset(dataset, output_file, batch_size):
    """Process a dataset by translating conversations batch by batch."""
    process_name = current_process().name
    print(f"Process {process_name} started at {datetime.now()}")
    start_time = datetime.now()

    with open(output_file, "a", encoding="utf-8") as f:
        for i in tqdm(range(0, len(dataset), batch_size), desc=f"Translating data ({process_name})"):
            batch = dataset[i:i + batch_size]
            concatenated_texts = [concat_conversation(row) for row in batch]
            batch_results = []
            try:
                translated_texts = translate_to_vietnamese(concatenated_texts)
                for original, translated in zip(batch, translated_texts):
                    try:
                        translated_row = parse_translated_conversation(translated)
                        batch_results.append({"original": original, "translated": translated_row, "success": True})
                    except Exception as parse_error:
                        print(f"Error parsing translation: {parse_error}")
                        batch_results.append({"original": original, "translated": None, "success": False})
            except Exception as translation_error:
                print(f"Error processing batch {i // batch_size + 1}: {translation_error}")
                for original in batch:
                    batch_results.append({"original": original, "translated": None, "success": False})
            for result in batch_results:
                f.write(json.dumps(result, ensure_ascii=False) + "\n")

    end_time = datetime.now()
    print(f"Process {process_name} completed at {end_time}. Duration: {end_time - start_time}")

def partition_data(data, num_partitions, output_dir):
    """Split the dataset into partitions, offsetting already processed samples."""
    partition_size = len(data) // num_partitions
    partitions = []
    
    for i in range(num_partitions):
        partition_file = os.path.join(output_dir, f"partition_{i}.jsonl")
        if os.path.exists(partition_file):
            processed_samples = sum(1 for _ in open(partition_file, "r", encoding="utf-8"))
        else:
            processed_samples = 0
        
        start_idx = i * partition_size + processed_samples
        end_idx = (i + 1) * partition_size
        if i == num_partitions - 1:
            end_idx = len(data)
        
        partitions.append(data[start_idx:end_idx])
    
    return partitions

def process_partition(partition, output_dir, partition_idx, batch_size):
    """Wrapper for processing a single partition."""
    output_file = os.path.join(output_dir, f"partition_{partition_idx}.jsonl")
    process_dataset(partition, output_file, batch_size)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Translate dataset using LLM.")
    parser.add_argument("--data_file", type=str, default="wiki10k.jsonl", help="Input dataset file (JSONL).")
    parser.add_argument("--output_dir", type=str, default="output", help="Directory to store partition output files.")
    parser.add_argument("--reset", action="store_true", help="Clear the output directory if set.")
    parser.add_argument("--num_processes", type=int, default=64, help="Number of parallel processes.")
    args = parser.parse_args()

    if args.reset and os.path.exists(args.output_dir):
        for file in os.listdir(args.output_dir):
            os.remove(os.path.join(args.output_dir, file))

    os.makedirs(args.output_dir, exist_ok=True)

    data = load_dataset("json", data_files=[args.data_file], split="train")
    print(f"Total samples in dataset: {len(data)}")

    partitions = partition_data(data.to_list(), args.num_processes, args.output_dir)

    processes = []
    for i, partition in enumerate(partitions):
        p = Process(target=process_partition, args=(partition, args.output_dir, i, 4))
        processes.append(p)
        p.start()

    for p in processes:
        p.join()
