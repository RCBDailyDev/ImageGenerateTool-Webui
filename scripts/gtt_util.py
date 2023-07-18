import json
import os
import subprocess

import gradio as gr

folder_symbol = '\U0001f4c2'  # 📂
load_symbol = '\U0001f4bf'  # 💿

img_ext_list = [".png", ".jpg", ".tga", ".bmp", ".webp"]
setting_path = os.path.expanduser('~\\AppData\\Local\\GenerateTesterConfig')

default_path = os.path.abspath(
    os.path.join(os.path.split(os.path.realpath(__file__))[0], os.path.pardir + "\\Temp_Menu"))


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


class Singleton(object):
    def __init__(self, cls):
        self._cls = cls
        self._instance = {}

    def __call__(self):
        if self._cls not in self._instance:
            self._instance[self._cls] = self._cls()
        return self._instance[self._cls]


@Singleton
class ConfigMgr(object):
    def __init__(self):
        self.json_settings = {}
        self.load_json_settings()

    def parse_json_data(self, json_data):
        self.json_settings = {}
        for k in json_data:
            self.json_settings[k] = json_data[k]

    def load_json_settings(self):
        global setting_path
        os.makedirs(setting_path, exist_ok=True)
        json_path = os.path.join(setting_path, "setting.json")
        if not (os.path.exists(json_path) and os.path.isfile(json_path)):
            file = open(json_path, mode='w')
            file.close()
        with open(json_path, mode='r') as json_file:
            try:
                re = json.load(json_file)
                self.parse_json_data(re)
            except:
                self.json_settings = {}

    def save_json_setting(self):
        json_path = os.path.join(setting_path, "setting.json")
        if not (os.path.exists(json_path) and os.path.isfile(json_path)):
            file = open(json_path, mode='w')
            file.close()
        with open(json_path, mode='w') as json_file:
            json.dump(self.json_settings, json_file)

    def get_cfg_value(self, key, default):
        if key in self.json_settings:
            return self.json_settings[key]
        return default


def get() -> ConfigMgr:
    return ConfigMgr()
