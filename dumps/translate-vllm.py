import json
from tqdm import tqdm
import re
import argparse
import os
from datasets import load_dataset

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
        "stop": ["<|eot_id|>", "<|end_of_text|>", "<|start_header_id|>", "<|end_header_id|>"]
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
    return [extract_tags(x[0], left="<TRANSLATION>", right="</TRANSLATION>") for x in outputs]

def process_dataset(dataset, output_file, batch_size):
    """Process a dataset by translating conversations batch by batch."""
    with open(output_file, "a", encoding="utf-8") as f:
        for i in tqdm(range(0, len(dataset), batch_size), desc="Translating data"):
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

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Translate dataset using LLM.")
    parser.add_argument("--data_file", type=str, default="wiki10k.jsonl", help="Input dataset file (JSONL).")
    parser.add_argument("--out_file", type=str, default="wiki_questions.jsonl", help="Output file (JSONL).")
    parser.add_argument("--reset", action="store_true", help="Overwrite the output file if set.")
    args = parser.parse_args()

    if args.reset and os.path.exists(args.out_file):
        os.remove(args.out_file)

    data = load_dataset("json", data_files=[args.data_file], split="train")
    processed_count = sum(1 for _ in open(args.out_file, "r")) if os.path.exists(args.out_file) else 0
    data = data.select(range(processed_count, len(data))).to_list()

    print(f"Total: {len(data) + processed_count}, Processed: {processed_count}, Remaining: {len(data)}")
    process_dataset(dataset=data, output_file=args.out_file, batch_size=4)
