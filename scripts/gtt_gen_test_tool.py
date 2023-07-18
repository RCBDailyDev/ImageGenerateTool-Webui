import gradio as gr
import subprocess
from modules import shared, devices, script_callbacks
from modules.call_queue import wrap_gradio_call, wrap_gradio_gpu_call
from modules.shared import opts, OptionInfo

try:
    import gtt_util as util
    import gtt_tab_use_dataset as dataset_ui
except:
    import scripts.gtt_util as util
    import scripts.gtt_tab_use_dataset as dataset_ui

import importlib

importlib.reload(util)
importlib.reload(dataset_ui)


def on_tab_ui():
    util.get()
    with gr.Blocks(analytics_enabled=False, css=r"..\style.css") as gen_test:
        with gr.Row():
            with gr.Column():
                gr.HTML("<h2>生成测试</h2>")
                with gr.Tab("使用训练集生成"):
                    dataset_ui.tab_ui()
                with gr.Tab("使用csv生成"):
                    gr.HTML("<h2>使用csv生成</h2>")
            with gr.Column():
                gr.Image(interactive=False)

    return (gen_test, "GenerateTester", "rcb_gen_tester"),


script_callbacks.on_ui_tabs(on_tab_ui)
