import argparse
from huggingface_hub import HfApi, create_repo
token = "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" ## DO
# token = "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" ## DAO

def main(repo_id, local_dir):
    create_repo(
        repo_id=repo_id,
        private=True,
        # repo_type="model",
        repo_type="dataset",
        exist_ok=True,
        token=token
    )

    api = HfApi()
    path_in_repo = local_dir.split("/")[-1]
    api.upload_folder(
        folder_path=local_dir,
        repo_id=repo_id,
        path_in_repo=path_in_repo,
        # repo_type="model",
        repo_type="dataset",
        token=token
    )

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
      description="Create and upload a model repository to Hugging Face Hub."
    )
    parser.add_argument("--repo_id", type=str, required=True)
    parser.add_argument("--local_dir", type=str, required=True)
    # parser.add_argument("--token", type=str, required=True)

    args = parser.parse_args()
    main(args.repo_id, args.local_dir)
