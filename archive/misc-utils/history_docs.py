import os
import json

infile = "../lichsu_clean/vietnamese-history.txt"
CUTOFF_LEN = 2048
with open(infile, "r") as f:
    text = f.read()
    words = text.split()
    docs = [" ".join(words[i:i+CUTOFF_LEN]) 
            for i in range(0, len(words), CUTOFF_LEN)]
    json_docs = [{
        "text": doc,
        # "split": i,
        # "source": "vietnamese-history"
    } for (i, doc) in enumerate(docs)]

outfile = "../final_data/vietnamese-history.jsonl"
with open(outfile, "w") as file:
    for json_doc in json_docs:
        file.write(json.dumps(json_doc, ensure_ascii=False) + "\n")
