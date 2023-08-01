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
                gr.HTML(elem_id="gtt_progress_bar1")
                img_preview = gr.Image(interactive=False)

        btn_update = gr.Button(visible=False, elem_id="gtt_btn_update")
        tx_buffer = gr.Text(visible=False)

        def btn_update_click(img):
            prev_mgr = util.get_prev_mgr()
            if prev_mgr.curr_preview is not None:
                if img == prev_mgr.curr_preview:
                    return gr.skip(), ""
                return gr.update(value=prev_mgr.curr_preview), ""
            return None, ""

        btn_update.click(fn=btn_update_click, inputs=[img_preview],
                         outputs=[img_preview, tx_buffer])

    return (gen_test, "GenerateTester", "rcb_gen_tester"),


script_callbacks.on_ui_tabs(on_tab_ui)
