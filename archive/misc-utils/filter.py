from datatrove.executor.base import PipelineExecutor
from datatrove.executor.local import LocalPipelineExecutor
from datatrove.pipeline.dedup import SentenceDedupFilter, SentenceDedupSignature, SentenceFindDedups
from datatrove.pipeline.dedup.sentence_dedup import SentDedupConfig
from datatrove.pipeline.extractors import Trafilatura
from datatrove.pipeline.filters import *
from datatrove.pipeline.readers import JsonlReader, WarcReader
from datatrove.pipeline.writers.jsonl import JsonlWriter
from datatrove.utils.typeshelper import Languages
import os

# Set the environment variables to specify the GPUs
INPUT_READER = JsonlReader(
    data_folder="/home/user/data_0",
    # recursive=True
)
TOTAL_TASKS = 96
NUM_WORKERS = 48
FILTERING_OUTPUT_PATH = "/home/user/remove"
stage = LocalPipelineExecutor(
    pipeline=[
        INPUT_READER,
        URLFilter(exclusion_writer=JsonlWriter(f"{FILTERING_OUTPUT_PATH}/removed/URLFilter")),
        LanguageFilter(exclusion_writer=JsonlWriter(f"{FILTERING_OUTPUT_PATH}/removed/LanguageFilter")),
        GopherQualityFilter(exclusion_writer=JsonlWriter(f"{FILTERING_OUTPUT_PATH}/removed/GopherQualityFilter")),
        GopherRepetitionFilter(exclusion_writer=JsonlWriter(f"{FILTERING_OUTPUT_PATH}/removed/GopherRepetitionFilter")),
        C4QualityFilter(exclusion_writer=JsonlWriter(f"{FILTERING_OUTPUT_PATH}/removed/C4QualityFilter")),
        C4BadWordsFilter(exclusion_writer=JsonlWriter(f"{FILTERING_OUTPUT_PATH}/removed/C4BadWordsFilter")),
        FineWebQualityFilter(exclusion_writer=JsonlWriter(f"{FILTERING_OUTPUT_PATH}/removed/FineWebQualityFilter")),
        JsonlWriter(output_folder="filter_final/output")
    ],
    tasks=TOTAL_TASKS,
    workers=NUM_WORKERS,
    logging_dir="filter_final_/log",
) 
if __name__ == '__main__':
    # freeze_support()
    stage.run()
