# gpt-tuner
This repo implements a simple LoRA/QLoRA finetuning, 8bit & 4bit quantization. You can finetune models up to 7b parameters with only 24GB GPU.
To install:
```
conda create -n finetune python=3.10
conda activate finetune 
pip install -r requirements.txt 
conda install cudatoolkit
```
demo chat-bloom-3b: https://colab.research.google.com/drive/1CY-dOlwtOqC6TEXJw3BTFiq8-_esEfHB?usp=sharing
