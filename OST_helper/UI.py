import math
import os
import platform
import re
import time
import tkinter as tk
import tkinter.messagebox
from os.path import dirname, expanduser, isdir, isfile, join
from tkinter import filedialog

import fpdf
from PIL import Image, ImageTk

from Launcher import PATCH, from_json, to_json
from OST_helper.data_handler import Data, Drawer
from OST_helper.data_handler.Drawer import get_total_size_in_mm

# constant
CCCL_PATH = "./resource/default_cccl.json"
SETTING_PATH = "./resource/setting.json"
MCCANNY_LOGO = "./resource/mccanny_logo.ico"
OST_SAMPLE = "./resource/ost_sample.png"

# os
DEVICE_OS = platform.system()


def get_desktop_directory():
    if DEVICE_OS in ["Linux", "Darwin"]:
        home_dir = join(expanduser("~"), "Desktop")
    elif DEVICE_OS in ["Windows"]:
        home_dir = join(os.environ["USERPROFILE"], "Desktop")
    else:
        home_dir = None
    if home_dir is not None and isdir(home_dir):
        return home_dir
    else:
        return "/"


DEFAULT_DIR = get_desktop_directory()

# "course_code": ["course_title", "course_level", "credit", "compulsory"]
default_common_course_code_library = {}
default_setting = {
    "draw_ost_template": True,
    "smart_fill": True,
    "train": True,
    "json_dir": DEFAULT_DIR,
    "img_dir": DEFAULT_DIR,
    "last_session": None,
}

try:
    common_course_code_library = from_json(CCCL_PATH)
    print("Loaded Common Cource Code Library [{} courses]!".format(
        len(common_course_code_library)))
except Exception as exp:
    print(
        "No Common Course code library found, restoring from default..., Error: {}".format(
            str(exp)))
    common_course_code_library = default_common_course_code_library

try:
    setting = from_json(SETTING_PATH)
    if not isdir(setting["json_dir"]):
        setting["json_dir"] = DEFAULT_DIR
        print("json dir no longer is dir, resetting to default")
    if not isdir(setting["img_dir"]):
        setting["img_dir"] = DEFAULT_DIR
        print("image dir no longer is dir, resetting to default")
    if setting["last_session"] is not None and not isfile(
            setting["last_session"]):
        setting["last_session"] = None
        print("last session ost file no longer exist, resetting to default")
    print("Loaded setting!")
except Exception as exp:
    print("No setting found, restoring from default..., Error: {}".format(
        str(exp)))
    setting = default_setting


def finalize():
    to_json(CCCL_PATH, common_course_code_library)
    to_json(SETTING_PATH, setting)
    print("Common course code library saved!")
    print("Setting saved!")


class Application:
    def __init__(self, title="OST Helper", size=(800, 672)):
        width, height = size
        self.root = tk.Tk()
        self.root.minsize(width, height)
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x, y = (screen_width - width) // 2, (screen_height - height) // 2
        self.root.geometry("+{}+{}".format(x, y))
        self.size = size
        self.title = title
        self.update_title()
        self.root.resizable(0, 0)
        # self.root.iconbitmap(mccanny_logo)
        self.root.protocol("WM_DELETE_WINDOW", self.on_exit)
        self.infoFrame = None

    def add_info_frame(self):
        self.infoFrame = InfoFrame(self, self.root, self.size)
        self.infoFrame.pack(side=tk.TOP)

    def on_exit(self):
        self.infoFrame.ending_session()
        Data.finalize()
        Drawer.finalize()
        finalize()
        self.root.destroy()

    def run(self):
        self.add_info_frame()
        self.infoFrame.init_session(default=Data.default_ost)
        self.root.mainloop()

    def update_title(self, tit=None):
        self.root.title("{}{}".format(
            self.title, "" if tit is None else " -{}-".format(tit))
        )


class AdjustmentWindow(tk.Toplevel):
    def __init__(self, master, info_frame, x_offset, y_offset, font_size,
                 spacing, size=(3300 // 4, 2532 // 4 + 200)):
        width, height = size
        super().__init__(master=master, width=width, height=height)
        self.wm_title("Adjustment")
        self.info_frame = info_frame
        self._size = size
        self.resizable(0, 0)
        self.ost_sample = Image.open(OST_SAMPLE)
        self.canvas = None
        self.x_offset = None
        self.y_offset = None
        self.font_size = None
        self.spacing = None
        self.x_offset_val = x_offset
        self.y_offset_val = y_offset
        self.font_size_val = font_size
        self.spacing_val = spacing
        self.ost = None
        self.canceled = True
        self.image = None
        self.add_items(width)
        self.protocol("WM_DELETE_WINDOW", self.cancel)
        self.hide()

    def add_items(self, width):
        frame = tk.Frame(self)
        frame.pack(side="top", fill="both", expand=True)

        self.canvas = tk.Canvas(frame, bg="white", cursor="dot",
                                relief="groove", width=width, height=2550 // 4)
        self.x_offset = ScalePair(frame, "x offset", from_=-1650, to=1650,
                                  command=self.x_offset_action,
                                  size=(width, 40, width / 10))
        self.y_offset = ScalePair(frame, "y offset", from_=-1275, to=1275,
                                  command=self.y_offset_action,
                                  size=(width, 40, width / 10))
        self.font_size = ScalePair(frame, "font size", from_=0, to=100,
                                   command=self.font_size_action,
                                   size=(width, 40, width / 10))
        self.spacing = ScalePair(frame, "spacing", from_=0, to=200,
                                 command=self.spacing_action,
                                 size=(width, 40, width / 10))

        sub_frame = tk.Frame(frame, width=width, height=40)
        cancel = tk.Button(sub_frame, text="Cancel", command=self.cancel)
        confirm = tk.Button(sub_frame, text="Confirm", command=self.confirm,
                            bg="#CC0066", fg="white")
        cancel.place(x=10, y=10, width=(width - 30) / 3 * 1, height=23)
        confirm.place(x=20 + (width - 30) / 3 * 1, y=10,
                      width=(width - 30) / 3 * 2, height=23)

        self.x_offset.set(self.x_offset_val)
        self.y_offset.set(self.y_offset_val)
        self.font_size.set(self.font_size_val)
        self.spacing.set(self.spacing_val)

        self.canvas.pack(side="top")
        self.x_offset.pack(side="top")
        self.y_offset.pack(side="top")
        self.font_size.pack(side="top")
        self.spacing.pack(side="top")
        sub_frame.pack(side="bottom", fill="both", expand=True)

    def x_offset_action(self, _):
        self.update_image()
        pass

    def y_offset_action(self, _):
        self.update_image()
        pass

    def font_size_action(self, _):
        self.update_image()
        pass

    def spacing_action(self, _):
        self.update_image()
        pass

    def cancel(self):
        self.canceled = True
        self.hide()
        self.x_offset.set(self.x_offset_val)
        self.y_offset.set(self.y_offset_val)
        self.font_size.set(self.font_size_val)
        self.spacing.set(self.spacing_val)
        self.ost = None

        self.info_frame.status_bar.set("Adjustment Canceled!")

    def confirm(self):
        self.canceled = False
        self.hide()
        self.x_offset_val = self.x_offset.get()
        self.y_offset_val = self.y_offset.get()
        self.font_size_val = self.font_size.get()
        self.spacing_val = self.spacing.get()
        Drawer.coordinates["Offset"] = (self.x_offset_val, self.y_offset_val)
        self.ost = None

        self.info_frame.status_bar.set("Adjustment Confirmed!")

    def hide(self):
        self.wm_withdraw()
        self.grab_release()

    def show(self, ost):
        p_x = self.info_frame.tk_frame.winfo_rootx()
        p_y = self.info_frame.tk_frame.winfo_rooty()
        p_height = self.info_frame.tk_frame.winfo_height()
        p_width = self.info_frame.tk_frame.winfo_width()
        p_center_x, p_center_y = p_x + p_width // 2, p_y + p_height // 2
        width, height = self._size
        x, y = p_center_x - width // 2, p_center_y - height // 2
        self.wm_geometry("+{}+{}".format(x, y))
        self.ost = ost
        self.update()
        self.deiconify()
        self.grab_set()
        self.update_image()

    def update_image(self):
        x_off, y_off = self.x_offset.get(), self.y_offset.get()
        font_size, spacing = self.font_size.get(), self.spacing.get()
        self.ost.set_font_size(font_size)
        self.ost.set_spacing(spacing)
        img, _ = Drawer.draw(self.ost, False, offset=(x_off, y_off))
        img = img[0][0]
        image = self.ost_sample.copy()
        image.paste(img, (0, 0), img)
        self.image = ImageTk.PhotoImage(
            image=image.resize((3300 // 4, 2550 // 4), Image.ANTIALIAS))
        self.canvas.delete("all")
        # self.canvas.create_rectangle((0, 0, 3300 // 5, 2550 // 5), fill="white")
        self.canvas.create_image(0, 0, anchor="nw", image=self.image)

    def set_x_offset(self, val):
        self.x_offset_val = val
        self.x_offset.set(val)

    def set_y_offset(self, val):
        self.y_offset_val = val
        self.y_offset.set(val)

    def set_font_size(self, val):
        self.font_size_val = val
        self.font_size.set(val)

    def set_spacing(self, val):
        self.spacing_val = val
        self.spacing.set(val)


class ScalePair(tk.Frame):
    def __init__(self, master, text, from_, to, command, size):
        width, height, label_width = size
        super().__init__(master, width=width, height=height)
        self.scale = None
        self.add_item(width, height, label_width, text, from_, to, command)

    def add_item(self, width, height, label_width, text, from_, to, command):
        label = tk.Label(self, text=text)
        self.scale = tk.Scale(self, from_=from_, to=to, orient=tk.HORIZONTAL,
                              repeatinterval=200, command=command,
                              length=width - label_width - 10)
        label.place(x=0, y=0, width=label_width, height=height)
        self.scale.place(x=label_width, y=0)

    def set(self, value):
        self.scale.set(value)

    def get(self):
        return self.scale.get()


class InfoFrame(tk.Frame):
    """
    each info frame represents an ost_info object, it contains all ost info
    """

    def __init__(self, app, master, size):
        super().__init__(master, width=size[0], height=size[1])
        self.app = app
        self.size = size
        self.tk_frame = master
        self.menubar = None
        self.common_info_panel = None
        self.personal_info_panel = None
        self.course_panel = None
        self.other_info_panel = None
        self.utility_panel = None
        self.status_bar = None
        self.save_path = None
        self.adjustment = None
        self.add_panels()

    def add_panels(self):
        availWidth = self.size[0] - 10
        self.menubar = MenuBar(self.tk_frame, self)
        self.common_info_panel = CommonInfoPanel(self, size=(availWidth, 79))
        self.personal_info_panel = PersonalInfoPanel(self,
                                                     size=(availWidth, 79))
        self.course_panel = CoursePanel(self, size=(availWidth, 386))  # 353
        self.other_info_panel = OtherInfoPanel(self, size=(availWidth, 79))
        self.utility_panel = UtilityPanel(self, size=(availWidth, 29))
        self.status_bar = StatusBar(self,
                                    message="Welcome to McCanny OST Entry system!",
                                    size=(self.size[0], 20))
        self.tk_frame.config(menu=self.menubar)
        self.common_info_panel.pack()
        self.personal_info_panel.pack()
        self.course_panel.pack()
        self.other_info_panel.pack()
        self.utility_panel.pack()
        self.status_bar.pack(side=tk.BOTTOM)
        x_offset, y_offset = Drawer.coordinates["Offset"]
        font_size, spacing = Data.default_ost.course_font_size(), Data.default_ost.course_spacing()
        self.adjustment = AdjustmentWindow(self.tk_frame, self,
                                           x_offset=x_offset, y_offset=y_offset,
                                           font_size=font_size, spacing=spacing)

    def init_session(self, default):
        last_session = setting["last_session"]
        if last_session is not None:
            # we load last session file
            ost = Data.OST_info.from_json(last_session)
            self.save_path = last_session
            self.set_ost(ost)
            self.app.update_title(ost.full_name())
            self.status_bar.set("Session restored!")
            return
        # using default
        self.set_ost(default)

    def ending_session(self):
        self.course_panel.train()
        self.save_action()
        if self.save_path is not None:
            setting["last_session"] = self.save_path

    def set_ost(self, ost):
        data = ost.to_data()
        course = data["course_list"]
        self.common_info_panel.set(data)
        self.personal_info_panel.set(data)
        self.course_panel.set(course, sort=False)
        self.other_info_panel.set(data)
        self.utility_panel.set(data)
        self.adjustment.set_font_size(data["course_font_size"])
        self.adjustment.set_spacing(data["course_spacing"])

    def get_ost(self):
        data = {}
        self.common_info_panel.get(data)
        self.personal_info_panel.get(data)
        self.other_info_panel.get(data)
        self.utility_panel.get(data)
        course_list = self.course_panel.get()
        data["course_list"] = course_list
        data["course_font_size"] = self.adjustment.font_size_val
        data["course_spacing"] = self.adjustment.spacing_val
        return Data.OST_info.from_data(data)

    def generate_action(self, print_=True):
        ost = self.get_ost()
        images, file_name = Drawer.draw(ost, setting["draw_ost_template"],
                                        offset=Drawer.coordinates["Offset"])
        user_dir = tk.filedialog.askdirectory(
            parent=self.tk_frame,
            initialdir=setting["img_dir"],
            title="Save OST",
        )
        if not user_dir:
            return
        setting["img_dir"] = user_dir
        # first save the file in to a folder in the destination location
        temp_dir_name = "temp_dir_{}".format(time.time())
        temp_dir = join(user_dir, temp_dir_name)
        try:
            os.makedirs(temp_dir)
        except Exception as e:
            tk.messagebox.showerror(
                parent=self.tk_frame, title="Error",
                message="Can't create folder {} : {}".format(temp_dir, str(e)))
            self.status_bar.set(
                "Error Generating file! Can't create temp folder {} : {}".format(
                    temp_dir, str(e)))
            return
        # first write images to temp location
        img_dirs = []
        for img, name in images:
            image_path = join(temp_dir, name)
            try:
                img.save(image_path, "png")
            except Exception as e:
                tk.messagebox.showerror(
                    parent=self.tk_frame, title="Error",
                    message="Error on generate!\nError: {}".format(str(e)))
                self.status_bar.set(
                    "Error saving file! Error:{}".format(str(e)))
                return
            img_dirs.append(image_path)
        # now we get all the images we can output the pdf.
        mm_width, mm_height = get_total_size_in_mm()
        pdf = fpdf.FPDF(orientation="Landscape", unit="in",
                        format=(mm_height, mm_width))
        pdf.set_auto_page_break(False)
        for img_dir in img_dirs:
            pdf.add_page(orientation="Landscape")
            #  x=0, y=0,
            pdf.image(img_dir, w=mm_width, h=mm_height,
                      type="png")
        pdf.close()
        pdf_out_dir = join(user_dir, file_name)
        pdf.output(name=pdf_out_dir)
        self.status_bar.set("OST generated at {}!".format(pdf_out_dir))
        # now we delete the temp dir and files inside it
        for img_dir in img_dirs:
            os.remove(img_dir)
        # now remove temp dir
        try:
            os.rmdir(temp_dir)
        except OSError as ose:
            tk.messagebox.showerror(
                parent=self.tk_frame, title="OSError",
                message="Can't remove temp folder {} : {}".format(temp_dir,
                                                                  str(ose)))
            self.status_bar.set(
                "Can't remove temp folder {} : {}".format(temp_dir,
                                                          str(ose)))
        # now we move on to print
        if print_:
            self.print_file(pdf_out_dir)

    def print_file(self, file_name):
        # TODO print the pdf file
        pass

    def reset_action(self, ask=True):
        # pop up here
        if ask:
            res = tk.messagebox.askyesno(
                default=tk.messagebox.NO,
                parent=self.tk_frame, title="Warning",
                message="Are you sure to reset?",
                icon=tk.messagebox.WARNING)
        else:
            res = True
        if res:
            self.set_ost(Data.default_ost)
            self.app.update_title("NEW DRAFT")
            self.status_bar.set("Reset Successful!")

    def new_draft_action(self):
        # save the current draft
        self.save_action()
        # new all data
        self.reset_action(ask=False)
        self.save_path = None
        self.status_bar.set("New draft created!")

    def save_action(self):
        if self.save_path is None:
            res = tk.messagebox.askyesno(
                parent=self.tk_frame,
                default=tk.messagebox.YES, title="Save",
                message="Do you want to save the current draft?")
            if res:
                self.save_as_action()
            return
        ost = self.get_ost()
        ost.to_json(self.save_path)
        self.app.update_title(ost.full_name())
        print("Draft saved on {}!".format(self.save_path))
        self.status_bar.set("Draft saved on {}!".format(self.save_path))

    def save_as_action(self):
        path = tk.filedialog.asksaveasfilename(
            parent=self,
            initialdir=setting["json_dir"], title="Save as",
            filetypes=(
                ("JSON files", "*.json"),
                ("all files", "*.*")))
        if not path:
            return
        setting["json_dir"] = dirname(path)
        self.save_path = path
        self.save_action()

    def open_action(self):
        self.save_action()
        path = tk.filedialog.askopenfilename(
            parent=self,
            initialdir=setting["json_dir"], title="Open",
            filetypes=(
                ("JSON files", "*.json"),
                ("all files", "*.*")))
        if not path:
            return
        setting["json_dir"] = dirname(path)
        self.save_path = path
        ost = Data.OST_info.from_json(path)
        self.set_ost(ost)
        self.app.update_title(ost.full_name())
        self.status_bar.set("File opened!")

    def about_action(self):
        tk.messagebox.showinfo(parent=self.tk_frame, title="About",
                               message="This software is developed and licenced by McCanny Secondary School.\nVersion: {}".format(
                                   PATCH))

    def adjust_action(self):
        self.adjustment.show(self.get_ost())


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
            value=setting["draw_ost_template"])
        self.smart_fill = tk.BooleanVar(value=setting["smart_fill"])
        self.train = tk.BooleanVar(value=setting["train"])
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
        self.tools.add_command(label="OST Mass Production Tool")
        self.add_cascade(label="Tools", menu=self.tools)

        self.help = tk.Menu(self, tearoff=0)
        self.help.add_command(label="About",
                              command=self.info_panel.about_action)
        self.add_cascade(label="Help", menu=self.help)

    def toggle_draw_ost_template(self):
        draw_ost_template = self.draw_ost_template.get()
        setting["draw_ost_template"] = draw_ost_template
        self.info_panel.status_bar.set(
            "Draw ost Template has been set to {}!".format(
                "ON" if draw_ost_template else "OFF"))

    def toggle_smart_fill(self):
        smart_fill = self.smart_fill.get()
        setting["smart_fill"] = smart_fill
        self.info_panel.status_bar.set(
            "Smart fill has been set to {}!".format(
                "ON" if smart_fill else "OFF"))

    def toggle_train(self):
        train = self.train.get()
        setting["train"] = train
        self.info_panel.status_bar.set(
            "Train has been set to {}!".format("ON" if train else "OFF"))


class StatusBar(tk.Frame):
    def __init__(self, master, message, size):
        width, height = size
        super().__init__(master, width=width, height=height)
        self.status_bar = None
        self.logo = None
        self.add_items(message, width, height)

    def add_items(self, message, width, height):
        self.status_bar = tk.Label(self, text=message, relief=tk.SUNKEN,
                                   anchor=tk.W)
        self.status_bar.place(x=0, y=0, width=width, height=height)

    def set(self, message):
        self.status_bar.config(text=message)


class UtilityPanel(tk.Frame):
    def __init__(self, master, size):
        width, height = size
        super().__init__(master, width=width, height=height)
        self.master = master
        self.ost_date_of_issue = None
        self.new = None
        self.open = None
        self.generate = None
        self.save = None
        self.adjust = None
        self.add_items(width, height)

    def add_items(self, width, height):
        unit_width, unit_height = (width - 3 * 2) / 8, height - 6
        self.ost_date_of_issue = DatePair(self, "Date of Issue", ("", "", ""), (
            unit_height, unit_width * 2 / 5 * 2, unit_width * 2, 10))
        self.new = tk.Button(self, text="New",
                             command=self.master.new_draft_action)
        self.open = tk.Button(self, text="Open",
                              command=self.master.open_action)
        self.save = tk.Button(self, text="Save",
                              command=self.master.save_action)
        self.adjust = tk.Button(self, text="Adjust...",
                                command=self.master.adjust_action, fg="#CC0066")
        self.generate = tk.Button(self, text="Generate!",
                                  command=self.master.generate_action,
                                  bg="#CC0066", fg="white")

        self.ost_date_of_issue.place(x=3, y=3)
        self.new.place(x=width - (unit_width - 3) * 5 - 25, y=3,
                       width=unit_width, height=unit_height)
        self.open.place(x=width - (unit_width - 3) * 4 - 20, y=3,
                        width=unit_width, height=unit_height)
        self.save.place(x=width - (unit_width - 3) * 3 - 15, y=3,
                        width=unit_width, height=unit_height)
        self.adjust.place(x=width - (unit_width - 3) * 2 - 10, y=3,
                          width=unit_width, height=unit_height)
        self.generate.place(x=width - unit_width - 2, y=3, width=unit_width,
                            height=unit_height)

    def set(self, data):
        date_of_issue = data["OST_date_of_issue"]
        self.ost_date_of_issue.set(date_of_issue)

    def get(self, data):
        date_of_issue = self.ost_date_of_issue.get()
        data["OST_date_of_issue"] = date_of_issue


class CommonInfoPanel(tk.LabelFrame):
    def __init__(self, master, size):
        width, height = size
        super().__init__(master, text="Common Info", width=width, height=height)
        self.name_of_DSB = None
        self.number_of_DSB = None
        self.name_of_school = None
        self.number_of_school = None
        self.add_items(width, height)

    def add_items(self, width, height):
        unit_height = (height - 20) / 2 - 5
        unit_width = (width - 5 * 3) / 5
        long_width_unit = unit_width * 3 / 5
        short_width_unit = unit_width * 2 / 5
        # add name of DSB width 465
        self.name_of_DSB = LabelEntryPair(self,
                                          label_text="Name Of DSB",
                                          entry_placeholder="",
                                          size_config=(
                                              unit_height,
                                              long_width_unit * 2 - 5,
                                              long_width_unit * 3))
        # add number of DSB height 310
        self.number_of_DSB = LabelEntryPair(self,
                                            label_text="Number Of DSB",
                                            entry_placeholder="",
                                            size_config=(
                                                unit_height,
                                                short_width_unit * 2,
                                                short_width_unit * 3))
        # add name of school width 465
        self.name_of_school = LabelEntryPair(self,
                                             label_text="Name Of School",
                                             entry_placeholder="",
                                             size_config=(unit_height,
                                                          long_width_unit * 2 - 5,
                                                          long_width_unit * 3))
        # add number of school height 310
        self.number_of_school = LabelEntryPair(self,
                                               label_text="Number Of School",
                                               entry_placeholder="",
                                               size_config=(unit_height,
                                                            short_width_unit * 2,
                                                            short_width_unit * 3))
        self.name_of_DSB.place(x=5, y=0)
        self.number_of_DSB.place(x=5 + long_width_unit * 5, y=0)
        self.name_of_school.place(x=5, y=unit_height + 5)
        self.number_of_school.place(x=5 + long_width_unit * 5,
                                    y=unit_height + 5)

    def set(self, data):
        name_of_DSB = data["name_of_district_school_board"]
        number_of_DSB = data["district_school_board_number"]
        name_of_school = data["name_of_school"]
        number_of_school = data["school_number"]
        self.name_of_DSB.set(name_of_DSB)
        self.number_of_DSB.set(number_of_DSB)
        self.name_of_school.set(name_of_school)
        self.number_of_school.set(number_of_school)

    def get(self, data):
        name_of_DSB = self.name_of_DSB.get()
        number_of_DSB = self.number_of_DSB.get()
        name_of_school = self.name_of_school.get()
        number_of_school = self.number_of_school.get()
        data["name_of_district_school_board"] = name_of_DSB
        data["district_school_board_number"] = number_of_DSB
        data["name_of_school"] = name_of_school
        data["school_number"] = number_of_school


class PersonalInfoPanel(tk.LabelFrame):
    def __init__(self, master, size):
        width, height = size
        super().__init__(master, text="Personal Info", width=width,
                         height=height)
        self.surname = None
        self.given_name = None
        self.gender = None
        self.date_of_birth = None
        self.OEN = None
        self.student_number = None
        self.date_of_entry = None
        self.add_items(width, height)

    def add_items(self, width, height):
        unit_height = (height - 20) / 2 - 5
        date_width = (width - 5 * 5) / 3
        gender_width = date_width * 2 / 5
        name_width = gender_width * 2
        self.surname = LabelEntryPair(self,
                                      label_text="Surname",
                                      entry_placeholder="",
                                      size_config=(
                                          unit_height, name_width / 10 * 3,
                                          name_width / 10 * 7))
        self.given_name = LabelEntryPair(self,
                                         label_text="Given Name",
                                         entry_placeholder="",
                                         size_config=(
                                             unit_height, name_width / 10 * 4,
                                             name_width / 10 * 6))
        self.gender = LabelEntryPair(self,
                                     label_text="Gender",
                                     entry_placeholder="",
                                     size_config=(unit_height, gender_width / 2,
                                                  gender_width / 2))
        self.date_of_birth = DatePair(self,
                                      text="Date of Birth",
                                      date=(0, 0, 0),
                                      size_config=(unit_height, date_width / 3,
                                                   date_width / 3 * 2 - 5, 10))
        self.OEN = LabelEntryPair(self,
                                  label_text="OEN/MIN",
                                  entry_placeholder="",
                                  size_config=(
                                      unit_height, date_width / 10 * 3 - 15,
                                      date_width / 10 * 7 + 15))
        self.student_number = LabelEntryPair(self,
                                             label_text="Student Number",
                                             entry_placeholder="",
                                             size_config=(
                                                 unit_height,
                                                 date_width / 10 * 4,
                                                 date_width / 10 * 6 + 5))
        self.date_of_entry = DatePair(self,
                                      text="Date of Entry",
                                      date=(0, 0, 0),
                                      size_config=(unit_height, date_width / 3,
                                                   date_width / 3 * 2 - 5, 10))
        self.surname.place(x=5, y=0)
        self.given_name.place(x=5 * 2 + name_width, y=0)
        self.gender.place(x=5 * 3 + name_width * 2, y=0)
        self.date_of_birth.place(x=5 * 4 + name_width * 2 + gender_width, y=0)
        self.OEN.place(x=5, y=unit_height + 5)
        self.student_number.place(x=5 * 2 + date_width, y=unit_height + 5)
        self.date_of_entry.place(x=5 * 4 + date_width * 2, y=unit_height + 5)

    def set(self, data):
        surename, given_name = data["name"]
        gender = data["gender"]
        date_of_birth = data["date_of_birth"]
        OEN = data["OEN"]
        student_number = data["student_number"]
        date_of_entry = data["date_of_entry"]
        self.surname.set(surename)
        self.given_name.set(given_name)
        self.gender.set(gender)
        self.date_of_birth.set(date_of_birth)
        self.OEN.set(OEN)
        self.student_number.set(student_number)
        self.date_of_entry.set(date_of_entry)

    def get(self, data):
        surename = self.surname.get()
        given_name = self.given_name.get()
        gender = self.gender.get()
        date_of_birth = self.date_of_birth.get()
        OEN = self.OEN.get()
        student_number = self.student_number.get()
        date_of_entry = self.date_of_entry.get()
        name = [surename, given_name]
        data["name"] = name
        data["gender"] = gender
        data["date_of_birth"] = date_of_birth
        data["OEN"] = OEN
        data["student_number"] = student_number
        data["date_of_entry"] = date_of_entry


class CoursePanel(tk.LabelFrame):
    def __init__(self, master, size):
        width, height = size
        super().__init__(master, text="Courses", width=width, height=height)
        self.index = 0
        self.courses = []
        self.canvas = None
        self.frame = None
        self.add = None
        self.date_label = None
        self.grade_label = None
        self.title_label = None
        self.code_label = None
        self.percentage_label = None
        self.credit_label = None
        self.compulsory_label = None
        self.note_label = None
        self.scrollBar = None
        self.sort = None
        self.credit_summary = None
        self.compulsory_summary = None
        self.avail_width = 0
        self.visible_on_screen = 10
        self._order_widgets = {
            0: "delete",
            1: "date",
            2: "grade",
            3: "title",
            4: "code",
            5: "percentage",
            6: "credit",
            7: "compulsory",
            8: "note",
        }
        self._widgets_order = {
            val: key for key, val in self._order_widgets.items()}
        self.add_items(width, height)

    def add_course(self, sync=True):
        c = CoursePair(self.frame, self.master, (self.avail_width - 5, 24),
                       self.delete_action, self.count_credit,
                       self.count_compulsory, self.count_courses,
                       self.next_action, self.enter_action, self.prev_action,
                       self.right_action, self.left_action)
        self.courses.append(c)
        self.index += 1
        c.grid(row=self.index, column=0, ipadx=0, ipady=2)
        if sync:
            self.set_focus(self.index - 1, "code")
        c.bind_all("<MouseWheel>", self.mouse_scroll, add=True)
        return c

    def sync_canvas_loc(self, index):
        if self.index < self.visible_on_screen:
            return
        screen_index = index // self.visible_on_screen
        total_screens = math.ceil(self.index / self.visible_on_screen)
        self.after(10, self.canvas.yview_moveto, screen_index / total_screens)

    def mouse_scroll(self, event):
        self.canvas.yview_scroll(-1 * (event.delta / 120), "units")

    def left_action(self, event):
        widget = event.widget
        for i in range(len(self.courses)):
            key = self.courses[i].get_selected(widget)
            if key is not None and key in self._widgets_order:
                left_index = (self._widgets_order[key] - 1) % 9
                self.set_focus(i, self._order_widgets[left_index])
                return

    def right_action(self, event):
        widget = event.widget
        for i in range(len(self.courses)):
            key = self.courses[i].get_selected(widget)
            if key is not None and key in self._widgets_order:
                right_index = (self._widgets_order[key] + 1) % 9
                self.set_focus(i, self._order_widgets[right_index])
                return

    def enter_action(self, event):
        widget = event.widget
        for i in range(len(self.courses)):
            key = self.courses[i].get_selected(widget)
            if key is not None:
                # here we process some special cases
                # code -> percentage
                # percentage -> next line code
                if key == "code":
                    self.set_focus(i, "percentage")
                else:
                    if i + 1 >= len(self.courses):
                        # we add a new courses
                        self.add_course(sync=False)
                    # the widget is in this course, then we move it to next
                    if key == "percentage":
                        self.set_focus(i + 1, "code")
                    else:
                        self.set_focus(i + 1, key)
                return

    def next_action(self, event):
        widget = event.widget
        for i in range(len(self.courses)):
            key = self.courses[i].get_selected(widget)
            if key is not None:
                # the widget is in this course, then we move it to next
                self.set_focus(i + 1, key)
                return

    def prev_action(self, event):
        widget = event.widget
        for i in range(len(self.courses)):
            key = self.courses[i].get_selected(widget)
            if key is not None:
                # the widget is in this course, then we move it to next
                self.set_focus(i - 1, key)
                return

    def set_focus(self, index, key):
        if 0 <= index < len(self.courses):
            # it's an valid index
            self.courses[index].set_selected(key)
            self.sync_canvas_loc(index)

    def delete_action(self, event):
        c = event.widget.master
        self.next_action(event)
        c.destroy()
        self.index -= 1
        self.courses.remove(c)
        self.count_credit()
        self.count_compulsory()
        self.count_courses()

    def count_courses(self):
        total_course = sum([1 for course in self.courses if course.is_course()])
        self.add.config(text="+ ADD Course{}".format(
            "" if self.index == 0 else " ({})".format(total_course)))
        return True

    def count_credit(self):
        value = sum([c.calculate_credit() for c in self.courses])
        if not isinstance(value, int) and value.is_integer():
            value = int(value)
        self.credit_summary.config(text=str(value))
        return True

    def count_compulsory(self):
        value = len([c for c in self.courses if c.is_compulsory_active()])
        self.compulsory_summary.config(text=str(value))
        return True

    def train(self, _=None):
        if not setting["train"]:
            return
        train_able = [course.train_data() for course in self.courses]
        train_able = [data for data in train_able if
                      data[0] != "" and data[1] != "" and data[2] != "" and
                      data[3] != ""]
        for code, title, level, credit, compulsory in train_able:
            common_course_code_library[code.upper()] = (
                title, level, credit, compulsory)
        self.master.status_bar.set(
            "{} Trained!".format(
                ",".join(code for code, _, _, _, _ in train_able)))

    def sort_course(self):
        try:
            active_course = []
            inactive_course = []
            for c in self.courses:
                date = c.get_date()
                if date[2]:
                    active_course.append((date, c))
                else:
                    inactive_course.append((date, c))
        except Exception as e:
            tk.messagebox.showerror(parent=self, title="Sort Error",
                                    message="An Error has occurs when sorting. Please try again!\nThis is usually caused by incorrect format of the date.\nThe allowed format includes:\n->2000\\10\n->2000/10\n->2000-10\n->2000.10\n->2000 10\nError: {}".format(
                                        str(e)))
            return
        # first remove all the widget from the frame
        for c in self.courses:
            c.grid_remove()
        active_course.sort(key=lambda pair: (pair[0][0], pair[0][1]))
        index = 0
        for date, c in active_course:
            c.grid(row=index, column=0, ipadx=0, ipady=2)
            index += 1
        for date, c in inactive_course:
            c.grid(row=index, column=0, ipadx=0, ipady=2)
            index += 1

    def add_items(self, width, height):
        self.canvas = tk.Canvas(self, bd=0, highlightthickness=0)
        self.frame = tk.Frame(self.canvas)
        self.add = tk.Button(self, text="+ ADD Course", command=self.add_course,
                             bg="#669966", fg="white")
        self.date_label = tk.Label(self, text="Date", anchor=tk.S)
        self.grade_label = tk.Label(self, text="Grad.", anchor=tk.S)
        self.title_label = tk.Label(self, text="Course Title", anchor=tk.S)
        self.code_label = tk.Label(self, text="Code", anchor=tk.S)
        self.percentage_label = tk.Label(self, text="Perc.", anchor=tk.S)
        self.credit_label = tk.Label(self, text="Cred.", anchor=tk.S)
        self.compulsory_label = tk.Label(self, text="Comp.", anchor=tk.S)
        self.note_label = tk.Label(self, text="Note", anchor=tk.S)
        self.scrollBar = tk.Scrollbar(self, orient="vertical",
                                      command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.scrollBar.set)
        self.sort = tk.Button(self, text="Sort", command=self.sort_course,
                              bg="#669966", fg="white")
        self.credit_summary = tk.Label(self, text="0", anchor=tk.N)
        self.compulsory_summary = tk.Label(self, text="0", anchor=tk.N)
        avail_width = width - 20 - 10 - 5
        avail_height = height - 20 - 24 - 24 - 24 - 9 - 5
        unit_avail_width = (avail_width - 5 - 5 * 8 - 24) / 20
        # 10 * (24 + 2) + 20 + 24 + 24 + 5
        self.add.place(x=5, y=0, width=width - 15, height=24)

        self.date_label.place(x=5 + 2 + 24 + unit_avail_width * 0 + 5 * 1, y=24,
                              width=unit_avail_width * 2, height=24)
        self.grade_label.place(x=5 + 2 + 24 + unit_avail_width * 2 + 5 * 2,
                               y=24, width=unit_avail_width * 1, height=24)
        self.title_label.place(x=5 + 2 + 24 + unit_avail_width * 3 + 5 * 3,
                               y=24, width=unit_avail_width * 10, height=24)
        self.code_label.place(x=5 + 2 + 24 + unit_avail_width * 13 + 5 * 4,
                              y=24, width=unit_avail_width * 2, height=24)
        self.percentage_label.place(
            x=5 + 2 + 24 + unit_avail_width * 15 + 5 * 5, y=24,
            width=unit_avail_width * 1, height=24)
        self.credit_label.place(x=5 + 2 + 24 + unit_avail_width * 16 + 5 * 6,
                                y=24, width=unit_avail_width * 1, height=24)
        self.compulsory_label.place(
            x=5 + 2 + 24 + unit_avail_width * 17 + 5 * 7, y=24,
            width=unit_avail_width * 1, height=24)
        self.note_label.place(x=5 + 2 + 24 + unit_avail_width * 18 + 5 * 8,
                              y=24, width=unit_avail_width * 2, height=24)

        self.canvas.place(x=5, y=24 + 24, width=avail_width,
                          height=avail_height)
        self.scrollBar.place(x=width - 20 - 5 - 5, y=24 + 24, width=20,
                             height=avail_height)
        self.canvas.create_window((0, 0), window=self.frame, anchor="nw")

        self.sort.place(x=5 + 2 + 24 + unit_avail_width * 0 + 5 * 1,
                        y=24 + avail_height + 5 + 24,
                        width=unit_avail_width * 2, height=24)
        self.credit_summary.place(x=5 + 2 + 24 + unit_avail_width * 16 + 5 * 6,
                                  y=24 + avail_height + 5 + 24,
                                  width=unit_avail_width * 1, height=24)
        self.compulsory_summary.place(
            x=5 + 2 + 24 + unit_avail_width * 17 + 5 * 7,
            y=24 + avail_height + 5 + 24, width=unit_avail_width * 1, height=24)

        def conf(_):
            self.canvas.config(scrollregion=self.canvas.bbox("all"),
                               width=avail_width, height=avail_height)

        self.frame.bind("<Configure>", conf)
        self.avail_width = avail_width
        self.bind("<FocusOut>", self.train)
        self.canvas.bind_all("<MouseWheel>", self.mouse_scroll)

    def set(self, courses, sort=True):
        for c in self.courses:
            c.grid_remove()
        self.courses.clear()
        self.index = 0
        for data in courses:
            c = self.add_course()
            c.set(data)
        if sort:
            self.sort_course()
        self.count_courses()
        self.count_compulsory()
        self.count_credit()

    def get(self):
        course = [c.get() for c in self.courses]
        return course


class OtherInfoPanel(tk.LabelFrame):
    def __init__(self, master, size):
        width, height = size
        super().__init__(master, text="Other Info", width=width, height=height)
        self.community_involvement_var = None
        self.community_involvement = None
        self.literacy_requirement_var = None
        self.literacy_requirement = None
        self.specialized_program = None
        self.diploma_or_certificate = None
        self.diploma_or_certificate_date_of_issue = None
        self.authorization = None
        self.add_items(width, height)

    def add_items(self, width, height):
        unit_width, unit_height = (width - 3 * 4) / 10, (height - 20) / 2 - 5
        self.community_involvement_var = tk.BooleanVar()
        self.community_involvement = tk.Checkbutton(self,
                                                    text="Community Involvement",
                                                    variable=self.community_involvement_var)
        self.literacy_requirement_var = tk.BooleanVar()
        self.literacy_requirement = tk.Checkbutton(self,
                                                   text="Provincial Literacy Requirement",
                                                   variable=self.literacy_requirement_var)
        self.specialized_program = LabelEntryPair(self, "Specialized Program",
                                                  "", (unit_height, (
                    unit_width * 5) / 10 * 3, (unit_width * 5) / 10 * 7))
        self.diploma_or_certificate = LabelEntryPair(self,
                                                     "Diploma or Certificate",
                                                     "", (unit_height, (
                    unit_width * 5) / 3 * 1, (unit_width * 5) / 3 * 2))
        self.diploma_or_certificate_date_of_issue = SimpleDatePair(self, (
            "2000", "1"), (unit_height, unit_width, 5))
        self.authorization = LabelEntryPair(self, "Authorization", "", (
            unit_height, (unit_width * 4) / 4 * 1, (unit_width * 4) / 4 * 3))
        self.community_involvement.grid(row=0, column=0, rowspan=1,
                                        columnspan=2, sticky=tk.NW)
        self.literacy_requirement.grid(row=0, column=2, rowspan=1, columnspan=3,
                                       sticky=tk.NW)
        self.specialized_program.grid(row=0, column=5, rowspan=1, columnspan=5,
                                      sticky=tk.NW, ipadx=3, ipady=3)
        self.diploma_or_certificate.grid(row=1, column=0, rowspan=1,
                                         columnspan=5, sticky=tk.NW)
        self.diploma_or_certificate_date_of_issue.grid(row=1, column=5,
                                                       rowspan=1, columnspan=1,
                                                       sticky=tk.NW)
        self.authorization.grid(row=1, column=6, rowspan=1, columnspan=4,
                                sticky=tk.NW, ipadx=3, ipady=3)

    def set(self, data):
        community_involvement = data["community_involvement_flag"]
        literacy_requirement = data[
            "provincial_secondary_school_literacy_requirement_flag"]
        specialized_program = data["specialized_program"]
        diploma_or_certificate = data["diploma_or_certificate"]
        diploma_or_certificate_date_of_issue = data[
            "diploma_or_certificate_date_of_issue"]
        authorization = data["authorization"]
        self.community_involvement_var.set(community_involvement)
        self.literacy_requirement_var.set(literacy_requirement)
        self.specialized_program.set(specialized_program)
        self.diploma_or_certificate.set(diploma_or_certificate)
        self.diploma_or_certificate_date_of_issue.set(
            diploma_or_certificate_date_of_issue)
        self.authorization.set(authorization)

    def get(self, data):
        community_involvement = self.community_involvement_var.get()
        literacy_requirement = self.literacy_requirement_var.get()
        specialized_program = self.specialized_program.get()
        diploma_or_certificate = self.diploma_or_certificate.get()
        diploma_or_certificate_date_of_issue = self.diploma_or_certificate_date_of_issue.get()
        authorization = self.authorization.get()
        data["community_involvement_flag"] = community_involvement
        data[
            "provincial_secondary_school_literacy_requirement_flag"] = literacy_requirement
        data["specialized_program"] = specialized_program
        data["diploma_or_certificate"] = diploma_or_certificate
        data[
            "diploma_or_certificate_date_of_issue"] = diploma_or_certificate_date_of_issue
        data["authorization"] = authorization


class CoursePair(tk.Frame):
    def __init__(self, master, info_frame, size_config, button_action,
                 count_credit, count_compulsory, count_course, next_action,
                 enter_action, prev_action, right_action, left_action):
        width, height = size_config
        super().__init__(master, width=width, height=height)
        self.delete = None
        self.date = None
        self.grade = None
        self.title = None
        self.code = None
        self.percentage = None
        self.credit = None
        self.compulsory = None
        self.note = None
        self._widgets = None
        self._ordered_widgets = None
        self._inv_ordered_widgets = None
        self.info_frame = info_frame
        self.add_items(width, height, button_action, count_credit,
                       count_compulsory, count_course, next_action,
                       enter_action, prev_action, right_action, left_action)

    def add_items(self, width, height, button_action, count_credit,
                  count_compulsory, count_course, next_action, enter_action,
                  prev_action, right_action, left_action):
        def smart_fill(_):
            self.smart_fill()
            count_course()
            count_compulsory()
            count_credit()

        unit_height = height
        unit_width = (width - 5 * 8 - height) / 20
        self.delete = tk.Button(master=self, text="X", bg="#CC0066", fg="white")
        self.delete.bind("<Button-1>", button_action)
        self.date = tk.Entry(master=self, bd=2)
        self.grade = tk.Entry(master=self, bd=2)
        self.title = tk.Entry(master=self, bd=2)
        self.code = tk.Entry(master=self, bd=2)
        self.percentage = tk.Entry(master=self, bd=2)
        self.credit = tk.Entry(master=self, bd=2, validate="focusout",
                               validatecommand=count_credit)
        self.compulsory = tk.Entry(master=self, bd=2, validate="focusout",
                                   validatecommand=count_compulsory)
        self.note = tk.Entry(master=self, bd=2)
        self._widgets = {
            "delete": self.delete,
            "date": self.date,
            "grade": self.grade,
            "title": self.title,
            "code": self.code,
            "percentage": self.percentage,
            "credit": self.credit,
            "compulsory": self.compulsory,
            "note": self.note,
        }
        # bind some action
        self.code.bind("<Tab>", smart_fill, add=True)
        # next action
        self.date.bind("<Return>", enter_action)
        self.grade.bind("<Return>", enter_action)
        self.title.bind("<Return>", enter_action)
        self.code.bind("<Return>", enter_action)
        self.code.bind("<Return>", smart_fill, add=True)
        self.percentage.bind("<Return>", enter_action)
        self.credit.bind("<Return>", enter_action)
        self.compulsory.bind("<Return>", enter_action)
        self.note.bind("<Return>", enter_action)
        # Down
        self.date.bind("<Down>", next_action)
        self.grade.bind("<Down>", next_action)
        self.title.bind("<Down>", next_action)
        self.code.bind("<Down>", next_action)
        self.code.bind("<Down>", smart_fill, add=True)
        self.percentage.bind("<Down>", next_action)
        self.credit.bind("<Down>", next_action)
        self.compulsory.bind("<Down>", next_action)
        self.note.bind("<Down>", next_action)
        # prev action
        self.date.bind("<Up>", prev_action)
        self.grade.bind("<Up>", prev_action)
        self.title.bind("<Up>", prev_action)
        self.code.bind("<Up>", prev_action)
        self.code.bind("<Up>", smart_fill, add=True)
        self.percentage.bind("<Up>", prev_action)
        self.credit.bind("<Up>", prev_action)
        self.compulsory.bind("<Up>", prev_action)
        self.note.bind("<Up>", prev_action)
        # left action
        self.delete.bind("<Left>", left_action)
        self.date.bind("<Left>", left_action)
        self.grade.bind("<Left>", left_action)
        self.title.bind("<Left>", left_action)
        self.code.bind("<Left>", left_action)
        self.code.bind("<Left>", smart_fill, add=True)
        self.percentage.bind("<Left>", left_action)
        self.credit.bind("<Left>", left_action)
        self.compulsory.bind("<Left>", left_action)
        self.note.bind("<Left>", left_action)
        # right action
        self.delete.bind("<Right>", right_action)
        self.date.bind("<Right>", right_action)
        self.grade.bind("<Right>", right_action)
        self.title.bind("<Right>", right_action)
        self.code.bind("<Right>", right_action)
        self.code.bind("<Right>", smart_fill, add=True)
        self.percentage.bind("<Right>", right_action)
        self.credit.bind("<Right>", right_action)
        self.compulsory.bind("<Right>", right_action)
        self.note.bind("<Right>", right_action)
        # delete action
        self.delete.bind("<Delete>", button_action)
        self.date.bind("<Delete>", button_action)
        self.grade.bind("<Delete>", button_action)
        self.title.bind("<Delete>", button_action)
        self.code.bind("<Delete>", button_action)
        self.percentage.bind("<Delete>", button_action)
        self.credit.bind("<Delete>", button_action)
        self.compulsory.bind("<Delete>", button_action)
        self.note.bind("<Delete>", button_action)
        # self.date.insert(tk.END, date_text)
        # self.grade.insert(tk.END, grade_text)
        # self.title.insert(tk.END, title_text)
        # self.code.insert(tk.END, code_text)
        # self.percentage.insert(tk.END, percentage_text)
        # self.credit.insert(tk.END, credit_text)
        # self.compulsory.insert(tk.END, compulsory_text)
        # self.note.insert(tk.END, note_text)
        self.delete.place(x=0, y=0, width=height, height=unit_height)
        self.date.place(x=unit_width * 0 + 5 * 1 + height, y=0,
                        width=unit_width * 2, height=unit_height)
        self.grade.place(x=unit_width * 2 + 5 * 2 + height, y=0,
                         width=unit_width * 1, height=unit_height)
        self.title.place(x=unit_width * 3 + 5 * 3 + height, y=0,
                         width=unit_width * 10, height=unit_height)
        self.code.place(x=unit_width * 13 + 5 * 4 + height, y=0,
                        width=unit_width * 2, height=unit_height)
        self.percentage.place(x=unit_width * 15 + 5 * 5 + height, y=0,
                              width=unit_width * 1, height=unit_height)
        self.credit.place(x=unit_width * 16 + 5 * 6 + height, y=0,
                          width=unit_width * 1, height=unit_height)
        self.compulsory.place(x=unit_width * 17 + 5 * 7 + height, y=0,
                              width=unit_width * 1, height=unit_height)
        self.note.place(x=unit_width * 18 + 5 * 8 + height, y=0,
                        width=unit_width * 2, height=unit_height)

    def get_selected(self, widget):
        if widget is None:
            return None
        for key, val in self._widgets.items():
            if val == widget:
                return key
        return None

    def set_selected(self, key):
        if key is None:
            return
        widget = self._widgets[key]
        widget.focus_set()
        if key == "delete":
            return
        # select text
        widget.select_range(0, 'end')
        # move cursor to the end
        widget.icursor('end')

    def smart_fill(self):
        if not setting["smart_fill"]:
            return
        code = self.code.get().upper()
        if code not in common_course_code_library:
            return
        title, level, credit, compulsory = common_course_code_library[code]
        if self.title.get() == "":
            self.title.insert(0, title)
        if self.grade.get() == "":
            self.grade.insert(0, level)
        if self.credit.get() == "":
            self.credit.insert(0, credit)
        if self.compulsory.get() == "":
            self.compulsory.insert(0, compulsory)
        self.info_frame.status_bar.set("{} Smart filled!".format(code))

    def is_compulsory_active(self):
        return self.compulsory.get() != ""

    def calculate_credit(self):
        try:
            return float(self.credit.get())
        except ValueError:
            return 0

    def is_course(self):
        return self.code.get() != ""

    def train_data(self):
        code, title, level, credit, compulsory = self.code.get(), self.title.get(), self.grade.get(), self.credit.get(), self.compulsory.get()
        return code, title, level, credit, compulsory

    def get_date(self):
        date = self.date.get()
        if date == "":
            return 0, 0, False
        result = re.findall("([\d]+)[\\\/\-.\s]([\d]+)", string=date)[0]
        year, month = result
        # first process the year
        if len(year) == 4:
            int_year = int(year)
        elif len(year) == 2:
            int_year = int("20" + year)
        else:
            raise Exception("Year format error")
        # then the month
        int_month = int(month)
        if int_month > 12:
            raise Exception("Month format error")
        return int_year, int_month, True

    def set(self, data):
        if type(data) is Data.Course:
            date, level, title, code, percentage, credit, compulsory, note = data.date, data.level, data.title, data.code, data.percentage, data.credit, data.compulsory, data.note
        else:
            date, level, title, code, percentage, credit, compulsory, note = data
        set_entry_value(self.date, date)
        set_entry_value(self.grade, level)
        set_entry_value(self.title, title)
        set_entry_value(self.code, code)
        set_entry_value(self.percentage, percentage)
        set_entry_value(self.credit, credit)
        set_entry_value(self.compulsory, compulsory)
        set_entry_value(self.note, note)

    def get(self):
        date, level, title, code, percentage, credit, compulsory, note = self.date.get(), self.grade.get(), self.title.get(), self.code.get(), self.percentage.get(), self.credit.get(), self.compulsory.get(), self.note.get()
        return Data.Course(date_=date, level=level, title=title, code=code,
                           percentage=percentage, credit=credit,
                           compulsory=compulsory, note=note)


class LabelEntryPair(tk.Frame):
    def __init__(self, master, label_text, entry_placeholder, size_config):
        # (height, label width, entry width)
        height, label_width, entry_width = size_config
        super().__init__(master, width=label_width + entry_width, height=height)
        self.label = None
        self.entry = None
        self.add_items(height, label_width, entry_width, label_text,
                       entry_placeholder)

    def add_items(self, height, label_width, entry_width, label_text,
                  entry_placeholder):
        self.label = tk.Label(master=self, text=label_text, anchor=tk.W)
        self.entry = tk.Entry(master=self, bd=2)
        self.entry.insert(tk.END, entry_placeholder)
        self.label.place(x=0, y=0, width=label_width, height=height)
        self.entry.place(x=label_width, y=0, width=entry_width, height=height)

    def set(self, value):
        set_entry_value(self.entry, value)

    def get(self):
        return self.entry.get()


class DatePair(tk.Frame):
    def __init__(self, master, text, date, size_config, spacing_text="-"):
        # (height, label_width, unit_width, spacing)
        height, label_width, date_width, spacing = size_config
        unit_width = (date_width - 2 * spacing) / 3
        year, month, day = date
        super().__init__(master,
                         width=unit_width * 3 + spacing * 2 + label_width,
                         height=height)
        self.label = None
        self.entry_year = None
        self.entry_month = None
        self.entry_day = None
        self.add_items(height, text, label_width, unit_width, spacing,
                       spacing_text, year, month, day)

    def add_items(self, height, text, label_width, unit_width, spacing,
                  spacing_text, year, month, day):
        label = tk.Label(master=self, text=text, anchor=tk.W)
        entry_year = tk.Entry(master=self, bd=2)
        entry_year.insert(tk.END, year)
        spacing_1 = tk.Label(master=self, text=spacing_text, anchor=tk.CENTER)
        entry_month = tk.Entry(master=self, bd=2)
        entry_month.insert(tk.END, month)
        spacing_2 = tk.Label(master=self, text=spacing_text, anchor=tk.CENTER)
        entry_day = tk.Entry(master=self, bd=2)
        entry_day.insert(tk.END, day)
        self.label = label
        self.entry_year = entry_year
        self.entry_month = entry_month
        self.entry_day = entry_day
        label.place(x=0, y=0, width=label_width, height=height)
        entry_year.place(x=label_width, y=0, width=unit_width, height=height)
        spacing_1.place(x=label_width + unit_width, y=0, width=spacing,
                        height=height)
        entry_month.place(x=label_width + unit_width + spacing, y=0,
                          width=unit_width, height=height)
        spacing_2.place(x=label_width + unit_width * 2 + spacing, y=0,
                        width=spacing, height=height)
        entry_day.place(x=label_width + unit_width * 2 + spacing * 2, y=0,
                        width=unit_width, height=height)

    def set(self, date):
        year, month, day = date
        set_entry_value(self.entry_year, year)
        set_entry_value(self.entry_month, month)
        set_entry_value(self.entry_day, day)

    def get(self):
        year, month, day = self.entry_year.get(), self.entry_month.get(), self.entry_day.get()
        return [year, month, day]


class SimpleDatePair(tk.Frame):
    def __init__(self, master, date, size_config, spacing_text="-"):
        # (height, width, spacing)
        height, width, spacing = size_config
        unit_width = (width - spacing) / 2
        year, month = date
        super().__init__(master, width=width, height=height)
        self.entry_year = None
        self.entry_month = None
        self.add_items(height, unit_width, spacing, spacing_text, year, month)

    def add_items(self, height, unit_width, spacing, spacing_text, year, month):
        entry_year = tk.Entry(master=self, bd=2)
        entry_year.insert(tk.END, year)
        spacing_1 = tk.Label(master=self, text=spacing_text, anchor=tk.CENTER)
        entry_month = tk.Entry(master=self, bd=2)
        entry_month.insert(tk.END, month)
        self.entry_year = entry_year
        self.entry_month = entry_month
        entry_year.place(x=0, y=0, width=unit_width, height=height)
        spacing_1.place(x=unit_width, y=0, width=spacing, height=height)
        entry_month.place(x=unit_width + spacing, y=0, width=unit_width,
                          height=height)

    def set(self, date):
        year, month = date
        set_entry_value(self.entry_year, year)
        set_entry_value(self.entry_month, month)

    def get(self):
        year, month = self.entry_year.get(), self.entry_month.get()
        return [year, month]


def set_entry_value(entry_target, value):
    entry_target.delete(0, tk.END)
    entry_target.insert(0, value)


if __name__ == '__main__':

    def test(event):
        print('keysym:', event.keysym)


    root = tk.Tk()

    root.bind('<Key>', test)

    root.mainloop()
