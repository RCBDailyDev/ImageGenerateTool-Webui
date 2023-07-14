import gradio as gr
import subprocess
from modules import shared, devices, script_callbacks
from modules.call_queue import wrap_gradio_call, wrap_gradio_gpu_call
from modules.shared import opts, OptionInfo

try:
    import gtt_util as util
except:
    import scripts.gtt_util as util

import importlib

importlib.reload(util)


def on_tab_ui():
    with gr.Blocks(analytics_enabled=False, css=r"..\style.css") as gen_test:
        with gr.Row():
            with gr.Column():
                gr.HTML("<h2>生成测试</h2>")
            with gr.Column():
                gr.Image(interactive=False)

    return (gen_test, "GenerateTester", "rcb_gen_tester"),


script_callbacks.on_ui_tabs(on_tab_ui)
