import tkinter as tk

from OST_helper.UI.tk_objects import DatePair, TopDownSizeConfig


class UtilityPanel(tk.Frame):
    def __init__(self, master, size_config: TopDownSizeConfig):
        self.size_config = size_config
        super().__init__(master, width=size_config.width,
                         height=size_config.height)
        self.master = master
        self.ost_date_of_issue = None
        self.new = None
        self.open = None
        self.generate = None
        self.save = None
        self.save_as = None
        self.adjust = None
        self.add_items()

    def add_items(self):
        divide = self.size_config.divide([
            [1, 4, 2, 1, 1, 1, 1, 1, 1]
        ])
        self.ost_date_of_issue = DatePair(
            self, "Date of Issue", ("", "", ""), divide[0][0], place_side=True)
        self.new = tk.Button(self, text="New",
                             command=self.master.new_draft_action)
        self.open = tk.Button(self, text="Open",
                              command=self.master.open_action)
        self.save = tk.Button(self, text="Save",
                              command=self.master.save_action)
        self.save_as = tk.Button(self, text="Save As...",
                              command=self.master.save_as_action)
        self.adjust = tk.Button(self, text="Preview...",
                                command=self.master.adjust_action, fg="#CC0066")
        self.generate = tk.Button(self, text="Generate",
                                  command=self.master.generate_action, fg="#CC0066")
        self.size_config.place([
            [self.ost_date_of_issue, None, self.new, self.open, self.save, self.save_as,
             self.adjust, self.generate]
        ])

    def set(self, data):
        date_of_issue = data["OST_date_of_issue"]
        self.ost_date_of_issue.set(date_of_issue)

    def get(self, data):
        date_of_issue = self.ost_date_of_issue.get()
        data["OST_date_of_issue"] = date_of_issue
