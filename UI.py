import os
import re
import tkinter as tk
import tkinter.messagebox
from tkinter import filedialog

from PIL import Image, ImageTk

from Launcher import *


# constant
cccl_path = "default_cccl.json"
setting_path = "setting.json"
tfont = "times-new-roman.ttf"
mccanny_logo = "mccanny_logo.ico"
ost_sample = "ost_sample.png"

# "course_code": ["course_title", "course_level", "credit", "compulsory"]
default_common_course_code_library = { }
default_setting = {
	"smart_fill": True,
	"train": True
}

try:
	common_course_code_library = from_json(cccl_path)
except Exception as exp:
	print("No common course code library found, restoring from default..., Error: {}".format(str(exp)))
	common_course_code_library = default_common_course_code_library

try:
	setting = from_json(setting_path)
except Exception as exp:
	print("No setting found, restoring from default..., Error: {}".format(str(exp)))
	setting = default_setting


def finalize():
	to_json(cccl_path, common_course_code_library)
	to_json(setting_path, setting)


class Main:
	def __init__(self, title="OST Entry System", size=(800, 672)):
		width, height = size
		self.root = tk.Tk()
		self.root.minsize(width, height)
		screen_width = self.root.winfo_screenwidth()
		screen_height = self.root.winfo_screenheight()
		x, y = (screen_width - width) // 2, (screen_height - height) // 2
		self.root.geometry("+{}+{}".format(x, y))
		self.size = size
		self.root.title(title)
		self.root.resizable(0, 0)
		self.root.iconbitmap(mccanny_logo)
		self.root.protocol("WM_DELETE_WINDOW", self.on_exit)
		self.infoFrame = None
	
	
	def add_info_frame(self):
		self.infoFrame = InfoFrame(self.root, self.size)
		self.infoFrame.pack(side=tk.TOP)
	
	
	def on_exit(self):
		res = tk.messagebox.askyesno(default=tk.messagebox.YES, parent=self.root, title="Save", message="Do you want to save before exit?")
		if res:
			self.infoFrame.save_action()
		self.root.destroy()
	
	
	def run(self):
		self.add_info_frame()
		self.infoFrame.set_ost(Data.default_ost)
		self.root.mainloop()


class AdjustmentWindow(tk.Toplevel):
	def __init__(self, master, info_frame, x_offset, y_offset, font_size, spacing, size=(3300 // 4, 2550 // 4 + 200)):
		width, height = size
		super().__init__(master, width=width, height=height)
		self.wm_title("Adjustment")
		self.info_frame = info_frame
		self.resizable(0, 0)
		self.ost_sample = Image.open(ost_sample)
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
		self.bind('<Escape>', lambda e: self.destroy())
		self.hide()
	
	
	def add_items(self, width):
		frame = tk.Frame(self)
		frame.pack(side="top", fill="both", expand=True)
		
		self.canvas = tk.Canvas(frame, bg="white", cursor="dot", relief="groove", width=width, height=2550 // 4)
		self.x_offset = ScalePair(frame, "x offset", from_=-1650, to=1650, command=self.x_offset_action, size=(width, 40, width / 10))
		self.y_offset = ScalePair(frame, "y offset", from_=-1275, to=1275, command=self.y_offset_action, size=(width, 40, width / 10))
		self.font_size = ScalePair(frame, "font size", from_=0, to=100, command=self.font_size_action, size=(width, 40, width / 10))
		self.spacing = ScalePair(frame, "spacing", from_=0, to=200, command=self.spacing_action, size=(width, 40, width / 10))
		
		sub_frame = tk.Frame(frame, width=width, height=40)
		cancel = tk.Button(sub_frame, text="Cancel", command=self.cancel)
		confirm = tk.Button(sub_frame, text="Confirm", command=self.confirm, bg="#CC0066", fg="white")
		cancel.place(x=10, y=10, width=(width - 30) / 3 * 1, height=23)
		confirm.place(x=20 + (width - 30) / 3 * 1, y=10, width=(width - 30) / 3 * 2, height=23)
		
		self.x_offset.set_info(self.x_offset_val)
		self.y_offset.set_info(self.y_offset_val)
		self.font_size.set_info(self.font_size_val)
		self.spacing.set_info(self.spacing_val)
		
		self.canvas.pack(side="top")
		self.x_offset.pack(side="top")
		self.y_offset.pack(side="top")
		self.font_size.pack(side="top")
		self.spacing.pack(side="top")
		sub_frame.pack(side="bottom", fill="both", expand=True)
	
	
	def x_offset_action(self, val):
		self.update_image()
		pass
	
	
	def y_offset_action(self, val):
		self.update_image()
		pass
	
	
	def font_size_action(self, val):
		self.update_image()
		pass
	
	
	def spacing_action(self, val):
		self.update_image()
		pass
	
	
	def cancel(self):
		self.canceled = True
		self.hide()
		self.x_offset.set_info(self.x_offset_val)
		self.y_offset.set_info(self.y_offset_val)
		self.font_size.set_info(self.font_size_val)
		self.spacing.set_info(self.spacing_val)
		self.ost = None
		
		self.info_frame.status_bar.set_info("Adjustment Canceled!")
	
	
	def confirm(self):
		self.canceled = False
		self.hide()
		self.x_offset_val = self.x_offset.get_info()
		self.y_offset_val = self.y_offset.get_info()
		self.font_size_val = self.font_size.get_info()
		self.spacing_val = self.spacing.get_info()
		Drawer.coordinates["Offset"] = (self.x_offset_val, self.y_offset_val)
		self.ost = None
		
		self.info_frame.status_bar.set_info("Adjustment Confirmed!")
	
	
	def hide(self):
		self.wm_withdraw()
		self.grab_release()
	
	
	def show(self, ost):
		self.ost = ost
		self.update()
		self.deiconify()
		self.grab_set()
		self.update_image()
	
	
	def update_image(self):
		x_off, y_off = self.x_offset.get_info(), self.y_offset.get_info()
		font_size, spacing = self.font_size.get_info(), self.spacing.get_info()
		self.ost.set_font_size(font_size)
		self.ost.set_spacing(spacing)
		img, _ = Drawer.draw(self.ost, offset=(x_off, y_off))
		img = img[0][0]
		image = self.ost_sample.copy()
		image.paste(img, (0, 0), img)
		self.image = ImageTk.PhotoImage(image=image.resize((3300 // 4, 2550 // 4), Image.ANTIALIAS))
		self.canvas.delete("all")
		# self.canvas.create_rectangle((0, 0, 3300 // 5, 2550 // 5), fill="white")
		self.canvas.create_image(0, 0, anchor="nw", image=self.image)
	
	
	def set_x_offset(self, val):
		self.x_offset_val = val
		self.x_offset.set_info(val)
	
	
	def set_y_offset(self, val):
		self.y_offset_val = val
		self.y_offset.set_info(val)
	
	
	def set_font_size(self, val):
		self.font_size_val = val
		self.font_size.set_info(val)
	
	
	def set_spacing(self, val):
		self.spacing_val = val
		self.spacing.set_info(val)


class ScalePair(tk.Frame):
	def __init__(self, master, text, from_, to, command, size):
		width, height, label_width = size
		super().__init__(master, width=width, height=height)
		self.scale = None
		self.add_item(width, height, label_width, text, from_, to, command)
	
	
	def add_item(self, width, height, label_width, text, from_, to, command):
		label = tk.Label(self, text=text)
		self.scale = tk.Scale(self, from_=from_, to=to, orient=tk.HORIZONTAL, repeatinterval=200, command=command, length=width - label_width - 10)
		label.place(x=0, y=0, width=label_width, height=height)
		self.scale.place(x=label_width, y=0)
	
	
	def set_info(self, value):
		self.scale.set(value)
	
	
	def get_info(self):
		return self.scale.get()


class InfoFrame(tk.Frame):
	"""
	each info frame represents an ost_info object, it contains all ost info
	"""
	
	
	def __init__(self, master, size):
		super().__init__(master, width=size[0], height=size[1])
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
		self.personal_info_panel = PersonalInfoPanel(self, size=(availWidth, 79))
		self.course_panel = CoursePanel(self, size=(availWidth, 386))  # 353
		self.other_info_panel = OtherInfoPanel(self, size=(availWidth, 79))
		self.utility_panel = UtilityPanel(self, size=(availWidth, 29))
		self.status_bar = StatusBar(self, message="Welcome to McCanny OST Entry system!", size=(self.size[0], 20))
		self.tk_frame.config(menu=self.menubar)
		self.common_info_panel.pack()
		self.personal_info_panel.pack()
		self.course_panel.pack()
		self.other_info_panel.pack()
		self.utility_panel.pack()
		self.status_bar.pack(side=tk.BOTTOM)
		x_offset, y_offset = Drawer.coordinates["Offset"]
		font_size, spacing = Data.default_ost.course_font_size(), Data.default_ost.course_spacing()
		self.adjustment = AdjustmentWindow(self.tk_frame, self, x_offset=x_offset, y_offset=y_offset, font_size=font_size, spacing=spacing)
	
	
	def set_ost(self, ost):
		data = ost.to_data()
		course = data["course_list"]
		self.common_info_panel.set_info(data)
		self.personal_info_panel.set_info(data)
		self.course_panel.set_info(course, sort=False)
		self.other_info_panel.set_info(data)
		self.utility_panel.set_info(data)
		self.adjustment.set_font_size(data["course_font_size"])
		self.adjustment.set_spacing(data["course_spacing"])
	
	
	def get_ost(self):
		data = { }
		self.common_info_panel.get_info(data)
		self.personal_info_panel.get_info(data)
		self.other_info_panel.get_info(data)
		self.utility_panel.get_info(data)
		course_list = self.course_panel.get_info()
		data["course_list"] = course_list
		data["course_font_size"] = self.adjustment.font_size_val
		data["course_spacing"] = self.adjustment.spacing_val
		return Data.OST_info.from_data(data)
	
	
	def generate_action(self):
		ost = self.get_ost()
		imgs, dir = Drawer.draw(ost, offset=Drawer.coordinates["Offset"])
		if len(imgs) == 1:
			img, name = imgs[0]
			filename = tk.filedialog.asksaveasfilename(parent=self, defaultextension=".png", initialdir="/", initialfile=name, title="Save OST", filetypes=(("PNG files", "*.png"), ("all files", "*.*")))
			if filename == "":
				return
			try:
				img.save(filename)
			except Exception as exp:
				tk.messagebox.showerror(parent=self.tk_frame, title="Error", message="Error on generate!\nError: {}".format(str(exp)))
				self.status_bar.set_info("Error saving file! Error:{}".format(str(exp)))
				return
			self.status_bar.set_info("OST generated at {}!".format(filename))
		else:
			directory = tk.filedialog.askdirectory(parent=self, initialdir="/", title="Save OSTs")
			if directory == "":
				return
			directory += "/" + dir
			try:
				os.mkdir(directory)
			except Exception as exp:
				print("Folder exsisted, Error:{}".format(str(exp)))
			for pair in imgs:
				img, name = pair
				filename = directory + "/" + name
				try:
					img.save(filename)
				except Exception as exp:
					tk.messagebox.showerror(parent=self.tk_frame, title="Error", message="Error on generate!\nError: {}".format(str(exp)))
					self.status_bar.set_info("Error saving file! Error:{}".format(str(exp)))
					return
			self.status_bar.set_info("OST generated at {}!".format(directory))
	
	
	def reset_action(self, ask=True):
		# pop up here
		if ask:
			res = tk.messagebox.askyesno(default=tk.messagebox.NO, parent=self.tk_frame, title="Warning", message="Are you sure to reset?", icon=tk.messagebox.WARNING)
		else:
			res = True
		if res:
			self.set_ost(Data.default_ost)
			self.status_bar.set_info("Reset Successful!")
	
	
	def new_draft_action(self):
		# save the current draft
		res = tk.messagebox.askyesno(default=tk.messagebox.YES, title="Save", message="Do you want to save the current draft?")
		if res:
			self.save_action()
		# new all data
		self.reset_action(ask=False)
		self.save_path = None
		self.status_bar.set_info("New draft created!")
	
	
	def save_action(self):
		if self.save_path is None:
			self.save_as_action()
			return
		self.get_ost().to_json(self.save_path)
		self.status_bar.set_info("Draft saved on {}!".format(self.save_path))
	
	
	def save_as_action(self):
		path = tk.filedialog.asksaveasfilename(parent=self, defaultextension=".json", initialdir="/", title="Save as", filetypes=(("JSON files", "*.json"), ("all files", "*.*")))
		if path == "":
			return
		self.save_path = path
		self.save_action()
	
	
	def open_action(self):
		res = tk.messagebox.askyesno(default=tk.messagebox.YES, parent=self.tk_frame, title="Save", message="Do you want to save the current draft?")
		if res:
			self.save_action()
		path = tk.filedialog.askopenfilename(parent=self, defaultextension=".json", initialdir="/", title="Open", filetypes=(("JSON files", "*.json"), ("all files", "*.*")))
		if path == "":
			return
		self.save_path = path
		ost = Data.OST_info.from_json(path)
		self.set_ost(ost)
		self.status_bar.set_info("File opened!")
	
	
	def about_action(self):
		tk.messagebox.showinfo(parent=self.tk_frame, title="About", message="This software is developed and licenced by McCanny Secondary School.\nVersion: 1.0-BETA")
	
	
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
		self.smart_fill = tk.BooleanVar(value=setting["smart_fill"])
		self.train = tk.BooleanVar(value=setting["train"])
		self.add_items()
	
	
	def add_items(self):
		self.file_menu = tk.Menu(self, tearoff=0)
		self.file_menu.add_command(label="New", command=self.info_panel.new_draft_action)
		self.file_menu.add_command(label="Open", command=self.info_panel.open_action)
		self.file_menu.add_separator()
		self.file_menu.add_command(label="Save", command=self.info_panel.save_action)
		self.file_menu.add_command(label="Save as...", command=self.info_panel.save_as_action)
		self.file_menu.add_separator()
		self.file_menu.add_command(label="Reset", command=self.info_panel.reset_action)
		self.add_cascade(label="File", menu=self.file_menu)
		
		self.setting = tk.Menu(self, tearoff=0)
		self.setting.add_command(label="Adjust...", command=self.info_panel.adjust_action)
		self.setting.add_separator()
		self.setting.add_checkbutton(label="Smart fill", variable=self.smart_fill, command=self.toggle_smart_fill)
		self.setting.add_checkbutton(label="Train", variable=self.train, command=self.toggle_train)
		self.add_cascade(label="Setting", menu=self.setting)
		
		self.tools = tk.Menu(self, tearoff=0)
		self.tools.add_command(label="OST Mass Production Tool")
		self.add_cascade(label="Tools", menu=self.tools)
		
		self.help = tk.Menu(self, tearoff=0)
		self.help.add_command(label="About", command=self.info_panel.about_action)
		self.add_cascade(label="Help", menu=self.help)
	
	
	def toggle_smart_fill(self):
		smart_fill = self.smart_fill.get()
		setting["smart_fill"] = smart_fill
		self.info_panel.status_bar.set_info("Smart fill has been set to {}!".format("ON" if smart_fill else "OFF"))
	
	
	def toggle_train(self):
		train = self.train.get()
		setting["train"] = train
		self.info_panel.status_bar.set_info("Train has been set to {}!".format("ON" if train else "OFF"))


class StatusBar(tk.Frame):
	def __init__(self, master, message, size):
		width, height = size
		super().__init__(master, width=width, height=height)
		self.status_bar = None
		self.logo = None
		self.add_items(message, width, height)
	
	
	def add_items(self, message, width, height):
		self.status_bar = tk.Label(self, text=message, relief=tk.SUNKEN, anchor=tk.W)
		self.status_bar.place(x=0, y=0, width=width, height=height)
	
	
	def set_info(self, message):
		self.status_bar.config(text=message)


class UtilityPanel(tk.Frame):
	def __init__(self, master, size):
		width, height = size
		super().__init__(master, width=width, height=height)
		self.master = master
		self.ost_date_of_issue = None
		self.new = None
		self.generate = None
		self.save = None
		self.adjust = None
		self.add_items(width, height)
	
	
	def add_items(self, width, height):
		unit_width, unit_height = (width - 3 * 2) / 8, height - 6
		self.ost_date_of_issue = DatePair(self, "Date of Issue", ("", "", ""), (unit_height, unit_width * 2 / 5 * 2, unit_width * 2, 10))
		self.new = tk.Button(self, text="New", command=self.master.new_draft_action)
		self.save = tk.Button(self, text="Save", command=self.master.save_action)
		self.adjust = tk.Button(self, text="Adjust...", command=self.master.adjust_action, fg="#CC0066")
		self.generate = tk.Button(self, text="Generate!", command=self.master.generate_action, bg="#CC0066", fg="white")
		
		self.ost_date_of_issue.place(x=3, y=3)
		self.new.place(x=width - (unit_width - 3) * 4 - 20, y=3, width=unit_width, height=unit_height)
		self.save.place(x=width - (unit_width - 3) * 3 - 15, y=3, width=unit_width, height=unit_height)
		self.adjust.place(x=width - (unit_width - 3) * 2 - 10, y=3, width=unit_width, height=unit_height)
		self.generate.place(x=width - unit_width - 2, y=3, width=unit_width, height=unit_height)
	
	
	def set_info(self, data):
		date_of_issue = data["OST_date_of_issue"]
		self.ost_date_of_issue.set_info(date_of_issue)
	
	
	def get_info(self, data):
		date_of_issue = self.ost_date_of_issue.get_info()
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
		                                  size_config=(unit_height, long_width_unit * 2 - 5, long_width_unit * 3))
		# add number of DSB height 310
		self.number_of_DSB = LabelEntryPair(self,
		                                    label_text="Number Of DSB",
		                                    entry_placeholder="",
		                                    size_config=(unit_height, short_width_unit * 2, short_width_unit * 3))
		# add name of school width 465
		self.name_of_school = LabelEntryPair(self,
		                                     label_text="Name Of School",
		                                     entry_placeholder="",
		                                     size_config=(unit_height, long_width_unit * 2 - 5, long_width_unit * 3))
		# add number of school height 310
		self.number_of_school = LabelEntryPair(self,
		                                       label_text="Number Of School",
		                                       entry_placeholder="",
		                                       size_config=(unit_height, short_width_unit * 2, short_width_unit * 3))
		self.name_of_DSB.place(x=5, y=0)
		self.number_of_DSB.place(x=5 + long_width_unit * 5, y=0)
		self.name_of_school.place(x=5, y=unit_height + 5)
		self.number_of_school.place(x=5 + long_width_unit * 5, y=unit_height + 5)
	
	
	def set_info(self, data):
		name_of_DSB = data["name_of_district_school_board"]
		number_of_DSB = data["district_school_board_number"]
		name_of_school = data["name_of_school"]
		number_of_school = data["school_number"]
		self.name_of_DSB.set_info(name_of_DSB)
		self.number_of_DSB.set_info(number_of_DSB)
		self.name_of_school.set_info(name_of_school)
		self.number_of_school.set_info(number_of_school)
	
	
	def get_info(self, data):
		name_of_DSB = self.name_of_DSB.get_info()
		number_of_DSB = self.number_of_DSB.get_info()
		name_of_school = self.name_of_school.get_info()
		number_of_school = self.number_of_school.get_info()
		data["name_of_district_school_board"] = name_of_DSB
		data["district_school_board_number"] = number_of_DSB
		data["name_of_school"] = name_of_school
		data["school_number"] = number_of_school


class PersonalInfoPanel(tk.LabelFrame):
	def __init__(self, master, size):
		width, height = size
		super().__init__(master, text="Personal Info", width=width, height=height)
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
		                              size_config=(unit_height, name_width / 10 * 3, name_width / 10 * 7))
		self.given_name = LabelEntryPair(self,
		                                 label_text="Given Name",
		                                 entry_placeholder="",
		                                 size_config=(unit_height, name_width / 10 * 4, name_width / 10 * 6))
		self.gender = LabelEntryPair(self,
		                             label_text="Gender",
		                             entry_placeholder="",
		                             size_config=(unit_height, gender_width / 2, gender_width / 2))
		self.date_of_birth = DatePair(self,
		                              text="Date of Birth",
		                              date=(0, 0, 0),
		                              size_config=(unit_height, date_width / 3, date_width / 3 * 2 - 5, 10))
		self.OEN = LabelEntryPair(self,
		                          label_text="OEN/MIN",
		                          entry_placeholder="",
		                          size_config=(unit_height, date_width / 10 * 3 - 15, date_width / 10 * 7 + 15))
		self.student_number = LabelEntryPair(self,
		                                     label_text="Student Number",
		                                     entry_placeholder="",
		                                     size_config=(unit_height, date_width / 10 * 4, date_width / 10 * 6 + 5))
		self.date_of_entry = DatePair(self,
		                              text="Date of Entry",
		                              date=(0, 0, 0),
		                              size_config=(unit_height, date_width / 3, date_width / 3 * 2 - 5, 10))
		self.surname.place(x=5, y=0)
		self.given_name.place(x=5 * 2 + name_width, y=0)
		self.gender.place(x=5 * 3 + name_width * 2, y=0)
		self.date_of_birth.place(x=5 * 4 + name_width * 2 + gender_width, y=0)
		self.OEN.place(x=5, y=unit_height + 5)
		self.student_number.place(x=5 * 2 + date_width, y=unit_height + 5)
		self.date_of_entry.place(x=5 * 4 + date_width * 2, y=unit_height + 5)
	
	
	def set_info(self, data):
		surename, given_name = data["name"]
		gender = data["gender"]
		date_of_birth = data["date_of_birth"]
		OEN = data["OEN"]
		student_number = data["student_number"]
		date_of_entry = data["date_of_entry"]
		self.surname.set_info(surename)
		self.given_name.set_info(given_name)
		self.gender.set_info(gender)
		self.date_of_birth.set_info(date_of_birth)
		self.OEN.set_info(OEN)
		self.student_number.set_info(student_number)
		self.date_of_entry.set_info(date_of_entry)
	
	
	def get_info(self, data):
		surename = self.surname.get_info()
		given_name = self.given_name.get_info()
		gender = self.gender.get_info()
		date_of_birth = self.date_of_birth.get_info()
		OEN = self.OEN.get_info()
		student_number = self.student_number.get_info()
		date_of_entry = self.date_of_entry.get_info()
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
		self.add_items(width, height)
	
	
	def add_course(self):
		c = CoursePair(self.frame, self.master, (self.avail_width - 5, 24), self.delete_action, self.count_credit, self.count_compulsory, self.count_courses)
		self.courses.append(c)
		self.index += 1
		c.grid(row=self.index, column=0, ipadx=0, ipady=2)
		return c
	
	
	def delete_action(self, event):
		c = event.widget.master
		c.destroy()
		self.index -= 1
		self.courses.remove(c)
		self.count_credit()
		self.count_compulsory()
		self.count_courses()
	
	
	def count_courses(self):
		total_course = sum([1 for course in self.courses if course.is_course()])
		self.add.config(text="+ ADD Course{}".format("" if self.index == 0 else " ({})".format(total_course)))
	
	
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
	
	
	def train(self, event):
		if not setting["train"]:
			return
		train_able = [course.train_data() for course in self.courses]
		train_able = [data for data in train_able if data[0] != "" and data[1] != "" and data[2] != "" and data[3] != ""]
		for data in train_able:
			code, title, level, credit, compulsory = data
			common_course_code_library[code.upper()] = (title, level, credit, compulsory)
		self.master.status_bar.set_info("{} Data Trained!".format(len(train_able)))
	
	
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
		except Exception as exp:
			tk.messagebox.showerror(parent=self, title="Sort Error", message="An Error has occurs when sorting. Please try again!\nThis is usually caused by incorrect format of the date.\nThe allowed format includes:\n->2000\\10\n->2000/10\n->2000-10\n->2000.10\n->2000 10\nError: {}".format(str(exp)))
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
		self.add = tk.Button(self, text="+ ADD Course", command=self.add_course, bg="#669966", fg="white")
		self.date_label = tk.Label(self, text="Date", anchor=tk.S)
		self.grade_label = tk.Label(self, text="Grad.", anchor=tk.S)
		self.title_label = tk.Label(self, text="Course Title", anchor=tk.S)
		self.code_label = tk.Label(self, text="Code", anchor=tk.S)
		self.percentage_label = tk.Label(self, text="Perc.", anchor=tk.S)
		self.credit_label = tk.Label(self, text="Cred.", anchor=tk.S)
		self.compulsory_label = tk.Label(self, text="Comp.", anchor=tk.S)
		self.note_label = tk.Label(self, text="Note", anchor=tk.S)
		self.scrollBar = tk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
		self.canvas.configure(yscrollcommand=self.scrollBar.set)
		self.sort = tk.Button(self, text="Sort", command=self.sort_course, bg="#669966", fg="white")
		self.credit_summary = tk.Label(self, text="0", anchor=tk.N)
		self.compulsory_summary = tk.Label(self, text="0", anchor=tk.N)
		avail_width = width - 20 - 10 - 5
		avail_height = height - 20 - 24 - 24 - 24 - 9 - 5
		unit_avail_width = (avail_width - 5 - 5 * 8 - 24) / 20
		# 10 * (24 + 2) + 20 + 24 + 24 + 5
		self.add.place(x=5, y=0, width=width - 15, height=24)
		
		self.date_label.place(x=5 + 2 + 24 + unit_avail_width * 0 + 5 * 1, y=24, width=unit_avail_width * 2, height=24)
		self.grade_label.place(x=5 + 2 + 24 + unit_avail_width * 2 + 5 * 2, y=24, width=unit_avail_width * 1, height=24)
		self.title_label.place(x=5 + 2 + 24 + unit_avail_width * 3 + 5 * 3, y=24, width=unit_avail_width * 10, height=24)
		self.code_label.place(x=5 + 2 + 24 + unit_avail_width * 13 + 5 * 4, y=24, width=unit_avail_width * 2, height=24)
		self.percentage_label.place(x=5 + 2 + 24 + unit_avail_width * 15 + 5 * 5, y=24, width=unit_avail_width * 1, height=24)
		self.credit_label.place(x=5 + 2 + 24 + unit_avail_width * 16 + 5 * 6, y=24, width=unit_avail_width * 1, height=24)
		self.compulsory_label.place(x=5 + 2 + 24 + unit_avail_width * 17 + 5 * 7, y=24, width=unit_avail_width * 1, height=24)
		self.note_label.place(x=5 + 2 + 24 + unit_avail_width * 18 + 5 * 8, y=24, width=unit_avail_width * 2, height=24)
		
		self.canvas.place(x=5, y=24 + 24, width=avail_width, height=avail_height)
		self.scrollBar.place(x=width - 20 - 5 - 5, y=24 + 24, width=20, height=avail_height)
		self.canvas.create_window((0, 0), window=self.frame, anchor="nw")
		
		self.sort.place(x=5 + 2 + 24 + unit_avail_width * 0 + 5 * 1, y=24 + avail_height + 5 + 24, width=unit_avail_width * 2, height=24)
		self.credit_summary.place(x=5 + 2 + 24 + unit_avail_width * 16 + 5 * 6, y=24 + avail_height + 5 + 24, width=unit_avail_width * 1, height=24)
		self.compulsory_summary.place(x=5 + 2 + 24 + unit_avail_width * 17 + 5 * 7, y=24 + avail_height + 5 + 24, width=unit_avail_width * 1, height=24)
		
		
		def conf(event):
			self.canvas.config(scrollregion=self.canvas.bbox("all"), width=avail_width, height=avail_height)
		
		
		self.frame.bind("<Configure>", conf)
		self.avail_width = avail_width
		self.bind("<FocusOut>", self.train)
	
	
	def set_info(self, courses, sort=True):
		for c in self.courses:
			c.grid_remove()
		self.courses.clear()
		self.index = 0
		for data in courses:
			c = self.add_course()
			c.set_info(data)
		if sort:
			self.sort_course()
		self.count_courses()
		self.count_compulsory()
		self.count_credit()
	
	
	def get_info(self):
		course = [c.get_info() for c in self.courses]
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
		self.community_involvement = tk.Checkbutton(self, text="Community Involvement", variable=self.community_involvement_var)
		self.literacy_requirement_var = tk.BooleanVar()
		self.literacy_requirement = tk.Checkbutton(self, text="Provincial Literacy Requirement", variable=self.literacy_requirement_var)
		self.specialized_program = LabelEntryPair(self, "Specialized Program", "", (unit_height, (unit_width * 5) / 10 * 3, (unit_width * 5) / 10 * 7))
		self.diploma_or_certificate = LabelEntryPair(self, "Diploma or Certificate", "", (unit_height, (unit_width * 5) / 3 * 1, (unit_width * 5) / 3 * 2))
		self.diploma_or_certificate_date_of_issue = SimpleDatePair(self, ("2000", "1"), (unit_height, unit_width, 5))
		self.authorization = LabelEntryPair(self, "Authorization", "", (unit_height, (unit_width * 4) / 4 * 1, (unit_width * 4) / 4 * 3))
		self.community_involvement.grid(row=0, column=0, rowspan=1, columnspan=2, sticky=tk.NW)
		self.literacy_requirement.grid(row=0, column=2, rowspan=1, columnspan=3, sticky=tk.NW)
		self.specialized_program.grid(row=0, column=5, rowspan=1, columnspan=5, sticky=tk.NW, ipadx=3, ipady=3)
		self.diploma_or_certificate.grid(row=1, column=0, rowspan=1, columnspan=5, sticky=tk.NW)
		self.diploma_or_certificate_date_of_issue.grid(row=1, column=5, rowspan=1, columnspan=1, sticky=tk.NW)
		self.authorization.grid(row=1, column=6, rowspan=1, columnspan=4, sticky=tk.NW, ipadx=3, ipady=3)
	
	
	def set_info(self, data):
		community_involvement = data["community_involvement_flag"]
		literacy_requirement = data["provincial_secondary_school_literacy_requirement_flag"]
		specialized_program = data["specialized_program"]
		diploma_or_certificate = data["diploma_or_certificate"]
		diploma_or_certificate_date_of_issue = data["diploma_or_certificate_date_of_issue"]
		authorization = data["authorization"]
		self.community_involvement_var.set(community_involvement)
		self.literacy_requirement_var.set(literacy_requirement)
		self.specialized_program.set_info(specialized_program)
		self.diploma_or_certificate.set_info(diploma_or_certificate)
		self.diploma_or_certificate_date_of_issue.set_info(diploma_or_certificate_date_of_issue)
		self.authorization.set_info(authorization)
	
	
	def get_info(self, data):
		community_involvement = self.community_involvement_var.get()
		literacy_requirement = self.literacy_requirement_var.get()
		specialized_program = self.specialized_program.get_info()
		diploma_or_certificate = self.diploma_or_certificate.get_info()
		diploma_or_certificate_date_of_issue = self.diploma_or_certificate_date_of_issue.get_info()
		authorization = self.authorization.get_info()
		data["community_involvement_flag"] = community_involvement
		data["provincial_secondary_school_literacy_requirement_flag"] = literacy_requirement
		data["specialized_program"] = specialized_program
		data["diploma_or_certificate"] = diploma_or_certificate
		data["diploma_or_certificate_date_of_issue"] = diploma_or_certificate_date_of_issue
		data["authorization"] = authorization


class CoursePair(tk.Frame):
	def __init__(self, master, info_frame, size_config, button_action, count_credit, count_compulsory, count_course):
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
		self.info_frame = info_frame
		self.add_items(width, height, button_action, count_credit, count_compulsory, count_course)
	
	
	def add_items(self, width, height, button_action, count_credit, count_compulsory, count_course):
		def wrapper():
			self.smart_fill()
			count_course()
			count_compulsory()
			count_credit()
		
		
		unit_height = height
		unit_width = (width - 5 * 8 - height) / 20
		self.delete = tk.Button(master=self, text="X", bg="#CC0066", fg="white")
		self.delete.bind("<1>", button_action)
		self.date = tk.Entry(master=self, bd=2)
		self.grade = tk.Entry(master=self, bd=2)
		self.title = tk.Entry(master=self, bd=2)
		self.code = tk.Entry(master=self, bd=2, validate="focusout", validatecommand=wrapper)
		self.percentage = tk.Entry(master=self, bd=2)
		self.credit = tk.Entry(master=self, bd=2, validate="focusout", validatecommand=count_credit)
		self.compulsory = tk.Entry(master=self, bd=2, validate="focusout", validatecommand=count_compulsory)
		self.note = tk.Entry(master=self, bd=2)
		# self.date.insert(tk.END, date_text)
		# self.grade.insert(tk.END, grade_text)
		# self.title.insert(tk.END, title_text)
		# self.code.insert(tk.END, code_text)
		# self.percentage.insert(tk.END, percentage_text)
		# self.credit.insert(tk.END, credit_text)
		# self.compulsory.insert(tk.END, compulsory_text)
		# self.note.insert(tk.END, note_text)
		self.delete.place(x=0, y=0, width=height, height=unit_height)
		self.date.place(x=unit_width * 0 + 5 * 1 + height, y=0, width=unit_width * 2, height=unit_height)
		self.grade.place(x=unit_width * 2 + 5 * 2 + height, y=0, width=unit_width * 1, height=unit_height)
		self.title.place(x=unit_width * 3 + 5 * 3 + height, y=0, width=unit_width * 10, height=unit_height)
		self.code.place(x=unit_width * 13 + 5 * 4 + height, y=0, width=unit_width * 2, height=unit_height)
		self.percentage.place(x=unit_width * 15 + 5 * 5 + height, y=0, width=unit_width * 1, height=unit_height)
		self.credit.place(x=unit_width * 16 + 5 * 6 + height, y=0, width=unit_width * 1, height=unit_height)
		self.compulsory.place(x=unit_width * 17 + 5 * 7 + height, y=0, width=unit_width * 1, height=unit_height)
		self.note.place(x=unit_width * 18 + 5 * 8 + height, y=0, width=unit_width * 2, height=unit_height)
	
	
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
		self.info_frame.status_bar.set_info("{} Smart filled!".format(code))
	
	
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
	
	
	def set_info(self, data):
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
	
	
	def get_info(self):
		date, level, title, code, percentage, credit, compulsory, note = self.date.get(), self.grade.get(), self.title.get(), self.code.get(), self.percentage.get(), self.credit.get(), self.compulsory.get(), self.note.get()
		return Data.Course(date=date, level=level, title=title, code=code, percentage=percentage, credit=credit, compulsory=compulsory, note=note)


class LabelEntryPair(tk.Frame):
	def __init__(self, master, label_text, entry_placeholder, size_config):
		# (height, label width, entry width)
		height, label_width, entry_width = size_config
		super().__init__(master, width=label_width + entry_width, height=height)
		self.label = None
		self.entry = None
		self.add_items(height, label_width, entry_width, label_text, entry_placeholder)
	
	
	def add_items(self, height, label_width, entry_width, label_text, entry_placeholder):
		self.label = tk.Label(master=self, text=label_text, anchor=tk.W)
		self.entry = tk.Entry(master=self, bd=2)
		self.entry.insert(tk.END, entry_placeholder)
		self.label.place(x=0, y=0, width=label_width, height=height)
		self.entry.place(x=label_width, y=0, width=entry_width, height=height)
	
	
	def set_info(self, value):
		set_entry_value(self.entry, value)
	
	
	def get_info(self):
		return self.entry.get()


class DatePair(tk.Frame):
	def __init__(self, master, text, date, size_config, spacing_text="-"):
		# (height, label_width, unit_width, spacing)
		height, label_width, date_width, spacing = size_config
		unit_width = (date_width - 2 * spacing) / 3
		year, month, day = date
		super().__init__(master, width=unit_width * 3 + spacing * 2 + label_width, height=height)
		self.label = None
		self.entry_year = None
		self.entry_month = None
		self.entry_day = None
		self.add_items(height, text, label_width, unit_width, spacing, spacing_text, year, month, day)
	
	
	def add_items(self, height, text, label_width, unit_width, spacing, spacing_text, year, month, day):
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
		spacing_1.place(x=label_width + unit_width, y=0, width=spacing, height=height)
		entry_month.place(x=label_width + unit_width + spacing, y=0, width=unit_width, height=height)
		spacing_2.place(x=label_width + unit_width * 2 + spacing, y=0, width=spacing, height=height)
		entry_day.place(x=label_width + unit_width * 2 + spacing * 2, y=0, width=unit_width, height=height)
	
	
	def set_info(self, date):
		year, month, day = date
		set_entry_value(self.entry_year, year)
		set_entry_value(self.entry_month, month)
		set_entry_value(self.entry_day, day)
	
	
	def get_info(self):
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
		entry_month.place(x=unit_width + spacing, y=0, width=unit_width, height=height)
	
	
	def set_info(self, date):
		year, month = date
		set_entry_value(self.entry_year, year)
		set_entry_value(self.entry_month, month)
	
	
	def get_info(self):
		year, month = self.entry_year.get(), self.entry_month.get()
		return [year, month]


def set_entry_value(entry_target, value):
	entry_target.delete(0, tk.END)
	entry_target.insert(0, value)
