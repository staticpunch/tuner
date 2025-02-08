import google.generativeai as genai
import time
import os
from tqdm import tqdm
import json
import concurrent.futures
import argparse
from typing import Callable, Optional, Dict, Any

improve_template = """Câu hỏi cần sâu sắc hơn và nội dung trả lời cần được diễn giải chi tiết hơn nữa.
""".strip()


def generate_response(conversation, api_key, model_name, max_retries, retry_delay):
    """Generates a response for a multi-turn conversation, handling retries."""
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(model_name)
    chat = model.start_chat(history=conversation)
    generation_config = {
        "temperature": 0.8
    }
    retries = 0
    while retries < max_retries:
        try:
            # Send the *last* message in the conversation
            response = chat.send_message(
                conversation[-1]['parts'][0]['text'],
                generation_config=generation_config
            )
            return response.text
        except Exception as e:
            retries += 1
            wait_time = retry_delay * (2 ** (retries - 1))
            print(f"Request failed (attempt {retries}/{max_retries}): {e}.  Retrying in {wait_time:.2f} seconds...")
            time.sleep(wait_time)
            if "429" in str(e) and "Please use Vertex AI to" in str(e):
                raise RuntimeError("Rate limit exceeded and suggests using Vertex AI.")
            if retries == max_retries:
                print(f"Max retries reached for conversation.  Skipping.")
                return "ERROR: Max retries exceeded"
    return None  # Should never reach here


def process_batch(conversations_batch, api_key, model_name, max_retries, retry_delay, max_workers, conversation_processor: Callable):
    """Processes a batch of conversations using multiprocessing, including follow-up."""
    results = []
    with concurrent.futures.ProcessPoolExecutor(max_workers=max_workers) as executor:
        futures = [
            executor.submit(
                conversation_processor, conversation, api_key, model_name, max_retries, retry_delay
            )
            for conversation in conversations_batch
        ]
        for future in concurrent.futures.as_completed(futures):
            try:
                result = future.result()
                if result:
                    results.append(result)
            except Exception as e:
                print(f"An error occurred during processing: {e}")
    return results


def default_process_single_conversation(conversation_entry: Dict[str, Any], api_key: str, model_name: str, max_retries: int, retry_delay: int) -> Optional[Dict[str, Any]]:
    """
    Processes a single conversation, including a follow-up request, using the default logic.
    """
    conversation = conversation_entry.get("conversation")
    metadata = conversation_entry.get("metadata", {})

    if not conversation or not isinstance(conversation, list):
        print("Warning: Entry found without a valid 'conversation' field (list). Skipping.")
        return None

    # --- First Turn ---
    response_text = generate_response(conversation, api_key, model_name, max_retries, retry_delay)
    updated_conversation = conversation + [{"role": "model", "parts": [{"text": response_text}]}]

    # --- Second Turn (Follow-up) ---
    if response_text != "ERROR: Max retries exceeded":  # Only follow up if the first turn succeeded
        follow_up_prompt = improve_template
        updated_conversation = updated_conversation + [{"role": "user", "parts": [{"text": follow_up_prompt}]}]
        follow_up_response = generate_response(updated_conversation, api_key, model_name, max_retries, retry_delay)
        updated_conversation = updated_conversation + [{"role": "model", "parts": [{"text": follow_up_response}]}]

    result_entry = {
        "conversation": updated_conversation,
        "metadata": metadata
    }
    return result_entry


def call_gemini_multiprocess(
    conversations,
    api_key,
    model_name="models/gemini-pro",
    save_every=100,
    output_dir="gemini_responses",
    max_retries=1,
    retry_delay=5,
    max_workers=20,
    reuse=True,
    conversation_processor: Optional[Callable] = None
):
    """
    Processes conversations with the Gemini API in parallel.

    Args:
        conversations: A list of conversation dictionaries.
        api_key: Your Google Gemini API key.
        model_name: The name of the Gemini model to use.
        save_every: Save the responses every N conversations.
        output_dir: The directory to save the responses to.
        max_retries: The maximum number of retries for each API call.
        retry_delay: The initial delay between retries in seconds.
        max_workers: The maximum number of worker processes to use.
        reuse: Whether to reuse existing output files.
        conversation_processor:  A function that takes a single conversation entry, api_key,
                                 model_name, max_retries, and retry_delay and returns
                                 a modified conversation entry or None.  If None, the
                                 `default_process_single_conversation` will be used.
    """

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    all_responses = []
    batch_start_time = time.time()
    total_requests = 0
    num_conversations = len(conversations)

    if conversation_processor is None:
        conversation_processor = default_process_single_conversation


    with tqdm(total=num_conversations, desc="Processing Conversations") as pbar:
        for i in range(0, num_conversations, save_every):
            batch = conversations[i : min(i + save_every, num_conversations)]

            # --- Reuse Logic ---
            if reuse:
                filename = os.path.join(output_dir, f"responses_{i + save_every:07d}.jsonl")
                if os.path.exists(filename):
                    print(f"File {filename} already exists. Skipping batch.")
                    pbar.update(len(batch))  # Update progress bar to reflect skipped batch
                    continue  # Skip to the next iteration of the loop

            # Rate limiting
            elapsed_time = time.time() - batch_start_time
            if (
                total_requests > 0
                and elapsed_time < 60.0
                and (total_requests % 1000) >= 990
            ):
                sleep_time = 60.0 - elapsed_time + 2
                print(f"Approaching rate limit. Sleeping for {sleep_time:.2f} seconds...")
                time.sleep(sleep_time)
                batch_start_time = time.time()

            batch_responses = process_batch(
                batch, api_key, model_name, max_retries, retry_delay, max_workers, conversation_processor
            )
            all_responses.extend(batch_responses)
            total_requests += sum(1 for response in batch_responses if response)

            # Save responses
            save_responses(all_responses, output_dir, i + save_every)
            pbar.update(len(batch))
            all_responses = []


def save_responses(responses, output_dir, file_num):
    """Saves responses to a JSONL file."""
    filename = os.path.join(output_dir, f"responses_{file_num:07d}.jsonl")
    with open(filename, "w", encoding="utf-8") as f:
        for response in responses:
            if response:
                f.write(json.dumps(response, ensure_ascii=False) + "\n")


def load_conversations_from_jsonl(filepath):
    """Loads conversations from a .jsonl file."""
    conversations = []
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    data = json.loads(line)
                    if "conversation" in data and isinstance(data["conversation"], list):
                        conversations.append(data)
                    else:
                        print(f"Warning: Skipping invalid entry in {filepath}")
                except json.JSONDecodeError:
                    print(f"Warning: Skipping invalid JSON line in {filepath}")
    except FileNotFoundError:
        print(f"Error: File not found: {filepath}")
    except Exception as e:
        print(f"Error loading conversations from {filepath}: {e}")
    return conversations


def load_conversations_from_directory(input_dir):
    """Loads initial prompts from all .jsonl files in a directory, starting new conversations."""
    all_conversations = []
    for filename in os.listdir(input_dir):
        if filename.endswith(".jsonl"):
            filepath = os.path.join(input_dir, filename)
            all_conversations.extend(load_initial_prompts_from_jsonl(filepath))
    return all_conversations


def load_initial_prompts_from_jsonl(filepath):
    """Loads initial prompts from a .jsonl and formats them as starting conversations."""
    initial_conversations = []
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    data = json.loads(line)
                    # Check if the "prompt" key exists
                    if "prompt" in data:
                        # Create a new conversation with the initial prompt
                        initial_conversation = {
                            "conversation": [
                                {"role": "user", "parts": [{"text": data["prompt"]}]}
                            ],
                            "metadata": data.get("metadata", {})  # Include any existing metadata
                        }
                        initial_conversations.append(initial_conversation)
                    else:
                        print(f"Warning: Skipping invalid entry (no 'prompt' key) in {filepath}")

                except json.JSONDecodeError:
                    print(f"Warning: Skipping invalid JSON line in {filepath}")
    except FileNotFoundError:
        print(f"Error: File not found: {filepath}")
    except Exception as e:
        print(f"Error loading prompts from {filepath}: {e}")
    return initial_conversations


def main():
    parser = argparse.ArgumentParser(description="Process conversations with Gemini API, including follow-up.")
    parser.add_argument(
        "--input_dir",
        type=str,
        required=True,
        help="Path to the input directory containing .jsonl files with *initial prompts*.",
    )
    parser.add_argument(
        "--output_dir",
        type=str,
        required=True,
        help="Path to the output directory for saving conversations.",
    )
    parser.add_argument(
        "--api_key", type=str, required=True, help="Your Google Gemini API key."
    )
    parser.add_argument(
        "--model_name",
        type=str,
        default="models/gemini-pro",
        help="Name of the Gemini model.",
    )
    parser.add_argument(
        "--save_every",
        type=int,
        default=100,
        help="Save responses every N conversations.",
    )
    parser.add_argument(
        "--max_retries",
        type=int,
        default=3,  # Increased default retries
        help="Maximum number of retries.",
    )
    parser.add_argument(
        "--retry_delay",
        type=int,
        default=5,
        help="Initial retry delay in seconds.",
    )
    parser.add_argument(
        "--max_workers",
        type=int,
        default=20,
        help="Maximum number of worker processes.",
    )

    args = parser.parse_args()

    conversations = load_conversations_from_directory(args.input_dir)
    if not conversations:
        print("No conversations found. Exiting.")
        return

    # Example of a custom conversation processor
    def my_custom_processor(conversation_entry, api_key, model_name, max_retries, retry_delay):
        # Your custom logic here
        conversation = conversation_entry.get("conversation")
        metadata = conversation_entry.get("metadata", {})

        if not conversation or not isinstance(conversation, list):
            print("Warning: Entry found without a valid 'conversation' field (list). Skipping.")
            return None

        # --- First Turn ---
        response_text = generate_response(conversation, api_key, model_name, max_retries, retry_delay)
        updated_conversation = conversation + [{"role": "model", "parts": [{"text": response_text}]}]

        result_entry = {
            "conversation": updated_conversation,
            "metadata": metadata
        }
        return result_entry

    call_gemini_multiprocess(
        conversations,
        args.api_key,
        model_name=args.model_name,
        save_every=args.save_every,
        output_dir=args.output_dir,
        max_retries=args.max_retries,
        retry_delay=args.retry_delay,
        max_workers=args.max_workers,
        conversation_processor=my_custom_processor  # Pass your custom function here
    )
    print("Processing complete.")


if __name__ == "__main__":
    main()
