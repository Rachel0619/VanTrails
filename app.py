import gradio as gr
import sys
import os
from dotenv import load_dotenv

load_dotenv()

# Initialize Phoenix tracing BEFORE importing other modules
sys.path.append(os.path.join(os.path.dirname(__file__), 'monitoring'))
from tracing import tracer

sys.path.append(os.path.join(os.path.dirname(__file__), 'src/workflows'))
from recommend_trails import recommend_trails

with gr.Blocks(fill_height=True) as demo:

    gr.Markdown("# Vancouver Hiking Trail Assistant")

    query = gr.Textbox(
        label = "Question",
        placeholder = "Describe the trail you're looking for",
        lines = 3
    )

    with gr.Row():
        submit_btn = gr.Button("Submit", variant="primary", size="lg")
        clear_btn = gr.Button("Clear", variant="secondary", size="lg")
    
    output = gr.Textbox(
        label="Recommendation",
        lines=10
    )

    submit_btn.click(
        fn=recommend_trails,
        inputs=query,
        outputs=output,
        api_name="recommend"
    )

    clear_btn.click(
        fn=lambda: ("",""),
        outputs=[query, output]
    )

demo.launch(server_name="0.0.0.0", server_port=7860)