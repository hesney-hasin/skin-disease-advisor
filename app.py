%%writefile /kaggle/working/hf-space/app.py
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import gradio as gr
from app.main import app as fastapi_app
from ui.gradio_app import demo

app = gr.mount_gradio_app(fastapi_app, demo, path="/gradio")