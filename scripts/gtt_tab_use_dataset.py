import hashlib
import os.path
import random

import gradio as gr
from PIL import Image

from modules import shared
from modules.call_queue import wrap_gradio_gpu_call
from modules.sd_samplers import samplers

try:
    import gtt_util as util
    import gtt_gen_img as gen

except:
    import scripts.gtt_util as util
    import scripts.gtt_gen_img as gen

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
    with gr.Accordion(label="默认参数", open=False):
        with gr.Row():
            sl_img_width = gr.Slider(label='图片宽', value=512, minimum=16, maximum=2048, step=1, interactive=True)
            sl_img_height = gr.Slider(label='图片高', value=512, minimum=16, maximum=2048, step=1, interactive=True)
        ch_use_default_size = gr.Checkbox(label='仅使用默认图片尺寸')
        with gr.Row():
            dr_sampler = gr.Dropdown(label='Sampling method', elem_id=f"sampling",
                                     choices=[" ", *[x.name for x in samplers]], value="Euler a", type="value")
            dr_sampler.__setattr__("do_not_save_to_config", True)
            sl_cfg_scale = gr.Slider(label='CFG强度', value=7, minimum=1, maximum=30, step=1, interactive=True)
            sl_sample_step = gr.Slider(label='采样步数', value=20, interactive=True)
            sl_sample_step.__setattr__("do_not_save_to_config", True)
    with gr.Accordion(label="关键词设置", open=False):
        ch_prompt_mode = gr.Radio(label="关键词模式", choices=["添加", "直接使用"], value='添加')
        tx_prompt = gr.Textbox(label="关键词", lines=3)
        tx_prompt_block = gr.Textbox(label="屏蔽关键词", lines=3)
        tx_neg_prompt = gr.Textbox(label="反向关键词", lines=3)
        tx_replace_prompt = gr.Textbox(label="替换关键词", lines=1)
    with gr.Accordion(label="数量模式"):
        with gr.Row():
            rd_count_mod = gr.Radio(label="数量模式", choices=["每个数据", "绝对数量"], value='每个数据')
        num_gen_count = gr.Number(label="生成数量", value=10)
    with gr.Box():
        ch_save_prompt = gr.Checkbox(label="保存标注", value=cfg_mgr.get_cfg_value("ch_save_prompt", True))
        ch_save_prompt.__setattr__("do_not_save_to_config", True)
        rd_prompt_save_mode = gr.Radio(show_label=False, choices=["原始", "包含附加", "固定"], value="原始",
                                       interactive=True)
        tx_fix_save_prompt = gr.Textbox(label="固定标注", lines=1, value=cfg_mgr.get_cfg_value('tx_fix_save_prompt', "bad-image"), interactive=True)
        tx_fix_save_prompt.__setattr__("do_not_save_to_config", True)
    with gr.Box():
        ch_keep_tree = gr.Checkbox(label="保持文件层级")

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
            return prompt, prompt
        p_list = p.split(',')
        new_p_list = []
        for i in p_list:
            if i not in block_prompt:
                new_p_list.append(i)
        if len(new_p_list) <= 0:
            new_p = ""
        else:
            new_p = ",".join(new_p_list)
        combine_p = new_p
        if prompt:
            combine_p = prompt + "," + new_p
        return combine_p, new_p

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
                        prompt_info_list.append((f_name, p, has_img, img_w, img_h, img_path))
            if len(prompt_info_list) > 0:
                ret_list = []
                if count_mode == "每个数据":
                    choice_list = prompt_info_list * int(gen_count)
                else:
                    choice_list = random.choices(prompt_info_list, k=int(gen_count))
                for p_info in choice_list:
                    gen_info_dic = {}
                    final_prompt = make_final_prompt(p_info[1], prompt, block_prompt, prompt_mode, replace_prompt)
                    gen_info_dic["file_name"] = p_info[0]
                    gen_info_dic["prompt"] = final_prompt[0]
                    gen_info_dic["origin_p"] = final_prompt[1]
                    gen_info_dic["neg_prompt"] = neg_prompt
                    gen_info_dic["cfg_scale"] = cfg_scale
                    gen_info_dic["sample_step"] = sample_step
                    gen_info_dic["sampler"] = sampler if sampler else 'Euler a'
                    gen_info_dic["use_image"] = p_info[2]
                    gen_info_dic["img_width"] = p_info[3]
                    gen_info_dic["img_height"] = p_info[4]
                    gen_info_dic["img_path"] = p_info[5]
                    ret_list.append(gen_info_dic)
                return ret_list

        return []

    def btn_generate_click(_pid, src_dir, dst_dir, w, h, only_default_size, cfg_scale, sample_step, prompt,
                           block_prompt, neg_prompt, count_mode, gen_count, prompt_mode, replace_prompt, sampler,
                           save_prompt, save_prompt_mode, fix_save_prompt, keep_tree):

        gen_info = prepare_gen_info(src_dir, w, h, only_default_size, cfg_scale, sample_step, prompt,
                                    block_prompt, neg_prompt, count_mode, gen_count, prompt_mode, replace_prompt,
                                    sampler)
        shared.state.begin()
        shared.state.job = 'gen_reg_image'
        shared.state.textinfo = "Processing Image"

        shared.state.job_count = len(gen_info)
        shared.state.job_no = 0
        shared.state.interrupted = False

        i = 0
        for info_dic in gen_info:
            if shared.state.interrupted:
                break
            imgs = gen.gen_image(info_dic)
            preview_mgr = util.get_prev_mgr()
            preview_mgr.curr_preview = imgs[0]
            if dst_dir:
                os.makedirs(dst_dir, exist_ok=True)
                file_name = hashlib.sha1(imgs[0].tobytes()).hexdigest()
                true_dir = dst_dir
                if keep_tree:
                    if info_dic["img_path"] is None:
                        true_dir = os.path.join(true_dir, "AutoGen", "auto_gen")
                        os.makedirs(true_dir, exist_ok=True)
                    else:
                        rel = os.path.dirname(os.path.relpath(info_dic["img_path"], src_dir))
                        true_dir = os.path.join(true_dir, rel)
                        os.makedirs(true_dir, exist_ok=True)
                save_path = os.path.join(true_dir, str(file_name) + ".png")
                imgs[0].save(save_path)
                if save_prompt:
                    save_path_txt = os.path.join(true_dir, str(file_name) + ".txt")
                    if save_prompt_mode == "固定" and len(fix_save_prompt) <= 0:
                        pass
                    else:
                        with open(save_path_txt, 'w') as txt:
                            if save_prompt_mode == "原始":
                                txt.write(info_dic["origin_p"])
                            elif save_prompt_mode == "包含附加":
                                txt.write(info_dic["prompt"])
                            else:
                                txt.write(fix_save_prompt)

            i += 1
            shared.state.textinfo = "Generating : " + str((i + 1)) + "/" + str(len(gen_info))
        shared.state.end()
        return "", ""

    btn_generate.click(fn=wrap_gradio_gpu_call(btn_generate_click), _js='gtt_do_process',
                       inputs=[tx_param_buffer1,
                               tx_dataset_dir, tx_output_dir,
                               sl_img_width, sl_img_height,
                               ch_use_default_size,
                               sl_cfg_scale, sl_sample_step, tx_prompt, tx_prompt_block, tx_neg_prompt,
                               rd_count_mod, num_gen_count, ch_prompt_mode, tx_replace_prompt, dr_sampler,
                               ch_save_prompt, rd_prompt_save_mode, tx_fix_save_prompt, ch_keep_tree],
                       outputs=[tx_param_buffer1, tx_param_buffer2])

    def btn_cancel_click():
        shared.state.interrupted = True

    btn_cancel.click(fn=btn_cancel_click, inputs=[], outputs=[])

    def save_cfg_on_change(*args):
        global json_settings
        cfg_mgr = util.get()
        cfg_mgr.set_cfg_value("tx_dataset_dir", args[0])
        cfg_mgr.set_cfg_value("tx_output_dir", args[1])
        cfg_mgr.set_cfg_value("ch_save_prompt", args[2])
        cfg_mgr.set_cfg_value("tx_fix_save_prompt", args[3])
        cfg_mgr.save_json_setting()

    save_com_list = [tx_dataset_dir, tx_output_dir, ch_save_prompt,tx_fix_save_prompt]
    tx_dataset_dir.blur(fn=save_cfg_on_change, inputs=save_com_list, outputs=None)
    tx_output_dir.blur(fn=save_cfg_on_change, inputs=save_com_list, outputs=None)
    ch_save_prompt.change(fn=save_cfg_on_change, inputs=save_com_list, outputs=None)
    tx_fix_save_prompt.change(fn=save_cfg_on_change, inputs=save_com_list, outputs=None)
