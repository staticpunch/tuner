from nltk.tokenize import sent_tokenize
import sys
import re 

def group_chunks(text, max_length=4999):
    sentences = sent_tokenize(text)
    
    chunks = [sentences[0]]
    for string in sentences[1:]:
        current_length = len(chunks[-1])
        if current_length + len(string) > max_length: 
            chunks.append(string[:max_length])
        else:
            chunks[-1] += " " + string

    return chunks
