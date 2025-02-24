import torch
import yaml
import argparse

from mergekit.config import MergeConfiguration
from mergekit.merge import MergeOptions, run_merge
import sys
import os
import importlib
import json

LORA_MERGE_CACHE = "/tmp"  # change if you want to keep these for some reason
COPY_TOKENIZER = True  # you want a tokenizer? yeah, that's what i thought
LAZY_UNPICKLE = False  # experimental low-memory model loader
LOW_CPU_MEMORY = False  # enable if you somehow have more VRAM than RAM+swap


def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(description="Merge language models using mergekit")
    parser.add_argument(
        "-c",
        "--config",
        type=str,
        required=True,
        help="Path to the merge configuration Python file",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Print merge configuration details without running the merge",
    )

    # Parse arguments
    args = parser.parse_args()
    CONFIG_PATH = args.config

    # Extract directory and module name
    directory = os.path.dirname(os.path.abspath(CONFIG_PATH))
    module_name = os.path.splitext(os.path.basename(CONFIG_PATH))[0]

    # Temporarily add directory to Python path
    sys.path.insert(0, directory)
    module = importlib.import_module(module_name)
    sys.path.pop(0)  # Optional: Remove the directory from the path afterward

    # Load configuration
    config = yaml.safe_load(module.CONFIG)
    OUTPUT_PATH = config.pop("output_dir")
    merge_config = MergeConfiguration.model_validate(config)

    # Debug mode
    if args.debug:
        print("Debug Mode:")
        print("\n--- Merge Configuration ---")
        print(json.dumps(merge_config.model_dump(), indent=2))
        print(f"\n--- Output Path: {OUTPUT_PATH}")
        return

    # Run merge
    run_merge(
        merge_config,
        out_path=OUTPUT_PATH,
        options=MergeOptions(
            lora_merge_cache=LORA_MERGE_CACHE,
            cuda=torch.cuda.is_available(),
            copy_tokenizer=COPY_TOKENIZER,
            lazy_unpickle=LAZY_UNPICKLE,
            low_cpu_memory=LOW_CPU_MEMORY,
        ),
    )
    print(f"Done! The merged model is successfully saved to {OUTPUT_PATH}.")


if __name__ == "__main__":
    main()
