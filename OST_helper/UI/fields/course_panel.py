import math
import re
import tkinter as tk
import tkinter.messagebox

from OST_helper.UI.tk_objects import TopDownSizeConfig, set_entry_value
from OST_helper.data_handler import Data
from OST_helper.parameter import *


class CoursePanel(tk.Frame):
    def __init__(self, master, size_config: TopDownSizeConfig):
        self.size_config = size_config
        super().__init__(master, width=size_config.width,
                         height=size_config.height)
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
        self.symbol_label = None
        self.note_label = None
        self.scrollBar = None
        self.sort = None
        self.credit_summary = None
        self.compulsory_summary = None
        self.visible_on_screen = 10
        self.course_size = None
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
        self.add_items()

    def add_course(self, sync=True):
        c = CoursePair(self.frame, self.master, self.course_size,
                       self.delete_action, self.count_credit,
                       self.count_compulsory, self.count_courses,
                       self.next_action, self.enter_action, self.prev_action,
                       self.right_action, self.left_action)
        self.courses.append(c)
        self.index += 1
        c.grid(row=self.index, column=0, ipadx=0, ipady=2)
        if sync:
            self.set_focus(self.index - 1, "code")
        # c.bind_all("<MouseWheel>", self.mouse_scroll, add=True)
        return c

    def sync_canvas_loc(self, index):
        if self.index < self.visible_on_screen:
            self.after(10, self.canvas.yview_moveto, 0)
            return
        screen_index = index // self.visible_on_screen
        total_screens = math.ceil(self.index / self.visible_on_screen)
        self.after(10, self.canvas.yview_moveto, screen_index / total_screens)

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
        if not SETTING["train"]:
            return
        train_able = [course.train_data() for course in self.courses]
        train_able = [data for data in train_able if
                      data[0] != "" and data[1] != "" and data[2] != "" and
                      data[3] != ""]
        for code, title, level, credit, compulsory in train_able:
            COMMON_COURSE_CODE_LIBRARY[code.upper()] = (
                title, level, credit, compulsory)
        self.master.status_bar.set(
            "{} Trained!".format(
                ",".join(code for code, _, _, _, _ in train_able)))

    def sort_course(self):
        try:
            active_course = []
            inactive_course = []
            for c in self.courses:
                date_ = c.get_date()
                if date_[2]:
                    active_course.append((date_, c))
                else:
                    inactive_course.append((date_, c))
        except Exception as e:
            tk.messagebox.showerror(
                parent=self, title="Sort Error",
                message="An Error has occurs when sorting. "
                        "Please fix the error and try again!\n"
                        "\n"
                        "This is usually caused by incorrect format of the date."
                        "\n\n"
                        "The allowed format includes:\n"
                        "➜ 2000\\10\n"
                        "➜ 2000/10\n"
                        "➜ 2000-10\n"
                        "➜ 2000.10\n"
                        "➜ 2000 10\n\n"
                        "Error:\n{}".format(str(e)))
            return
        # first remove all the widget from the frame
        for c in self.courses:
            c.grid_forget()
        self.courses.clear()
        active_course.sort(key=lambda pair: (pair[0][0], pair[0][1]))
        index = 0
        for _, c in active_course:
            c.grid(row=index, column=0, ipadx=0, ipady=2)
            self.courses.append(c)
            index += 1
        for _, c in inactive_course:
            c.grid(row=index, column=0, ipadx=0, ipady=2)
            self.courses.append(c)
            index += 1

    def add_items(self):
        divided = self.size_config.divide([
            [1, 1],
            [1, 1, 3, 2, 12, 3, 2, 2, 2, 3, 1],
            [12, 30, 1],
            [1, 1, 3, 2, 12, 5, 2, 2, 3, 1],
        ])
        self.canvas = tk.Canvas(self, bd=0, highlightthickness=0)
        self.frame = tk.Frame(self.canvas)
        self.add = tk.Button(self, text="+ ADD Course", command=self.add_course)
        self.date_label = tk.Label(self, text="Date (Y/M)", anchor=tk.S)
        self.grade_label = tk.Label(self, text="Level", anchor=tk.S)
        self.title_label = tk.Label(self, text="Course Title", anchor=tk.S)
        self.code_label = tk.Label(self, text="Course Code", anchor=tk.S)
        self.percentage_label = tk.Label(self, text="Grade %", anchor=tk.S)
        self.credit_label = tk.Label(self, text="Credit", anchor=tk.S)
        self.compulsory_label = tk.Label(self, text="Comp.", anchor=tk.S)
        self.note_label = tk.Label(self, text="Note", anchor=tk.S)
        self.scrollBar = tk.Scrollbar(self, orient="vertical",
                                      command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.scrollBar.set)
        self.sort = tk.Button(self, text="Sort", command=self.sort_course)
        self.credit_summary = tk.Label(self, text="0", anchor=tk.N)
        self.compulsory_summary = tk.Label(self, text="0", anchor=tk.N)
        self.symbol_label = tk.Label(self, text="SUMMARY OF CREDITS \u2192",
                                     anchor=tk.NE, justify=tk.LEFT)
        self.canvas.create_window((0, 0), window=self.frame, anchor="nw")
        self.size_config.place([
            [self.add],
            [None, self.date_label, self.grade_label, self.title_label,
             self.code_label, self.percentage_label, self.credit_label,
             self.compulsory_label, self.note_label],
            [self.canvas, self.scrollBar],
            [None, self.sort, None, None, self.symbol_label,
             self.credit_summary,
             self.compulsory_summary, None, None],
        ])

        canvas_size = divided[2][0]

        canvas_width, canvas_height = canvas_size.size()

        def conf(_):
            self.canvas.config(scrollregion=self.canvas.bbox("all"),
                               width=canvas_width, height=canvas_height)

        self.frame.bind("<Configure>", conf)
        self.course_size = canvas_size.divide(
            [[1, 1]] * self.visible_on_screen
        )[0][0]
        # self.bind("<FocusOut>", self.train)
        # self.canvas.bind_all("<MouseWheel>", self.mouse_scroll)

    def set(self, courses, sort=True):
        for c in self.courses:
            c.grid_forget()
        self.courses.clear()
        self.index = 0
        for data in courses:
            c = self.add_course()
            c.set(data)
        if sort:
            self.sort_course()
        self.sync_canvas_loc(0)
        self.count_courses()
        self.count_compulsory()
        self.count_credit()

    def get(self):
        course = [c.get() for c in self.courses]
        return course


class CoursePair(tk.Frame):
    def __init__(self, master, info_frame, size_config: TopDownSizeConfig,
                 button_action, count_credit, count_compulsory, count_course,
                 next_action, enter_action, prev_action, right_action,
                 left_action):
        self.size_config = size_config
        super().__init__(master, width=size_config.width,
                         height=size_config.height)
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
        self.add_items(button_action, count_credit,
                       count_compulsory, count_course, next_action,
                       enter_action, prev_action, right_action, left_action)

    def add_items(self, button_action, count_credit,
                  count_compulsory, count_course, next_action, enter_action,
                  prev_action, right_action, left_action):
        def smart_fill(_):
            self.smart_fill()
            count_course()
            count_compulsory()
            count_credit()

        self.size_config.divide([
            [1, 1, 3, 2, 12, 3, 2, 2, 2, 3],
        ])
        self.delete = tk.Button(master=self, text="X")
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
        self.size_config.place([
            [self.delete, self.date, self.grade, self.title, self.code,
             self.percentage, self.credit, self.compulsory, self.note]
        ])

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
        if not SETTING["smart_fill"]:
            return
        code = self.code.get().upper()
        if code not in COMMON_COURSE_CODE_LIBRARY:
            return
        title, level, credit, compulsory = COMMON_COURSE_CODE_LIBRARY[code]
        if self.title.get() != "" or \
                self.grade.get() != "" or \
                self.credit.get() != "" or \
                self.compulsory.get() != "":
            return
        else:
            self.title.insert(0, title)
            self.grade.insert(0, level)
            self.credit.insert(0, credit)
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
        date_ = self.date.get()
        if date_ == "":
            return 0, 0, False
        result = re.findall("([\d]+)[\\\/\-.\s]([\d]+)", string=date_)[0]
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
