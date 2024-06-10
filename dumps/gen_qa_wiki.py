import re
import json
viet_keywords = [
    "việt nam", "hà nội", "hồ chí minh", "đông dương", "cà phê",
]
pattern = r'\b(?:{})\b'.format("|".join(viet_keywords))
def is_local_content(example):
    text = example["text"]
    match = re.search(pattern, text, re.IGNORECASE)
    return bool(match)

def get_first_text(example):
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

def extract_code(text):
    pattern = r"```(.*?)```"
    matches = re.findall(pattern, text, re.DOTALL)
    return matches[0].strip()

def extract_questions(text):
    pattern = r'"(.*?)"'
    matches = re.findall(pattern, text, re.DOTALL)
    questions = [x for x in matches if "?" in x]
    return questions

ASK_PROMPT = """Bạn sẽ được cung cấp một đoạn trích từ Wikipedia tiếng Việt như sau:
{text}

NHIỆM VỤ: Đặt 4 câu hỏi với mục đích khai thác thông tin liên quan đến nội dung của văn bản trên.

Yêu cầu nội dung:
- Câu hỏi chỉ dựa trên những gì có trong nội dung của văn bản được cung cấp. Không đặt những câu hỏi về những thông tin nằm ngoài văn bản
- Mỗi câu hỏi phải có độ khó thử thách (yêu cầu nhiều bước phân tích hoặc diễn giải hoặc tổng hợp thông tin từ nhiều thành phần của của văn bản).
- Bạn nên hỏi những câu hỏi dài và phức tạp.

Yêu cầu hình thức: 
- Bạn phải trả về một danh sách python các câu hỏi. Format như sau:
```
[
    {{"question": (question-1)}},
    ...,
    {{"question": (question-4)}}
]
```
- Phản hồi của bạn chỉ chứa danh sách câu hỏi với format được hướng dẫn bên trên. Không tự ý thêm câu trả lời hay lời giải thích nào.
- Enclose the list within ``` and ``` for later easy parsing.
- Các câu hỏi phải bằng tiếng Việt.
- Không thêm những cụm như là "Theo văn bản", "Căn cứ vào nội dung", hoặc các cụm từ tương tự vào câu hỏi của bạn.
""".strip()

ANSWER_PROMPT = """Bạn sẽ được cung cấp một đoạn trích từ Wikipedia tiếng Việt như sau:
{text}

### NHIỆM VỤ: Dựa vào nội dung của văn bản trên, trả lời câu hỏi sau:
Câu hỏi: {question}

### YÊU CẦU:
- Không được sử dụng bất cứ kiến thức hay thông tin nào nằm ngoài văn bản được cung cấp.
- Hãy trả lời mà không nhắc lại câu "Dựa trên văn bản", "Theo văn bản", "Căn cứ vào nội dung", hoặc các cụm từ tương tự.
- Luôn cố gắng đưa ra giải thích chi tiết, cụ thể cho câu trả lời của bạn để khiến chúng hữu ích và thuyết phục. 
- Nếu nhắc tới một khái niệm nào đó trong văn bản, bạn cần phải trích lại rõ ràng để người dùng hiểu được.
- Có thể cung cấp các thông tin liên quan để câu trả lời của bạn hữu ích với người dùng hơn.
""".strip()

local_wiki = wiki.filter(is_local_content)
local_wiki = local_wiki.map(lambda x: {"word_count": len(x["text"].split())})
local_wiki = local_wiki.filter(lambda x: x["word_count"] > 500)
local_wiki = local_wiki.map(get_first_text)
wiki10k = local_wiki.sort(column_names=["id"]).select(range(10000))

from tqdm.asyncio import tqdm
from tqdm.notebook import tqdm as tqdm_notebook
from copy import deepcopy

wiki10k_list = wiki10k.to_list()

results = []
with open("wiki-facts-40k.jsonl", "a") as f:
    for i, _example in enumerate(tqdm_notebook(wiki10k)):
        try:
            example = deepcopy(_example)
            ask_prompt = ASK_PROMPT.format(text=example["first_text"])
            response = await batch_inference([ask_prompt])
            result_text = response[0][1]["generated_text"]
            questions = extract_questions(result_text)
        except:
            print(f"Failed at genaratin questions for example {i}")
            # print(response)
            continue

        try:
            answer_prompts = [ANSWER_PROMPT.format(
                text=example["first_text"],
                question=question
            ) for question in questions]
            response = await batch_inference(answer_prompts)
            answers = [x[1]["generated_text"] for x in response]
            pairs = [(q, a) for q, a in zip(questions, answers)]
            example.update({"generated_pairs": pairs})

            to_write = {k: v for k, v in example.items() if k in ["id", "title", "generated_pairs"]}
            results.append(to_write)
            f.write(json.dumps(to_write, ensure_ascii=False) + "\n")
            print("success")
        except:
            print(f"Failed at generating answers for example {i}")
            # print(response)
            continue
