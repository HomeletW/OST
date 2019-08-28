import re
import tkinter as tk
import tkinter.messagebox


class Main:
	def __init__(self, title="OST Entry System", size=(800, 700)):
		self.root = tk.Tk()
		self.root.minsize(size[0], size[1])
		self.size = size
		self.root.title(title)
		self.root.resizable(0, 0)
		self.infoFrame = None
	
	
	def add_info_frame(self):
		self.infoFrame = InfoFrame(self.root, self.size)
		self.infoFrame.pack(side=tk.TOP)
	
	
	def run(self):
		self.add_info_frame()
		self.root.mainloop()


class InfoFrame(tk.Frame):
	"""
	each info frame represents an ost_info object, it contains all ost info
	"""
	
	
	def __init__(self, master, size):
		super().__init__(master, width=size[0], height=size[1])
		self.size = size
		self.common_info_panel = None
		self.personal_info_panel = None
		self.course_panel = None
		self.add_common_info_panel()
	
	
	def add_common_info_panel(self):
		availWidth = self.size[0] - 10
		self.common_info_panel = CommonInfoPanel(self, size=(availWidth, 79))
		self.personal_info_panel = PersonalInfoPanel(self, size=(availWidth, 79))
		self.course_panel = CoursePanel(self, size=(availWidth, 386))  # 353
		# date_of_issue = DatePair(self, "OST Issue Date", (2000, 10, 28), size_config=(24, 100, 50, 5))
		# date_of_issue.place(x=400, y=500)
		# course = CoursePair(self, (availWidth, 24))
		# course.place(x=0, y=400, width=availWidth, height=24)
		self.common_info_panel.place(bordermode=tk.INSIDE, x=5, y=0)
		self.personal_info_panel.place(bordermode=tk.INSIDE, x=5, y=79)
		self.course_panel.place(bordermode=tk.INSIDE, x=5, y=158)


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
		pass


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
		self.add_items(width, height)
	
	
	def add_items(self, width, height):
		def delete_action(event):
			c = event.widget.master
			c.destroy()
			self.index -= 1
			self.courses.remove(c)
		
		
		def button_action():
			c = CoursePair(self.frame, (avail_width - 5, 24), delete_action, count_credit, count_compulsory)
			self.courses.append(c)
			self.index += 1
			c.grid(row=self.index, column=0, ipadx=0, ipady=2)
		
		
		def sort():
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
				tk.messagebox.showerror("Sort Error", "An Error has occurs when sorting. Please try again!\nThis is usually caused by incorrect format of the date.\nError: {}".format(exp.args[0]))
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
		
		
		def count_credit():
			value = sum([c.calculate_credit() for c in self.courses])
			if not isinstance(value, int) and value.is_integer():
				value = int(value)
			self.credit_summary.config(text=str(value))
			return True
		
		
		def count_compulsory():
			value = len([c for c in self.courses if c.is_compulsory_active()])
			self.compulsory_summary.config(text=str(value))
			return True
		
		
		self.canvas = tk.Canvas(self, bd=0, highlightthickness=0)
		self.frame = tk.Frame(self.canvas)
		self.add = tk.Button(self, text="+ ADD", command=button_action)
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
		self.sort = tk.Button(self, text="Sort", command=sort)
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


class OtherInfoPanel(tk.LabelFrame):
	def __init__(self, master, size):
		width, height = size
		super().__init__(master, text="Other Info", width=width, height=height)
		self.add_items(width, height)
	
	
	def add_items(self, width, height):
		community_enrollment = tk.Label(self, text="Community Involvement", anchor=tk.SW)
		PSSLR = tk.Label(self, text="Provincial Secondary School Literacy Requirement", anchor=tk.SW)
		ce = tk.BooleanVar()
		ce_true = tk.Radiobutton(self, text="Completed", variable=ce, value=True)
		ce_false = tk.Radiobutton(self, text="N/A", variable=ce, value=False)
		PSSLR_value = tk.BooleanVar()
		PSSLR_true = tk.Radiobutton(self, text="Completed", variable=PSSLR_value, value=True)
		PSSLR_false = tk.Radiobutton(self, text="N/A", variable=PSSLR_value, value=False)
		speclizaed_progrm = LabelEntryPair(self, "Specialized Program", "", ())
		diploma_or_certificate = LabelEntryPair(self, "Diploma or Certificate", "", ())
		date_of_diploma_or_certificate = DatePair(self, "Date of Issue", (2000, 1), ())


class CoursePair(tk.Frame):
	def __init__(self, master, size_config, button_action, count_credit, count_compulsory, texts=("", "", "", "", "", "", "", "")):
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
		self.add_items(width, height, texts, button_action, count_credit, count_compulsory)
	
	
	def add_items(self, width, height, texts, button_action, count_credit, count_compulsory):
		unit_height = height
		unit_width = (width - 5 * 8 - height) / 20
		date_text, grade_text, title_text, code_text, percentage_text, credit_text, compulsory_text, note_text = texts
		self.delete = tk.Button(master=self, text="X", fg="red")
		self.delete.bind("<1>", button_action)
		self.date = tk.Entry(master=self, bd=2)
		self.grade = tk.Entry(master=self, bd=2)
		self.title = tk.Entry(master=self, bd=2)
		self.code = tk.Entry(master=self, bd=2, validate="focusout", validatecommand=None)
		self.percentage = tk.Entry(master=self, bd=2)
		self.credit = tk.Entry(master=self, bd=2, validate="focusout", validatecommand=count_credit)
		self.compulsory = tk.Entry(master=self, bd=2, validate="focusout", validatecommand=count_compulsory)
		self.note = tk.Entry(master=self, bd=2)
		self.date.insert(tk.END, date_text)
		self.grade.insert(tk.END, grade_text)
		self.title.insert(tk.END, title_text)
		self.code.insert(tk.END, code_text)
		self.percentage.insert(tk.END, percentage_text)
		self.credit.insert(tk.END, credit_text)
		self.compulsory.insert(tk.END, compulsory_text)
		self.note.insert(tk.END, note_text)
		self.delete.place(x=0, y=0, width=height, height=unit_height)
		self.date.place(x=unit_width * 0 + 5 * 1 + height, y=0, width=unit_width * 2, height=unit_height)
		self.grade.place(x=unit_width * 2 + 5 * 2 + height, y=0, width=unit_width * 1, height=unit_height)
		self.title.place(x=unit_width * 3 + 5 * 3 + height, y=0, width=unit_width * 10, height=unit_height)
		self.code.place(x=unit_width * 13 + 5 * 4 + height, y=0, width=unit_width * 2, height=unit_height)
		self.percentage.place(x=unit_width * 15 + 5 * 5 + height, y=0, width=unit_width * 1, height=unit_height)
		self.credit.place(x=unit_width * 16 + 5 * 6 + height, y=0, width=unit_width * 1, height=unit_height)
		self.compulsory.place(x=unit_width * 17 + 5 * 7 + height, y=0, width=unit_width * 1, height=unit_height)
		self.note.place(x=unit_width * 18 + 5 * 8 + height, y=0, width=unit_width * 2, height=unit_height)
	
	
	def is_compulsory_active(self):
		return self.compulsory.get() != ""
	
	
	def calculate_credit(self):
		try:
			return float(self.credit.get())
		except ValueError:
			return 0
	
	
	def get_date(self):
		date = self.date.get()
		if date == "":
			return 0, 0, False
		result = re.findall("([\d]+)[\\\/\-\s]([\d]+)", string=date)[0]
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


if __name__ == '__main__':
	main = Main()
	main.run()
