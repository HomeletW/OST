import threading
import time
import tkinter as tk
import tkinter.filedialog
import tkinter.messagebox
from os import listdir
from os.path import basename, split
from tkinter import font
from tkinter.ttk import Progressbar

from PIL import ImageTk

from OST_helper.UI.tk_objects import DEFAULT_SPACING, ScalePair, \
    TopDownSizeConfig
from OST_helper.data_handler import Drawer
from OST_helper.parameter import *


class AdjustmentWindow(tk.Toplevel):
    def __init__(self, master, info_frame, x_offset, y_offset, font_size,
                 spacing):
        width, height = COORDINATES["Size"]
        c_width, c_height = width // 4, height // 4
        self.size_config = TopDownSizeConfig(width=c_width, height=250)
        self._size = c_width, c_height + 250
        self.canvas_size = c_width, c_height
        super().__init__(master=master, width=c_width, height=c_height + 250)
        self.wm_title("Adjustment")
        self.wm_iconbitmap(APP_LOGO)
        self.info_frame = info_frame
        self.resizable(0, 0)
        self.ost_sample = OST_SAMPLE_IMAGE
        self.canvas = None
        self.x_offset = None
        self.y_offset = None
        self.font_size = None
        self.spacing = None
        self.main_frame = None
        self.sub_frame = None
        self.cancel_button = None
        self.confirm_button = None
        self.image_update_thread = None
        self.lock = threading.Lock()
        self.update_image_finished = False
        self.x_offset_val = x_offset
        self.y_offset_val = y_offset
        self.font_size_val = font_size
        self.spacing_val = spacing
        self.ost = None
        self.canceled = True
        self.image = None
        self.add_items(width, height, c_width, c_height)
        self.protocol("WM_DELETE_WINDOW", self.cancel)
        self.hide()

    def add_items(self, a_width, a_height, c_width, c_height):
        self.main_frame = tk.Frame(self)
        width, height = self._size
        self.main_frame.place(x=0, y=0, width=width, height=height)
        divided = self.size_config.divide([
            [1, 1],
            [1, 1],
            [1, 1],
            [1, 1],
            [1, 1, 2],
        ], internal=False)
        self.canvas = tk.Canvas(self.main_frame, bg="white", cursor="dot",
                                relief="groove", width=c_width,
                                height=c_height)
        self.sub_frame = tk.Frame(self.main_frame)
        self.x_offset = ScalePair(self.sub_frame, "X offset",
                                  from_=-a_width, to=a_width,
                                  command=self.x_offset_action,
                                  size_config=divided[0][0])
        self.y_offset = ScalePair(self.sub_frame, "Y offset",
                                  from_=-a_height, to=a_height,
                                  command=self.y_offset_action,
                                  size_config=divided[1][0])
        self.font_size = ScalePair(self.sub_frame, "Font Size (pt)",
                                   from_=0, to=100,
                                   command=self.font_size_action,
                                   size_config=divided[2][0])
        self.spacing = ScalePair(self.sub_frame, "Spacing",
                                 from_=-10, to=200,
                                 command=self.spacing_action,
                                 size_config=divided[3][0])
        self.cancel_button = tk.Button(self.sub_frame, text="Cancel",
                                       command=self.cancel)
        self.confirm_button = tk.Button(self.sub_frame, text="Confirm",
                                        command=self.confirm)
        self.x_offset.set(self.x_offset_val)
        self.y_offset.set(self.y_offset_val)
        self.font_size.set(self.font_size_val)
        self.spacing.set(self.spacing_val)
        # place the canvas
        self.canvas.place(x=0, y=0, width=c_width, height=c_height)
        self.sub_frame.place(x=0, y=c_height, width=c_width, height=250)
        self.size_config.place([
            [self.x_offset],
            [self.y_offset],
            [self.font_size],
            [self.spacing],
            [self.cancel_button, self.confirm_button],
        ])

    def x_offset_action(self, _):
        self.update_image()

    def y_offset_action(self, _):
        self.update_image()

    def font_size_action(self, _):
        self.update_image()

    def spacing_action(self, _):
        self.update_image()

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
        COORDINATES["Offset"] = (self.x_offset_val, self.y_offset_val)
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
        # self.wait_visibility()

    def update_image(self):
        with self.lock:
            if self.image_update_thread is None:
                self.update_image_finished = False
                self.image_update_thread = threading.Thread(
                    target=self._update_image, name="Update Image", daemon=True
                )
                self.image_update_thread.start()
                self.after(50, self._check_update_image_thread)

    def _check_update_image_thread(self):
        if self.update_image_finished:
            # clear the thread
            with self.lock:
                self.image_update_thread = None
        else:
            self.after(50, self._check_update_image_thread)

    def _update_image(self):
        x_off, y_off = self.x_offset.get(), self.y_offset.get()
        font_size, spacing = self.font_size.get(), self.spacing.get()
        self.ost.set_font_size(font_size)
        self.ost.set_spacing(spacing)
        img, _ = Drawer.draw(self.ost, False, offset=(x_off, y_off))
        img = img[0][0]
        image = self.ost_sample.copy()
        image.paste(img, (0, 0), img)
        c_width, c_height = self.canvas_size
        self.image = ImageTk.PhotoImage(
            image=image.resize((c_width, c_height), Image.ANTIALIAS))
        self.canvas.delete("all")
        # self.canvas.create_rectangle((0, 0, 3300 // 5, 2550 // 5), fill="white")
        self.canvas.create_image(0, 0, anchor="nw", image=self.image)
        self.update_image_finished = True

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


class Tracker:
    def init(self, *args, **kwargs):
        pass

    def tick(self, *args, **kwargs):
        pass

    def end(self, *args, **kwargs):
        pass

    def log(self, *args, **kwargs):
        pass


class ThreadMonitorDialog(tk.Toplevel, Tracker):
    def __init__(self, master, title, info_frame, func, **kwargs):
        width, height = 714, 400
        self.size_config = TopDownSizeConfig(width=width, height=height)
        super().__init__(master=master, width=width, height=height)
        self.transient(master)
        self.title(title)
        self.wm_iconbitmap(APP_LOGO)
        self.resizable(0, 0)
        self.info_frame = info_frame
        self.thread_finished = False
        kwargs["progress_dialog"] = self
        self.thread = threading.Thread(target=func, name=title, kwargs=kwargs)
        self._start_time = None
        self.main_frame = None
        self.detail = None
        self.progress = None
        self.ok = None
        self.green = "#669966"
        self.red = "#CC0066"
        self.logger = logging.getLogger(title)
        self.add_items(width, height)
        self.grab_set()
        self.initial_focus = self.main_frame
        self.protocol("WM_DELETE_WINDOW", self.exit)

    def start(self):
        p_x = self.info_frame.tk_frame.winfo_rootx()
        p_y = self.info_frame.tk_frame.winfo_rooty()
        p_height = self.info_frame.tk_frame.winfo_height()
        p_width = self.info_frame.tk_frame.winfo_width()
        p_center_x, p_center_y = p_x + p_width // 2, p_y + p_height // 2
        width, height = self.size_config.size()
        x, y = p_center_x - width // 2, p_center_y - height // 2
        self.wm_geometry("+{}+{}".format(x, y))
        if not self.initial_focus:
            self.initial_focus = self
        self.initial_focus.focus_set()
        self.update()
        self.deiconify()
        self.start_process()
        self.wait_window(self)

    def init(self, total):
        self._start_time = time.time()
        self.progress['maximum'] = total

    def tick(self, text, amount=1, **kwargs):
        self.log(text, **kwargs)
        self.progress.step(amount=amount)

    def log(self, text, prefix="\n", suffix=""):
        self.logger.info(text)
        self.detail.config(state=tk.NORMAL)
        self.detail.insert(tk.END, "{}{}{}".format(prefix, text, suffix))
        self.detail.see(tk.END)
        self.detail.config(state=tk.DISABLED)

    def end(self, error=False):
        self.thread_finished = True
        self.progress["value"] = self.progress["maximum"]
        time_elapsed = time.time() - self._start_time if self._start_time is not None else "Unknown"
        self.log(
            "Time Elapsed {}".format(self._format_time(time_elapsed))
                .center(80, "=")
        )
        if error:
            self.ok.config(text="Process Failed, Press to Exit!")
        else:
            self.ok.config(text="Process Succeed, Press to Exit!")
        self.ok.config(state=tk.NORMAL)

    @staticmethod
    def _format_time(time_):
        hours, rem = divmod(time_, 3600)
        minutes, second = divmod(rem, 60)
        return "{:0>2}:{:0>2}:{:0>2}".format(int(hours), int(minutes),
                                             int(second))

    def add_items(self, width, height):
        self.main_frame = tk.Frame(self)
        self.main_frame.place(x=0, y=0, width=width, height=height)
        self.size_config.divide([
            [8, 1],
            [1, 1],
            [1, 1],
        ], internal=False)
        self.detail = tk.Text(
            master=self, state=tk.DISABLED, relief=tk.SUNKEN, borderwidth=2,
            width=80,
            font=font.Font(size=12)
        )
        self.detail.debug(True)
        self.progress = Progressbar(
            master=self,
            orient=tk.HORIZONTAL,
            mode="determinate")
        self.ok = tk.Button(master=self, text="Working...", command=self.exit)
        self.ok.config(state=tk.DISABLED)
        self.size_config.place([
            [self.detail],
            [self.progress],
            [self.ok],
        ])

    def start_process(self):
        self.log("Starting Process".center(80, "="), prefix="")
        self.thread.start()

    def exit(self, _=None):
        if not self.thread_finished:
            tk.messagebox.showwarning(
                parent=self, title="Process not Finished!",
                message="Process not Finished!\n")
            return
        self.master.focus_set()
        self.destroy()


EMPTY_TRACKER = Tracker()


class ProductionDialog(tk.Toplevel):
    """
    To start a production we need the following parameter

    -> ask the directory for where the json files are
    -> ask the directory for where the pdf files should be saved
    -> does draw ost template
    """

    def __init__(self, master, info_frame, json_value, output_value,
                 draw_ost_template):
        width, height = 600, 300
        self.size_config = TopDownSizeConfig(width, height)
        super().__init__(master=master, width=width, height=height)
        self.transient(master)
        self.info_frame = info_frame
        self.title("Production Tool")
        self.wm_iconbitmap(APP_LOGO)
        self.resizable(0, 0)
        self.main_frame = None
        self.description_label = None
        self.json_var = None
        self.json_value = json_value
        self.choose_json_button = None
        self.choose_json_label = None
        self.output_var = None
        self.output_value = output_value
        self.choose_output_button = None
        self.choose_output_label = None
        self.draw_template_var = None
        self.draw_ost_template_check = None
        self.overwrite_output_var = None
        self.overwrite_output = None
        self.cancel_button = None
        self.start_button = None
        self.add_items(width, height, draw_ost_template)
        self.grab_set()
        self.initial_focus = self.main_frame
        self.protocol("WM_DELETE_WINDOW", self.cancel)

    def cancel(self):
        self.master.focus_set()
        self.destroy()

    def start(self):
        p_x = self.info_frame.tk_frame.winfo_rootx()
        p_y = self.info_frame.tk_frame.winfo_rooty()
        p_height = self.info_frame.tk_frame.winfo_height()
        p_width = self.info_frame.tk_frame.winfo_width()
        p_center_x, p_center_y = p_x + p_width // 2, p_y + p_height // 2
        width, height = self.size_config.size()
        x, y = p_center_x - width // 2, p_center_y - height // 2
        self.wm_geometry("+{}+{}".format(x, y))
        if not self.initial_focus:
            self.initial_focus = self
        self.initial_focus.focus_set()
        self.update()
        self.deiconify()
        self.wait_window(self)

    def start_production(self):
        json_dir = self.json_value
        output_dir = self.output_value
        draw_template = self.draw_template_var.get()
        overwrite_output = self.overwrite_output_var.get()
        if not json_dir or not output_dir:
            tk.messagebox.showerror(
                parent=self, title="Can't Start Production",
                message="Can't start production right now\n"
                        "\n"
                        "Please choose production directory and output location"
                        " before proceeding."
            )
            return
        tmd = ThreadMonitorDialog(
            self, "Production", self.info_frame, self._production,
            json_dir=json_dir, output_dir=output_dir,
            draw_template=draw_template,
            overwrite_output=overwrite_output,
        )
        tmd.start()

    def _production(self, progress_dialog: Tracker, json_dir, output_dir,
                    draw_template, overwrite_output):
        jsons = listdir(json_dir)
        progress_dialog.init(len(jsons))
        for j in jsons:
            json_path = join(json_dir, j)
            if not isfile(json_path):
                progress_dialog.tick(
                    "✗ {} : Not a file.".format(j)
                )
            else:
                ret = self.info_frame.production(
                    json_path,
                    output_dir,
                    draw_template,
                    overwrite_output
                )
                if ret in [PRODUCTION_FILE_NOT_RECOGNIZED]:
                    progress_dialog.tick(
                        "✗ {} : Can't Recognize, Not a project file".format(j)
                    )
                elif ret in [PRODUCTION_FILE_EXISTS]:
                    progress_dialog.tick(
                        "✗ {} : Can't save PDF (file exists in output location)"
                            .format(j)
                    )
                else:
                    progress_dialog.tick(
                        "✔ {} : Successful!".format(j)
                    )
        progress_dialog.tick("➜ Finished!")
        progress_dialog.end()
        # try to open folder
        try:
            open_path(output_dir)
            progress_dialog.log("✔ Output Directory opened!")
        except Exception as e:
            progress_dialog.log(
                "✗ Fail to open Output Directory! {}".format(str(e)))

    def ask_dir(self, init_dir, title) -> str:
        return tk.filedialog.askdirectory(
            parent=self,
            initialdir=init_dir,
            title=title,
            mustexist=True,
        )

    def ask_json_dir(self):
        last_dir = self.json_value
        if not last_dir:
            last_dir = DEFAULT_DIR
        ret_dir = self.ask_dir(last_dir, "Choose Production Directory")
        if not ret_dir:
            return
        self.json_value = ret_dir
        path_name, file_name = split(ret_dir)
        folder_name = basename(path_name)
        self.json_var.set(join(folder_name, file_name))
        self.sync_fg()

    def ask_output_dir(self):
        last_dir = self.output_value
        if not last_dir:
            last_dir = DEFAULT_DIR
        ret_dir = self.ask_dir(last_dir, "Choose Output Location")
        if not ret_dir:
            return
        self.output_value = ret_dir
        path_name, file_name = split(ret_dir)
        folder_name = basename(path_name)
        self.output_var.set(join(folder_name, file_name))
        self.sync_fg()

    def sync_fg(self):
        if self.json_value:
            self.choose_json_button.config(fg="black")
        else:
            self.choose_json_button.config(fg="red")
        if self.output_value:
            self.choose_output_button.config(fg="black")
        else:
            self.choose_output_button.config(fg="red")

    def add_items(self, width, height, draw_ost_template):
        self.main_frame = tk.Frame(self)
        self.main_frame.place(x=0, y=0, width=width, height=height)
        self.size_config.divide([
            [4, 1],
            [1, 1, 2],
            [1, 1, 2],
            [1, 1, 1],
            [1, 1, 2],
        ], internal=False)
        self.description_label = tk.Label(
            self.main_frame,
            text="Welcome to the Production Tool!\n"
                 "Choose your Production Directory and Output Location to start production.\n"
                 "\n"
                 "Every file in the Production Directory will be processed to "
                 "generate an OST report (if possible) and saved to the "
                 "Output Location with the default file name. "
                 "If the file name already exists in Output Location, "
                 "it won't be overwritten unless <Overwrite when necessary> "
                 "is checked.",
            font=("arial", 12),
            justify=tk.LEFT,
            anchor=tk.NW,
            wraplength=width - 2 * DEFAULT_SPACING,
        )
        self.json_var = tk.StringVar()
        self.choose_json_button = tk.Button(
            self.main_frame, text="Production Directory",
            command=self.ask_json_dir, anchor=tk.W)
        self.choose_json_label = tk.Label(
            self.main_frame, textvariable=self.json_var, anchor=tk.W)
        self.output_var = tk.StringVar()
        self.choose_output_button = tk.Button(
            self.main_frame, text="Output Location",
            command=self.ask_output_dir, anchor=tk.W)
        self.choose_output_label = tk.Label(
            self.main_frame, textvariable=self.output_var, anchor=tk.W)
        self.draw_template_var = tk.BooleanVar()
        self.draw_template_var.set(draw_ost_template)
        self.draw_ost_template_check = tk.Checkbutton(
            master=self.main_frame, text="Draw OST Template when output",
            onvalue=True, offvalue=False, variable=self.draw_template_var,
            anchor=tk.W)
        self.overwrite_output_var = tk.BooleanVar()
        self.overwrite_output_var.set(False)
        self.overwrite_output = tk.Checkbutton(
            master=self.main_frame,
            text="Overwrite Output files when necessary",
            onvalue=True, offvalue=False, variable=self.overwrite_output_var,
            anchor=tk.W)
        self.start_button = tk.Button(
            self.main_frame, text="Start Production",
            command=self.start_production)
        self.cancel_button = tk.Button(
            self.main_frame, text="Cancel",
            command=self.cancel)
        self.size_config.place([
            [self.description_label],
            [self.choose_json_button, self.choose_json_label],
            [self.choose_output_button, self.choose_output_label],
            [self.draw_ost_template_check, self.overwrite_output],
            [self.cancel_button, self.start_button],
        ])
        self.sync_fg()
