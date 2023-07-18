import gradio as gr

from modules.call_queue import wrap_gradio_gpu_call

try:
    import gtt_util as util

except:
    import scripts.gtt_util as util


def tab_ui():
    cfg_mgr = util.get()
    with gr.Row():
        tx_dataset_dir = gr.Text(label="数据集路径", value=cfg_mgr.get_cfg_value('tx_dataset_dir', util.default_path))
        util.create_open_folder_button(tx_dataset_dir, "btn_tx_dataset_dir")
    with gr.Row():
        tx_output_dir = gr.Text(label="输出路径", value=cfg_mgr.get_cfg_value('tx_output_dir', util.default_path))
        util.create_open_folder_button(tx_output_dir, "btn_tx_output_dir")
    with gr.Box():
        gr.HTML("<p>默认参数</p>")
        with gr.Row():
            sl_img_width = gr.Slider(label='图片宽', value=512, minimum=16, maximum=2048, step=1, interactive=True)
            sl_img_height = gr.Slider(label='图片高', value=512, minimum=16, maximum=2048, step=1, interactive=True)
        ch_use_default_size = gr.Checkbox(label='仅使用默认图片尺寸')
        with gr.Row():
            sl_cfg_scale = gr.Slider(label='CFG强度', value=7, minimum=1, maximum=30, step=1, interactive=True)
            sl_sample_step = gr.Slider(label='采样步数')
    with gr.Box():
        tx_prompt = gr.Textbox(label="prompt", lines=3)
        tx_prompt_block = gr.Textbox(label="prompt_block", lines=3)
        tx_neg_prompt = gr.Textbox(label="negative prompt", lines=3)
    with gr.Box():
        with gr.Row():
            rd_count_mod = gr.Radio(choices=["每个数据", "绝对数量"])
        num_gen_count = gr.Number(label="生成数量", value=10)
    btn_generate = gr.Button(value='Generate', elem_id="gtt_btn_generate")
    btn_cancel = gr.Button(value='Cancel', elem_id="gtt_btn_cancel", visible=False)

    tx_param_buffer1 = gr.Text(visible=False)
    tx_param_buffer2 = gr.Text(visible=False)

    def prepare_gen_info(src_dir, w, h, only_default_size, cfg_scale, sample_step, prompt,
                           block_prompt, neg_prompt, count_mod, gen_count, data_type = 'data_set'):



    def btn_generate_click(_pid, src_dir, dst_dir, w, h, only_default_size, cfg_scale, sample_step, prompt,
                           block_prompt, neg_prompt, count_mod, gen_count):

        pass

    btn_generate.click(fn=wrap_gradio_gpu_call(btn_generate_click), _js='do_process',
                       inputs=[tx_param_buffer1,
                               tx_dataset_dir, tx_output_dir,
                               sl_img_width, sl_img_height,
                               ch_use_default_size,
                               sl_cfg_scale, sl_sample_step, tx_prompt, tx_prompt_block, tx_neg_prompt,
                               rd_count_mod, num_gen_count],
                       outputs=[tx_param_buffer1, tx_param_buffer2])
