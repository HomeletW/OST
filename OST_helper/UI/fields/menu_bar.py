import tkinter as tk

from OST_helper.UI.dialogs import ProductionDialog
from OST_helper.parameter import *


class MenuBar(tk.Menu):
    def __init__(self, master, info_panel):
        super().__init__(master)
        self.file_menu = None
        self.setting = None
        self.tools = None
        self.help = None
        self.info_panel = info_panel
        # setting
        self.draw_ost_template = tk.BooleanVar(
            value=SETTING["draw_ost_template"])
        self.smart_fill = tk.BooleanVar(value=SETTING["smart_fill"])
        self.train = tk.BooleanVar(value=SETTING["train"])
        self.add_items()

    def add_items(self):
        self.file_menu = tk.Menu(self, tearoff=0)
        self.file_menu.add_command(label="New",
                                   command=self.info_panel.new_draft_action)
        self.file_menu.add_command(label="Open",
                                   command=self.info_panel.open_action)
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Save",
                                   command=self.info_panel.save_action)
        self.file_menu.add_command(label="Save as...",
                                   command=self.info_panel.save_as_action)
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Reset",
                                   command=self.info_panel.reset_action)
        self.add_cascade(label="File", menu=self.file_menu)

        self.setting = tk.Menu(self, tearoff=0)
        self.setting.add_checkbutton(label="Draw OST Template when output",
                                     variable=self.draw_ost_template,
                                     command=self.toggle_draw_ost_template)
        self.setting.add_separator()
        self.setting.add_command(label="Adjust...",
                                 command=self.info_panel.adjust_action)
        self.setting.add_separator()
        self.setting.add_checkbutton(label="Smart fill",
                                     variable=self.smart_fill,
                                     command=self.toggle_smart_fill)
        self.setting.add_checkbutton(label="Train",
                                     variable=self.train,
                                     command=self.toggle_train)
        self.add_cascade(label="Setting", menu=self.setting)

        self.tools = tk.Menu(self, tearoff=0)
        self.tools.add_command(label="Production Tool",
                               command=self.start_production)
        self.add_cascade(label="Tools", menu=self.tools)

        self.help = tk.Menu(self, tearoff=0)
        self.help.add_command(label="About",
                              command=self.info_panel.about_action)
        self.add_cascade(label="Help", menu=self.help)

    def start_production(self):
        # first we display a dialog to ask user for some parm
        production_dialog = ProductionDialog(
            self.master, self.info_panel, "", "", SETTING["draw_ost_template"]
        )
        production_dialog.start()

    def toggle_draw_ost_template(self):
        draw_ost_template = self.draw_ost_template.get()
        SETTING["draw_ost_template"] = draw_ost_template
        self.info_panel.status_bar.set(
            "Draw ost Template has been set to {}!".format(
                "ON" if draw_ost_template else "OFF"))

    def toggle_smart_fill(self):
        smart_fill = self.smart_fill.get()
        SETTING["smart_fill"] = smart_fill
        self.info_panel.status_bar.set(
            "Smart fill has been set to {}!".format(
                "ON" if smart_fill else "OFF"))

    def toggle_train(self):
        train = self.train.get()
        SETTING["train"] = train
        self.info_panel.status_bar.set(
            "Train has been set to {}!".format("ON" if train else "OFF"))
