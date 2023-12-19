import os
from pathlib import Path
import json
from tqdm import tqdm

filenames = os.listdir("../book_processed")

with open("../final_data/vietnamese-books.jsonl", "w") as file:
    for filename in tqdm(filenames):
        SEP = "NGUYEN#QUANG#VAN#VINH"
        CUTOFF_LEN = 8000
        filepath = Path("../book_processed") / filename
        with open(filepath, "r") as f:
            text = f.read()
            docs = text.split(SEP)
            docs = [doc for doc in docs if len(doc.strip()) > 0]
            valid_docs = []
            for doc in docs:
                text = doc.strip()
                words = text.split(" ")
                new_docs = [doc]

                if len(text) == 0: continue
                if len(words) > CUTOFF_LEN:
                    new_docs = [" ".join(words[i:i+CUTOFF_LEN])
                            for i in range(0, len(words), CUTOFF_LEN)]
                valid_docs += new_docs

            json_docs = [{
                "text": doc,
                # "split": i,
                # "source": filename
            } for (i, doc) in enumerate(valid_docs)]
            for json_doc in json_docs:
                file.write(json.dumps(json_doc, ensure_ascii=False) + "\n")

