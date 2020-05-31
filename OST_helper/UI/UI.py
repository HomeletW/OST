import tkinter as tk
import tkinter.messagebox
from os.path import dirname, exists
from tempfile import TemporaryDirectory
from tkinter import filedialog

import fpdf

from Launcher import PATCH
from OST_helper.UI.dialogs import AdjustmentWindow, EMPTY_TRACKER, \
    ThreadMonitorDialog, Tracker
from OST_helper.UI.fields import *
from OST_helper.UI.tk_objects import TopDownSizeConfig
from OST_helper.data_handler import Data, Drawer
from OST_helper.data_handler.Data import OST_info
from OST_helper.data_handler.Drawer import get_total_size_in_mm
from OST_helper.parameter import *


class Application:
    def __init__(self, title="OST Helper"):
        width, height = 800, 700
        self.size_config = TopDownSizeConfig(width=1100, height=850)
        self.root = tk.Tk()
        self.root.minsize(width, height)
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x, y = (screen_width - width) // 2, (screen_height - height) // 2
        self.root.geometry("+{}+{}".format(x, y))
        self.title = title
        self.update_title()
        self.root.resizable(0, 0)
        # self.root.iconbitmap(mccanny_logo)
        self.root.protocol("WM_DELETE_WINDOW", self.on_exit)
        self.infoFrame = None

    def add_info_frame(self):
        divided = self.size_config.divide([
            [1, 1],
        ], internal=True, spacing=0)
        self.infoFrame = InfoFrame(self, self.root, divided[0][0])
        self.infoFrame.pack(side=tk.TOP)

    def on_exit(self):
        self.infoFrame.ending_session()
        self.root.destroy()

    def run(self):
        self.add_info_frame()
        self.infoFrame.init_session(default=DEFAULT_OST_INFO)
        self.root.mainloop()

    def update_title(self, tit=None):
        self.root.title("{}{}".format(
            self.title, "" if not tit else " - {}".format(tit))
        )


class InfoFrame(tk.Frame):
    """
    each info frame represents an ost_info object, it contains all ost info
    """

    def __init__(self, app, master, size_config: TopDownSizeConfig):
        super().__init__(master, width=size_config.width,
                         height=size_config.height)
        self.app = app
        self.size_config = size_config
        self.tk_frame = master
        self.menubar = None
        self.personal_info_panel = None
        self.course_panel = None
        self.other_info_panel = None
        self.utility_panel = None
        self.status_bar = None
        self.save_path = None
        self.adjustment = None
        self.logger = logging.getLogger()
        self.add_panels()

    def add_panels(self):
        divided = self.size_config.divide([
            [4, 1],  # personal info
            [14, 1],  # course_panel
            [4, 1],  # other_info
            [1, 1],  # utility
            [1, 1],  # status bar
        ], internal=False)
        self.menubar = MenuBar(self.tk_frame, self)
        self.personal_info_panel = PersonalInfoPanel(
            self, size_config=divided[0][0])
        self.course_panel = CoursePanel(
            self, size_config=divided[1][0])
        self.other_info_panel = OtherInfoPanel(
            self, size_config=divided[2][0])
        self.utility_panel = UtilityPanel(
            self, size_config=divided[3][0])
        self.status_bar = StatusBar(
            self, message="Welcome to McCanny OST Entry system!",
            size_config=divided[4][0])
        self.tk_frame.config(menu=self.menubar)
        x_offset, y_offset = COORDINATES["Offset"]
        self.adjustment = AdjustmentWindow(
            self.tk_frame, self,
            x_offset=x_offset, y_offset=y_offset,
            font_size=DEFAULT_OST_INFO.course_font_size(),
            spacing=DEFAULT_OST_INFO.course_spacing()
        )
        self.size_config.place([
            [self.personal_info_panel],
            [self.course_panel],
            [self.other_info_panel],
            [self.utility_panel],
            [self.status_bar],
        ])

    def init_session(self, default):
        last_session = SETTING["last_session"]
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
        self.save_action(ask=True)
        if self.save_path is not None:
            SETTING["last_session"] = self.save_path

    def set_ost(self, ost):
        data = ost.to_data()
        course = data["course_list"]
        self.personal_info_panel.set(data)
        self.course_panel.set(course, sort=False)
        self.other_info_panel.set(data)
        self.utility_panel.set(data)
        self.adjustment.set_font_size(data["course_font_size"])
        self.adjustment.set_spacing(data["course_spacing"])

    def get_ost(self):
        data = {}
        self.personal_info_panel.get(data)
        self.other_info_panel.get(data)
        self.utility_panel.get(data)
        course_list = self.course_panel.get()
        data["course_list"] = course_list
        data["course_font_size"] = self.adjustment.font_size_val
        data["course_spacing"] = self.adjustment.spacing_val
        return Data.OST_info.from_data(data)

    def production(self, ost_file, pdf_dir, draw_ost_template,
                   overwrite_output):
        try:
            ost = OST_info.from_json(ost_file)
            file_name = ost.get_file_name()
            pdf_path = join(pdf_dir, file_name)
            if not overwrite_output and exists(pdf_path):
                return PRODUCTION_FILE_EXISTS
            self._generate_action(EMPTY_TRACKER, ost, pdf_path,
                                  draw_ost_template=draw_ost_template,
                                  print_=False)
            return PRODUCTION_SUCCESS
        except Exception:
            return PRODUCTION_FILE_NOT_RECOGNIZED

    def generate_action(self, print_=True):
        ost = self.get_ost()
        pdf_path = tk.filedialog.asksaveasfilename(
            parent=self.tk_frame,
            initialdir=SETTING["img_dir"],
            initialfile=ost.get_file_name(),
            defaultextension=".pdf",
            title="Save PDF",
            filetypes=[
                ("PDF 文件", ".pdf"),
                ("所有文件", "*.*")
            ]
        )
        if not pdf_path:
            return
        tmd = ThreadMonitorDialog(self, "Generate OST",
                                  self._generate_action,
                                  ost=ost,
                                  pdf_path=pdf_path,
                                  draw_ost_template=None,
                                  print_=print_)
        tmd.start()

    def _generate_action(self,
                         progress_dialog: Tracker,
                         ost,
                         pdf_path,
                         draw_ost_template=None,
                         print_=True) -> bool:
        # ask the directory for pdf file save
        progress_dialog.init(10 if print_ else 9)
        progress_dialog.tick("Drawing Images...")
        if draw_ost_template is None:
            draw_ost_template = SETTING["draw_ost_template"]
        images, _ = Drawer.draw(ost, draw_ost_template,
                                offset=COORDINATES["Offset"])
        progress_dialog.tick("Generating to : {}...".format(pdf_path))
        pdf_dir = dirname(pdf_path)
        SETTING["img_dir"] = pdf_dir
        # first save the file in to a folder in the destination location
        progress_dialog.tick("Creating temp folder...")
        with TemporaryDirectory(dir=pdf_dir) as temp_dir:
            progress_dialog.tick("Writing images...")
            # first write images to temp location
            img_dirs = []
            for img, name in images:
                image_path = join(temp_dir, name)
                try:
                    img.save(image_path, "png")
                except Exception as e:
                    progress_dialog.log(
                        "Error on generate!\nError: {}".format(str(e)))
                    progress_dialog.end(error=True)
                    return False
                img_dirs.append(image_path)
            progress_dialog.tick("Creating PDF files by images...")
            # now we get all the images we can output the pdf.
            mm_width, mm_height = get_total_size_in_mm()
            pdf = fpdf.FPDF(orientation="Landscape", unit="in",
                            format=(mm_height, mm_width))
            pdf.set_auto_page_break(False)
            for img_dir in img_dirs:
                pdf.add_page(orientation="Landscape")
                # x=0, y=0,
                pdf.image(img_dir, w=mm_width, h=mm_height, type="png")
            pdf.close()
            pdf.output(name=pdf_path)
            progress_dialog.tick("PDF file saved...")
        # now we move on to print
        if print_:
            progress_dialog.tick("Starting Print Service...")
            self.print_file(pdf_dir)
        progress_dialog.tick("Finished!")
        self.status_bar.set("OST generated at {}!".format(pdf_path))
        progress_dialog.end()
        return True

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
            self.set_ost(DEFAULT_OST_INFO)
            self.app.update_title("NEW DRAFT")
            self.status_bar.set("Reset Successful!")

    def new_draft_action(self):
        # save the current draft
        self.save_action(ask=True)
        # new all data
        self.reset_action(ask=False)
        self.save_path = None
        self.status_bar.set("New draft created!")

    def save_action(self, ost=None, ask=False):
        if ost is None:
            ost = self.get_ost()
        if self.save_path is None:
            if ask:
                res = tk.messagebox.askyesno(
                    parent=self.tk_frame,
                    default=tk.messagebox.YES, title="Save",
                    message="Do you want to save the current draft?")
            else:
                res = True
            if res:
                self.save_as_action(ost)
            return
        assert ost is not None, "OST shouldn't be None at this point"
        ost.to_json(self.save_path)
        self.app.update_title(ost.full_name())
        self.logger.info("Draft saved on {}!".format(self.save_path))
        self.status_bar.set("Draft saved on {}!".format(self.save_path))

    def save_as_action(self, ost=None):
        file_name = "" if ost is None else ost.get_file_name()
        path = tk.filedialog.asksaveasfilename(
            parent=self,
            initialdir=SETTING["json_dir"],
            title="Save as",
            initialfile=file_name,
            defaultextension=".json",
            filetypes=(
                ("JSON files", "*.json"),
                ("all files", "*.*")))
        if not path:
            return
        SETTING["json_dir"] = dirname(path)
        self.save_path = path
        self.save_action(ost)

    def open_action(self):
        self.save_action(ask=True)
        path = tk.filedialog.askopenfilename(
            parent=self,
            initialdir=SETTING["json_dir"], title="Open",
            filetypes=(
                ("JSON files", "*.json"),
                ("all files", "*.*")))
        if not path:
            return
        SETTING["json_dir"] = dirname(path)
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


if __name__ == '__main__':

    def test(event):
        print('keysym:', event.keysym)


    root = tk.Tk()

    root.bind('<Key>', test)

    root.mainloop()
