import os
import shutil
from safetensors import safe_open

def load_layer(path, layer_idx=33):
	state_dict = {}
	shard_paths = [f for f in os.listdir(path) if f.endswith('.safetensors')]
	for shard_path in sorted(shard_paths, key=lambda x: int(x.split('-')[1])):
		apath = os.path.join(path, shard_path)
		with safe_open(apath, framework="pt", device="cpu") as f:
			for key in f.keys():
				if str(layer_idx) in key:
					state_dict[key] = f.get_tensor(key)
	return state_dict
