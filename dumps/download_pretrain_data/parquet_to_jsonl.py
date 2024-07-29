from datasets import load_dataset
from tqdm import tqdm
import multiprocessing
import glob

def to_jsonl(filepath):
    data = load_dataset("parquet", data_files=filepath, split="train")
    # data = data.select_columns(["text"])
    jsonl_path = filepath.split(".")[0] + ".jsonl"
    print("saving to", jsonl_path)
    data.to_json(jsonl_path, force_ascii=False)
    print("finished saving to", jsonl_path)

culturax_dir = "data/CulturaX/"
culturax_files = [fn for fn in glob.glob(culturax_dir + "*") if fn.endswith(".parquet")]
culturax_files.sort()
batch_size = 24
files_batch = [culturax_files[i:i+batch_size] for i in range(0, len(culturax_files), batch_size)]

with multiprocessing.Pool(processes=batch_size) as pool:
    for batch in tqdm(files_batch):
        items = [(x,) for x in batch]
        pool.starmap(to_jsonl, items)
