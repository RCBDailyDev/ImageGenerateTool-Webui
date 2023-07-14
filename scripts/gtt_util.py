import json
import os
import subprocess

import gradio as gr

folder_symbol = '\U0001f4c2'  # 📂
load_symbol = '\U0001f4bf'  # 💿

img_ext_list = [".png", ".jpg", ".tga", ".bmp", ".webp"]
setting_path = os.path.expanduser('~\\AppData\\Local\\GenerateTesterConfig')
json_settings = {}


def open_folder(f):
    if not os.path.exists(f) or not os.path.isdir(f):
        os.makedirs(f)
    path = os.path.normpath(f)
    subprocess.Popen(f'explorer /n,"{path}"')


def create_open_folder_button(path, elem_id, visible_in=True):
    button = gr.Button(value=folder_symbol, elem_id=elem_id, variant="tool-top1", visible=visible_in)
    if 'gradio.templates' in getattr(path, "__module__", ""):
        button.click(fn=lambda p: open_folder(p), inputs=[path], outputs=[])
    elif type(path) == gr.components.Textbox:
        button.click(fn=lambda p: open_folder(p), inputs=[path], outputs=[])
        pass
    else:
        button.click(fn=lambda: open_folder(path), inputs=[], outputs=[])
    return button


def parse_json_data(json_data):
    global json_settings
    json_settings = {}
    for k in json_data:
        json_settings[k] = json_data[k]


def load_json_settings():
    global setting_path
    global json_settings
    os.makedirs(setting_path, exist_ok=True)
    json_path = os.path.join(setting_path, "setting.json")
    if not (os.path.exists(json_path) and os.path.isfile(json_path)):
        file = open(json_path, mode='w')
        file.close()
    with open(json_path, mode='r') as json_file:
        try:
            re = json.load(json_file)
            parse_json_data(re)
        except:
            json_settings = {}


def save_json_setting():
    json_path = os.path.join(setting_path, "setting.json")
    if not (os.path.exists(json_path) and os.path.isfile(json_path)):
        file = open(json_path, mode='w')
        file.close()
    with open(json_path, mode='w') as json_file:
        json.dump(json_settings, json_file)


def get_cfg_value(key, default):
    if key in json_settings:
        return json_settings[key]

    return default

