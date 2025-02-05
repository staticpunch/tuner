import requests
from bs4 import BeautifulSoup
import os
import subprocess
import argparse
from huggingface_hub import login
token = "HF_TOKEN"
login(token)

def get_file_links(repo_url):
    # Send a GET request to the repository URL
    response = requests.get(repo_url)
    response.raise_for_status()  # Raise an exception for HTTP errors

    # Parse the HTML content using BeautifulSoup
    soup = BeautifulSoup(response.content, 'html.parser')

    # Find all file links
    file_links = []
    for link in soup.find_all('a', href=True):
        href = link['href']
        if href.endswith(('?download=true')):
            link = href[:-len('?download=true')]
            file_links.append(f"https://huggingface.co{link}")

    return file_links

def create_download_script(file_links, download_dir):
    if not os.path.exists(download_dir):
        os.makedirs(download_dir)

    script = "#!/bin/bash\n"
    for link in file_links:
        script += f"""wget {link} --header="Authorization: Bearer {token}" -P {download_dir} &\n"""

    dataname = download_dir.split("/")[-1]
    script_file = f"download_{dataname}.sh"
    with open(script_file, "w") as file:
        file.write(script)

## MADLAD
url = "https://huggingface.co/datasets/allenai/MADLAD-400/tree/main/data/ja"
links = get_file_links(url)
links = [x for x in links if "clean" in x]
create_download_script(links, download_dir="data/MADLAD")

## CulturaX
url = "https://huggingface.co/datasets/uonlp/CulturaX/resolve/main/ja"
filenames = [f"ja_part_{str(i).zfill(5)}.parquet" for i in range(160)]
links = [url + "/" + filename for filename in filenames]
create_download_script(links, download_dir="data/CulturaX")

## CulturaY
url = "https://huggingface.co/datasets/ontocord/CulturaY/tree/main/ja"
links = get_file_links(url)
create_download_script(links, download_dir="data/CulturaY")
