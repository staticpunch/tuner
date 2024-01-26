from huggingface_hub import HfApi, login
from huggingface_hub import create_repo
import sys

token = "token"
login(token)
repo_id = "nguyenthando/jjdo"
ckpt_id = sys.argv[1]

create_repo(
    repo_id=repo_id,
    private=True,
    repo_type="model",
    exist_ok=True
)

api = HfApi()
api.upload_folder(
    folder_path=ckpt_id,
    path_in_repo=f"output/{ckpt_id}",
    repo_id=repo_id,
    repo_type="model",
    ignore_patterns=["*.pth", "global*"]
)
