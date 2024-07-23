from datatrove.executor import LocalPipelineExecutor
from datatrove.pipeline.dedup import MinhashDedupSignature
from datatrove.pipeline.dedup.minhash import (
    MinhashConfig,
    MinhashDedupBuckets,
    MinhashDedupCluster,
    MinhashDedupFilter,
)
from datatrove.pipeline.readers import JsonlReader
from datatrove.pipeline.tokens import TokensCounter
from datatrove.pipeline.writers.jsonl import JsonlWriter

# you can also change ngrams or the number of buckets and their size here
minhash_config = MinhashConfig()  # better precision -> fewer false positives (collisions)
MINHASH_BASE_PATH = "minhash/output"
LOGS_FOLDER = "minhash/log"

TOTAL_TASKS = 128
NUM_WORKERS = 64

# this is the original data that we want to deduplicate
INPUT_READER = JsonlReader(
    data_folder="./data",
    recursive=True
)

# stage 1 computes minhash signatures for each task (each task gets a set of files)
stage1 = LocalPipelineExecutor(
    pipeline=[
        INPUT_READER,
        MinhashDedupSignature(
            output_folder=f"{MINHASH_BASE_PATH}/signatures", 
            config=minhash_config
        ),
    ],
    tasks=TOTAL_TASKS,
    workers=NUM_WORKERS,
    logging_dir=f"{LOGS_FOLDER}/signatures",
) 

# stage 2 finds matches between signatures in each bucket
stage2 = LocalPipelineExecutor(
    pipeline=[
        MinhashDedupBuckets(
            input_folder=f"{MINHASH_BASE_PATH}/signatures",
            output_folder=f"{MINHASH_BASE_PATH}/buckets",
            config=minhash_config,
        ),
    ],
    tasks=minhash_config.num_buckets * 64,
    workers=NUM_WORKERS,
    logging_dir=f"{LOGS_FOLDER}/buckets",
    depends=stage1,
)

# stage 3 creates clusters of duplicates using the results from all buckets
stage3 = LocalPipelineExecutor(
    pipeline=[
        MinhashDedupCluster(
            input_folder=f"{MINHASH_BASE_PATH}/buckets",
            output_folder=f"{MINHASH_BASE_PATH}/remove_ids",
            config=minhash_config,
        ),
    ],
    tasks=1,
    workers=NUM_WORKERS,
    logging_dir=f"{LOGS_FOLDER}/clusters",
    depends=stage2,
)

stage4 = LocalPipelineExecutor(
    # job_name="mh4",
    pipeline=[
        INPUT_READER,
#         TokensCounter("Llama-3-8B/tokenizer.json"),  # nice way to see how many tokens we had before and after deduplication
        MinhashDedupFilter(
            input_folder=f"{MINHASH_BASE_PATH}/remove_ids",
            exclusion_writer=JsonlWriter(f"{MINHASH_BASE_PATH}/removed"),
        ),
        JsonlWriter(output_folder=f"{MINHASH_BASE_PATH}/deduplicated_output"),
    ],
    tasks=TOTAL_TASKS,
    workers=NUM_WORKERS,
    logging_dir=f"{LOGS_FOLDER}/filter",
    depends=stage3,
)

stage4.run()
