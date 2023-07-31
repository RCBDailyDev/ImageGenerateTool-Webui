import os.path

import gradio as gr
from PIL import Image

from modules.call_queue import wrap_gradio_gpu_call
from modules.sd_samplers import samplers

try:
    import gtt_util as util

except:
    import scripts.gtt_util as util

img_ext_list = [".png", ".jpg", ".tga", ".bmp", ".webp"]


def tab_ui():
    cfg_mgr = util.get()
    cfg_mgr.load_json_settings()

    with gr.Row():
        tx_dataset_dir = gr.Text(label="数据集路径", value=cfg_mgr.get_cfg_value('tx_dataset_dir', util.default_path))
        tx_dataset_dir.__setattr__("do_not_save_to_config", True)
        util.create_open_folder_button(tx_dataset_dir, "btn_tx_dataset_dir")
    with gr.Row():
        tx_output_dir = gr.Text(label="输出路径", value=cfg_mgr.get_cfg_value('tx_output_dir', util.default_path))
        tx_output_dir.__setattr__("do_not_save_to_config", True)
        util.create_open_folder_button(tx_output_dir, "btn_tx_output_dir")
    with gr.Box():
        gr.HTML("<p>默认参数</p>")
        with gr.Row():
            sl_img_width = gr.Slider(label='图片宽', value=512, minimum=16, maximum=2048, step=1, interactive=True)
            sl_img_height = gr.Slider(label='图片高', value=512, minimum=16, maximum=2048, step=1, interactive=True)
        ch_use_default_size = gr.Checkbox(label='仅使用默认图片尺寸')
        with gr.Row():
            dr_sampler = gr.Dropdown(label='Sampling method', elem_id=f"sampling",
                                     choices=[" ", *[x.name for x in samplers]], value=" ", type="value")
            sl_cfg_scale = gr.Slider(label='CFG强度', value=7, minimum=1, maximum=30, step=1, interactive=True)
            sl_sample_step = gr.Slider(label='采样步数')
    with gr.Box():
        gr.HTML("<p>关键词设置</p>")
        ch_prompt_mode = gr.Radio(choices=["添加", "直接使用"], value='添加')
        tx_prompt = gr.Textbox(label="关键词", lines=3)
        tx_prompt_block = gr.Textbox(label="屏蔽关键词", lines=3)
        tx_neg_prompt = gr.Textbox(label="反向关键词", lines=3)
        tx_replace_prompt = gr.Textbox(label="替换关键词", lines=1)
    with gr.Box():
        with gr.Row():
            rd_count_mod = gr.Radio(choices=["每个数据", "绝对数量"], value='每个数据')
        num_gen_count = gr.Number(label="生成数量", value=10)
    btn_generate = gr.Button(value='Generate', elem_id="gtt_btn_generate")
    btn_cancel = gr.Button(value='Cancel', elem_id="gtt_btn_cancel", visible=False)

    tx_param_buffer1 = gr.Text(visible=False)
    tx_param_buffer2 = gr.Text(visible=False)

    def find_img(r, file_name):
        '''
        根据文件名查找图片
        :param r:
        :param file_name:
        :return:
        '''
        for ext in img_ext_list:
            img_path = os.path.join(r, file_name + ext)
            if os.path.exists(img_path) and os.path.isfile(img_path):
                return img_path
        return None

    def make_final_prompt(p: str, prompt: str, block_prompt: [str], prompt_mode, replace_prompt):
        if prompt_mode == '直接使用':
            return prompt
        p_list = p.split(',')
        new_p_list = []
        for i in p_list:
            if i not in block_prompt:
                new_p_list.append(i)
        if len(new_p_list) <= 0:
            new_p = ""
        else:
            new_p = ",".join(new_p_list)
        return (prompt + "," + new_p, new_p)

    def prepare_gen_info(src_dir, w, h, only_default_size, cfg_scale, sample_step, prompt,
                         block_prompt, neg_prompt, count_mode, gen_count, prompt_mode, replace_prompt,
                         sampler,
                         data_type='data_set'):
        if os.path.exists(src_dir) and os.path.isdir(src_dir):
            prompt_info_list = []  # [(txt_file_name, prompt, has_img, img_w, img_h)]
            for r, d, fs in os.walk(src_dir):
                for f in fs:
                    f_name, f_ext = os.path.splitext(f)
                    if f_ext == ".txt":
                        txt_path = os.path.join(r, f)
                        with open(txt_path, 'r') as fp:
                            p = fp.read()
                        if len(p) <= 0:
                            continue
                        img_path = find_img(r, f_name)
                        has_img = False
                        img_w = w
                        img_h = h
                        if img_path is not None:
                            has_img = True
                            if not only_default_size:
                                img = Image.open(img_path)
                                img_w = img.width
                                img_h = img.height
                        prompt_info_list.append((f_name, p, has_img, img_w, img_h))
            if len(prompt_info_list) > 0:

        return []

    def btn_generate_click(_pid, src_dir, dst_dir, w, h, only_default_size, cfg_scale, sample_step, prompt,
                           block_prompt, neg_prompt, count_mode, gen_count, prompt_mode, replace_prompt, sampler):

        gen_info = prepare_gen_info(src_dir, w, h, only_default_size, cfg_scale, sample_step, prompt,
                                    block_prompt, neg_prompt, count_mode, gen_count, prompt_mode, replace_prompt,
                                    sampler)
        return "", ""

    btn_generate.click(fn=wrap_gradio_gpu_call(btn_generate_click), _js='do_process',
                       inputs=[tx_param_buffer1,
                               tx_dataset_dir, tx_output_dir,
                               sl_img_width, sl_img_height,
                               ch_use_default_size,
                               sl_cfg_scale, sl_sample_step, tx_prompt, tx_prompt_block, tx_neg_prompt,
                               rd_count_mod, num_gen_count, ch_prompt_mode, tx_replace_prompt, dr_sampler],
                       outputs=[tx_param_buffer1, tx_param_buffer2])

    def save_cfg_on_change(*args):
        global json_settings
        cfg_mgr = util.get()
        cfg_mgr.set_cfg_value("tx_dataset_dir", args[0])
        cfg_mgr.set_cfg_value("tx_output_dir", args[1])
        cfg_mgr.save_json_setting()

    tx_list = [tx_dataset_dir, tx_output_dir]
    tx_dataset_dir.blur(fn=save_cfg_on_change, inputs=tx_list, outputs=None)
    tx_output_dir.blur(fn=save_cfg_on_change, inputs=tx_list, outputs=None)
