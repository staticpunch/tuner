import glob
import json
from tqdm.notebook import tqdm
import gzip
madlad_dir = "input_dir/*"
out_dir = "output_dir/"
xfiles = glob.glob(madlad_dir)
xfiles = sorted(xfiles)
xfiles = [x for x in xfiles if ".gz" in x]


buffer = []
counter = 0
THRESHOLD = 200_000
for filepath in tqdm(xfiles[:]):
    with gzip.open(filepath, "r") as file:
        for line in file:
            
            ## add metadata for mapping
            line = json.loads(line)
            line.update({"metadata": {"source_file": filepath}})

            ## write to file if the buffer reaching 200k lines.
            if len(buffer) == THRESHOLD:
                ## write file
                idx = str(counter).zfill(4)
                outfile = out_dir + f"madlad_part_{idx}.jsonl"
                with open(outfile, "w") as out:
                    for line in buffer:
                        out.write(json.dumps(line, ensure_ascii=False) + "\n")
                
                ## next iterator.
                buffer = []
                counter += 1

            ## append to buffer.
            buffer.append(line)

## write the remaining in the buffer to file
idx = str(counter).zfill(4)
outfile = out_dir + f"madlad_part_{idx}.jsonl"
with open(outfile, "w") as out:
    for line in buffer:
        out.write(json.dumps(line, ensure_ascii=False) + "\n")
