import json
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

def extract_tags(text, left="<>", right="</>"):
    escaped_left = re.escape(left)
    escaped_right = re.escape(right)
    pattern = rf"{escaped_left}(.*?){escaped_right}"
    match = re.search(pattern, text, re.DOTALL)
    
    return match.group(1).strip() if match else text

def limit_text(example):
    text = example["text"]
    lines = [line for line in text.split("\n")]
    first_few_lines = []
    cur_len = 0
    limit = 2500
    for line in lines:
        if cur_len + len(line.split()) > limit:
            break
        first_few_lines.append(line)
        cur_len += len(line.split())
    first_text = "\n".join(first_few_lines)
    first_word_count = len(first_text.split())
    return dict(
        first_text=first_text,
        first_word_count=first_word_count
    )

class ExtractQuestions(Step):
    @property
    def inputs(self) -> "StepColumns":
        return ['generation']

    @property
    def outputs(self) -> "StepColumns":
        return ["candidate_questions", "methods_list"]

    def process(self, inputs: StepInput) -> "StepOutput":
        for input in inputs:
            questions_in_tags = extract_tags(
                input["generation"],
                left="<Questions>", 
                right="</Questions>"
            )
            pattern = r"\d+\.\s*(.+?)(?=\n\d+\.|$)"
            questions = re.findall(pattern, questions_in_tags, re.DOTALL)
            
            input["candidate_questions"] = questions
            input["methods_list"] = extract_tags(
                input["generation"],
                left="<Methods>", 
                right="</Methods>"
            )
            
        yield inputs

class PostProcessor(Step):
    @property
    def inputs(self) -> "StepColumns":
        return ['generation']

    @property
    def outputs(self) -> "StepColumns":
        return ["verification", "refinement_plans", "final_questions"]

    def process(self, inputs: StepInput) -> "StepOutput":
        for input in inputs:
            plans_in_tags = extract_tags(
                input["generation"],
                left="<Refinement>", 
                right="</Refinement>"
            )
            verification_in_tags = extract_tags(
                input["generation"],
                left="<Verification>", 
                right="</Verification>"
            )
            questions_in_tags = extract_tags(
                input["generation"],
                left="<Output>", 
                right="</Output>"
            )
            
            pattern = r"\d+\.\s*(.+?)(?=\n\d+\.|$)"
            questions = re.findall(pattern, questions_in_tags, re.DOTALL)
            
            input["verification"] = verification_in_tags
            input["refinement_plans"] = plans_in_tags
            input["final_questions"] = questions
            
        yield inputs

class Writer(Step):
    out_file: str
    columns: List[str]

    @property
    def inputs(self) -> "StepColumns":
        return self.columns

    @property
    def outputs(self) -> "StepColumns":
        return self.columns

    def process(self, inputs: StepInput) -> "StepOutput":
        assert self.out_file.endswith(".jsonl")
        with open(self.out_file, "a", encoding="utf-8") as file:
            for input in inputs:
                json_mini = {k:input[k] for k in self.columns}
                file.write(json.dumps(json_mini, ensure_ascii=False) + "\n")
        yield inputs

def run_pipeline(
    api_key: str,
    data_file: str,
    out_file: str,
    reset: bool = False
):
    wiki = load_dataset(
        "json",
        data_files=[data_file],
        split="train"
    )
    if reset and os.path.exists(out_file):
        print(f"reset the pipeline, removing {out_file}")
        os.remove(out_file)
    linecount = sum(1 for _ in open(out_file, "r")) if os.path.exists(out_file) else 0

    data = wiki.select(range(linecount, len(wiki), 1))
    data = data.to_list()
    print(f"total: {len(wiki)}, processed: {linecount}, remain: {len(data)}")

    #########################
    ## DEFINE PIPELINE
    #########################
    with Pipeline("question-pipeline", description="Question Generation") as pipeline:
        loader = make_generator_step(
            data, 
            batch_size=2,
            output_mappings=None
        )
        
        llm = TogetherLLM(
            model="meta-llama/Meta-Llama-3.1-405B-Instruct-Turbo",
            # model="Qwen/Qwen2.5-72B-Instruct-Turbo",
            api_key=api_key,
        )
        
        question_generator = TextGeneration(
            name="question-generation",
            llm=llm,
            system_prompt="You are a helpful asssitant",
            template=GEN_PROMPT,
            columns=["text"],
            input_batch_size=2,
        )
        extract_questions = ExtractQuestions(
            name="extract-questions",
            # output_mappings={"candidate_questions": "questions"},
        )
        
        question_verifier = TextGeneration(
            name="question-verifier",
            llm=llm,
            system_prompt="You are a helpful asssitant",
            template=VERIFY_PROMPT,
            columns=["text", "candidate_questions"],
            # input_mappings={"candidate_questions": "questions"},
            input_batch_size=2,
        )
    
        post_processor = PostProcessor(
            name="post-processor",
            # output_mappings={"questions":"candidate_questions"}
        )

        writer = Writer(
            name="writer", 
            out_file=out_file,
            columns=[
                'id', 'url', 'title', 'text', 
                'methods_list', 'candidate_questions', 
                'verification', 'refinement_plans',
                'final_questions'
            ]
        )
        
        (
            loader >> question_generator 
            >> extract_questions >> question_verifier 
            >> post_processor >> writer
        )
        
        pipeline.draw(path="phase_1.png")
        
    #########################
    ## RUN PIPELINE
    #########################

    llm_params = {
        "generation_kwargs": {
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
    }
    
    result = pipeline.run(
        parameters = {
            question_generator.name: {
                "llm": llm_params
            },
            question_verifier.name: {
                "llm": llm_params
            }
        },
        use_cache=False,
        # batch_size=1
    )

    return result
    
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
    args = parser.parse_args()
    api_key='API_KEY'
    
    outfile = args.out_file
    result = run_pipeline(
        api_key=api_key,
        data_file=args.data_file,
        out_file=args.out_file,
        reset=args.reset
    )


