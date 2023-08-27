import tkinter as tk
import tkinter.messagebox
from os.path import dirname
from tkinter import filedialog

from Launcher import PATCH
from OST_helper.UI.dialogs import AdjustmentWindow, EMPTY_TRACKER, \
    ThreadMonitorDialog, Tracker
from OST_helper.UI.fields import *
from OST_helper.UI.tk_objects import TopDownSizeConfig
from OST_helper.data_handler import Data, Drawer
from OST_helper.data_handler.Data import OST_info
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
        self.root.iconbitmap(APP_LOGO)
        self.root.protocol("WM_DELETE_WINDOW", self.on_exit)
        self.infoFrame = None
        self.add_info_frame()

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
            self, message="Welcome to OST Entry system!",
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
        self.personal_info_panel.set(data)
        self.course_panel.set(data, sort=False)
        self.other_info_panel.set(data)
        self.utility_panel.set(data)
        self.adjustment.set_font_size(data["course_font_size"])
        self.adjustment.set_spacing(data["course_spacing"])

    def get_ost(self):
        data = {}
        self.personal_info_panel.get(data)
        self.other_info_panel.get(data)
        self.utility_panel.get(data)
        self.course_panel.get(data)
        data["course_font_size"] = self.adjustment.font_size_val
        data["course_spacing"] = self.adjustment.spacing_val
        return Data.OST_info.from_data(data)

    def production(self, ost_file, pdf_dir, 
                   draw_ost_template, 
                   draw_use_old_version_paper,
                   overwrite_output):
        try:
            ost = OST_info.from_json(ost_file)
            file_name = ost.get_file_name()
            pdf_path = join(pdf_dir, file_name)
            if not overwrite_output and exists(pdf_path):
                return PRODUCTION_FILE_EXISTS
            self._generate_action(EMPTY_TRACKER, ost, pdf_path,
                                  draw_ost_template=draw_ost_template,
                                  draw_use_old_version_paper=draw_use_old_version_paper,
                                  open_file=False)
            return PRODUCTION_SUCCESS
        except Exception:
            return PRODUCTION_FILE_NOT_RECOGNIZED

    def generate_action(self, open_file=True):
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
                                  self,
                                  self._generate_action,
                                  ost=ost,
                                  pdf_path=pdf_path,
                                  draw_ost_template=None,
                                  open_file=open_file)
        tmd.start()

    def _generate_action(self,
                         progress_dialog: Tracker,
                         ost,
                         pdf_path,
                         draw_ost_template=None,
                         draw_with_old_paper=None,
                         open_file=True) -> bool:
        # ask the directory for pdf file save
        progress_dialog.init(4)
        progress_dialog.tick("➜ Drawing OST")
        if draw_ost_template is None:
            draw_ost_template = SETTING["draw_ost_template"]
        if draw_with_old_paper is None:
            draw_with_old_paper = SETTING.get("draw_use_old_version_paper", True)
        images, _ = Drawer.draw(ost, 
                                draw_ost_template=draw_ost_template,
                                draw_with_old_paper=draw_with_old_paper,
                                offset=COORDINATES["Offset"])
        progress_dialog.tick("➜ Creating PDF file")
        pdf_dir = dirname(pdf_path)
        SETTING["img_dir"] = pdf_dir
        # first save the file in to a folder in the destination location
        # first write images to temp location
        imgs = [self.alpha_to_color(img) for img, _ in images]
        first_imgs = imgs[0]
        other_imgs = imgs[1:]
        try:
            first_imgs.save(
                pdf_path,
                format="pdf",
                save_all=True,
                append_images=other_imgs,
                author="OST Helper",
                subject="OST",
            )
        except Exception as e:
            progress_dialog.log("✗ Error on generate! {}".format(str(e)))
            progress_dialog.end(error=True)
            return False
        progress_dialog.tick("➜ PDF saved!")
        progress_dialog.end()
        progress_dialog.log("✔ PDF Saved to : {}".format(pdf_path))
        self.status_bar.set("PDF saved to : {}!".format(pdf_path))
        # now we move on to print
        if open_file:
            self.open_file(pdf_path, progress_dialog)
        return True

    @staticmethod
    def alpha_to_color(image):
        """Set all fully transparent pixels of an RGBA image to the specified color.
        This is a very simple solution that might leave over some ugly edges, due
        to semi-transparent areas. You should use alpha_composite_with color instead.

        Source: http://stackoverflow.com/a/9166671/284318

        Keyword Arguments:
        image -- PIL RGBA Image object
        color -- Tuple r, g, b (default 255, 255, 255)
        """
        background = Image.new("RGB", image.size, (255, 255, 255))
        background.paste(image, mask=image.split()[3])
        return background

    @staticmethod
    def open_file(pdf_path, progress_dialog):
        try:
            open_path(pdf_path)
            progress_dialog.log("✔ File opened!")
        except Exception as e:
            progress_dialog.log("✗ Fail to open file! {}".format(str(e)))

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
        # train the CCCL
        self.course_panel.train()

    def save_as_action(self, ost=None):
        if ost is None:
            ost = self.get_ost()
        file_name = ost.get_file_name(file_type=".json")
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
        tk.messagebox.showinfo(
            parent=self.tk_frame, title="About",
            message="OST Helper\n\n"
                    "Developed by HongCheng Wei (github.com/HomeletW)\n\n"
                    "Version : V{}\n\n"
                    "Copyright © HongCheng Wei".format(PATCH)
        )

    def adjust_action(self):
        self.adjustment.show(self.get_ost(), SETTING.get("draw_use_old_version_paper", True))


if __name__ == '__main__':

    def test(event):
        print('keysym:', event.keysym)


    root = tk.Tk()

    root.bind('<Key>', test)

    root.mainloop()
