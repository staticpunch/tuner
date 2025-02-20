import gradio as gr
import yaml
import os
import subprocess
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Generator
import queue
import threading
import time

def get_default_paths() -> Dict[str, str]:
    """Generate default paths with current date."""
    date_str = datetime.now().strftime("%Y%m%d")
    return {
        "model_a": "/raid/HUB_LLM/Llama-3.3-70B-Instruct",
        "model_b": "/raid/HUB_LLM/080225_vi_test_llama33_70b_instruct/checkpoint-2568",
        "config": f"/raid/dont15/merge-configs/slerp-{date_str}.yaml",
        "output": "/raid/HUB_LLM/080225_vi_test_llama33_70b_instruct/checkpoint-2568/SLERP-GUI"
    }

class StreamingOutput:
    def __init__(self, max_buffer_lines: int = 1000):
        self.queue = queue.Queue()
        self.finished = False
        self.buffer = []
        self.max_buffer_lines = max_buffer_lines
        
    def write(self, text: str):
        lines = text.splitlines(keepends=True)  # Keep line endings
        for line in lines:
            self.queue.put(line)
            self.buffer.append(line)
            # Maintain buffer size
            if len(self.buffer) > self.max_buffer_lines:
                self.buffer.pop(0)
        
    def read(self) -> Generator[str, None, None]:
        # First yield entire buffer
        yield "".join(self.buffer)
        
        while True:
            try:
                # Non-blocking queue get
                text = self.queue.get_nowait()
                yield text
            except queue.Empty:
                if self.finished:
                    break
                time.sleep(0.1)
                
    def close(self):
        self.finished = True

def _stream_output(pipe, stream_output: StreamingOutput, prefix: str = ""):
    """Helper function to stream output from a pipe"""
    try:
        with pipe:
            for line in iter(pipe.readline, ''):
                if line:
                    if prefix and line.strip():  # Only add prefix for non-empty lines
                        stream_output.write(f"{prefix}{line}")
                    else:
                        stream_output.write(line)
    except (ValueError, IOError):
        pass  # Pipe has been closed

def stream_subprocess_output(process: subprocess.Popen, stream_output: StreamingOutput):
    """Stream subprocess output to StreamingOutput using separate threads for stdout and stderr"""
    stdout_thread = threading.Thread(
        target=_stream_output,
        args=(process.stdout, stream_output),
        daemon=True
    )
    stderr_thread = threading.Thread(
        target=_stream_output,
        args=(process.stderr, stream_output, "ERROR: "),
        daemon=True
    )
    
    stdout_thread.start()
    stderr_thread.start()
    
    # Wait for process to complete
    process.wait()
    
    # Wait for output threads to finish
    stdout_thread.join()
    stderr_thread.join()
    
    stream_output.close()

def create_slerp_config(
    model_a: str,
    model_b: str,
    base_model_choice: str,
    config_path: str,
    output_dir: str,
    self_attn_values: str,
    mlp_values: str,
    fallback_value: str,
    use_cuda: bool,
    gpu_indices: str,
    dtype: str,
    progress=gr.Progress()
) -> Generator[str, None, None]:
    """Create SLERP mergekit config and run the merge operation with streaming output."""
    
    try:
        self_attn = [float(x.strip()) for x in self_attn_values.split(',')]
        mlp = [float(x.strip()) for x in mlp_values.split(',')]
        fallback = float(fallback_value)
    except ValueError:
        yield "Error: Invalid interpolation values. Please use comma-separated numbers for arrays and a single number for fallback."
        return

    # Map the choice to actual path
    base_model = model_a if base_model_choice == "Model A" else model_b

    if not os.path.exists(os.path.dirname(config_path)):
        try:
            os.makedirs(os.path.dirname(config_path))
        except Exception as e:
            yield f"Error creating config directory: {str(e)}"
            return

    config = {
        "models": [
            {"model": model_a},
            {"model": model_b}
        ],
        "merge_method": "slerp",
        "base_model": base_model,
        "parameters": {
            "t": [
                {
                    "filter": "self_attn",
                    "value": self_attn
                },
                {
                    "filter": "mlp",
                    "value": mlp
                },
                {
                    "value": fallback
                }
            ]
        },
        "dtype": dtype
    }

    try:
        os.makedirs(output_dir, exist_ok=True)
        with open(config_path, 'w') as f:
            yaml.dump(config, f)
    except Exception as e:
        yield f"Error saving config file: {str(e)}"
        return

    # Build command and environment
    env = os.environ.copy()
    if use_cuda and gpu_indices.strip():
        env["CUDA_VISIBLE_DEVICES"] = gpu_indices.strip()
    
    cmd = ["mergekit-yaml", config_path, output_dir]
    if use_cuda:
        cmd.append("--cuda")
    
    cmd_str = ""
    if use_cuda and gpu_indices.strip():
        cmd_str += f"CUDA_VISIBLE_DEVICES={gpu_indices.strip()} "
    cmd_str += " ".join(cmd)
    
    yield f"Starting merge with command:\n{cmd_str}\n\n"
    
    stream_output = StreamingOutput(max_buffer_lines=500)  # Keep last 500 lines
    
    process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=env,
        text=True,
        bufsize=1,
        universal_newlines=True
    )
    
    # Start output streaming in a separate thread
    threading.Thread(
        target=stream_subprocess_output,
        args=(process, stream_output),
        daemon=True
    ).start()
    
    # Yield output as it becomes available
    for text in stream_output.read():
        yield text

    if process.returncode != 0:
        yield "\nMerge process failed."
    else:
        yield "\nMerge completed successfully!"

def update_visible_components(method: str):
    """Update visibility of components based on selected merge method."""
    if method == "SLERP":
        return {
            slerp_container: gr.update(visible=True)
        }
    return {}

def update_gpu_indices(use_cuda):
    """Update GPU indices textbox interactivity based on CUDA checkbox."""
    return gr.update(interactive=use_cuda)

# Create the Gradio interface
with gr.Blocks(
    title="MergeKit GUI",
    css=".gradio-container { max-width:1000px; margin: auto; }"
) as app:
    gr.Markdown("# MergeKit Model Merger")
    
    # Method selector at the top
    merge_method = gr.Dropdown(
        choices=["SLERP"],  # Add more methods here in the future
        value="SLERP",
        label="Merge Method",
        container=False
    )

    # SLERP-specific components
    with gr.Column(visible=True) as slerp_container:
        with gr.Row():
            # Left column - Paths and basic settings
            with gr.Column():
                default_paths = get_default_paths()
                model_a = gr.Textbox(
                    label="Model A Path",
                    value=default_paths["model_a"],
                    placeholder="Path to first model"
                )
                model_b = gr.Textbox(
                    label="Model B Path",
                    value=default_paths["model_b"],
                    placeholder="Path to second model"
                )
                base_model = gr.Dropdown(
                    choices=["Model A", "Model B"],
                    value="Model A",
                    label="Base Model"
                )
                config_path = gr.Textbox(
                    label="Config File Path",
                    value=default_paths["config"],
                    placeholder="Path for saving config YAML"
                )
                output_dir = gr.Textbox(
                    label="Output Directory",
                    value=default_paths["output"],
                    placeholder="Directory for merged model output"
                )
                
            # Right column - SLERP parameters
            with gr.Column():
                self_attn_values = gr.Textbox(
                    label="Self Attention Interpolation Values",
                    placeholder="0, 0.3, 0.5, 0.7, 1",
                    value="0, 0.3, 0.5, 0.7, 1"
                )
                mlp_values = gr.Textbox(
                    label="MLP Interpolation Values",
                    placeholder="1, 0.7, 0.5, 0.3, 0",
                    value="1, 0.7, 0.5, 0.3, 0"
                )
                fallback_value = gr.Textbox(
                    label="Fallback Interpolation Value",
                    value="0.5",
                    placeholder="Default interpolation value"
                )
                dtype = gr.Dropdown(
                    choices=["bfloat16", "float16", "float32"],
                    value="bfloat16",
                    label="Data Type"
                )
                with gr.Row():
                    use_cuda = gr.Checkbox(
                        label="Use CUDA",
                        value=True
                    )
                    gpu_indices = gr.Textbox(
                        label="GPU Indices (e.g. 0,1)",
                        placeholder="0,1",
                        interactive=True
                    )
    
    with gr.Row():
        merge_btn = gr.Button("Merge Models", variant="primary")
        
    output = gr.Textbox(
        label="Output Log",
        lines=20,  # Show more lines in the UI
        max_lines=20,
        autoscroll=True,  # Enable autoscrolling
        interactive=False  # Prevent editing
    )
    
    # Event handlers
    merge_method.change(
        fn=update_visible_components,
        inputs=[merge_method],
        outputs=[slerp_container]
    )
    
    use_cuda.change(
        fn=update_gpu_indices,
        inputs=[use_cuda],
        outputs=[gpu_indices]
    )
    
    merge_btn.click(
        fn=create_slerp_config,
        inputs=[
            model_a,
            model_b,
            base_model,
            config_path,
            output_dir,
            self_attn_values,
            mlp_values,
            fallback_value,
            use_cuda,
            gpu_indices,
            dtype
        ],
        outputs=output
    )

if __name__ == "__main__":
    app.queue().launch(
        share=False,
        server_name="0.0.0.0",
        server_port=8808
    )
## to run: python mergerkit-gui.py
