import tkinter as tk

from Launcher import PATCH
from OST_helper.UI.tk_objects import TopDownSizeConfig


class StatusBar(tk.Frame):
    def __init__(self, master, message, size_config: TopDownSizeConfig):
        self.size_config = size_config
        super().__init__(master, width=size_config.width,
                         height=size_config.height)
        self.status_bar = None
        self.patch_info = None
        self.add_items(message)

    def add_items(self, message):
        self.size_config.divide([
            [1, 29, 1]
        ])
        self.status_bar = tk.Label(
            self, text=message, relief=tk.SUNKEN, anchor=tk.W)
        self.patch_info = tk.Label(
            self, text="V {}".format(PATCH), anchor=tk.E)
        self.size_config.place([
            [self.status_bar, self.patch_info]
        ])

    def set(self, message):
        self.status_bar.config(text=message)
