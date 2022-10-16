import threading
import tkinter as tk


class GenerateThread(threading.Thread):
    def __init__(self, progress_dialog, ):
        super().__init__(name="GenerateThread", daemon=True)
        pass

    def _update_progress(self):
        pass


DEFAULT_SPACING = 5


class TopDownSizeConfig:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self._config = None
        self._spacing = None
        self._internal = None

    def divide(self, config,
               spacing=DEFAULT_SPACING, internal=True, width_offset=0,
               height_offset=0):
        """
        Config should be in the format of:
        (
            (HEIGHT_PROP, FIRST_WIDTH_PROP, SECOND_WIDTH_PROP, ...)
        )
        """
        self._config = []
        self._spacing = spacing
        self._internal = internal
        divided = []
        hei_config = [row[0] for row in config]
        divided_height = self._div_height(hei_config, spacing, internal,
                                          height_offset)
        for index, row in enumerate(config):
            height = divided_height[index]
            row_config = row[1:]
            divided_width = self._div_width(row_config, spacing, internal,
                                            width_offset)
            divided.append(
                [TopDownSizeConfig(width, height) for width in divided_width]
            )
            self._config.append(
                [height] + divided_width
            )
        return divided

    def _div_width(self, row_config, spacing, internal, offset):
        avi_width = self.width - offset - (
            len(row_config) - 1 if internal else len(row_config) + 1) * spacing
        unit_width = avi_width / sum(row_config)
        return [unit_width * prop for prop in row_config]

    def _div_height(self, hei_config, spacing, internal, offset):
        avi_height = self.height - offset - (
            len(hei_config) - 1 if internal else len(hei_config) + 1) * spacing
        unit_height = avi_height / sum(hei_config)
        return [unit_height * prop for prop in hei_config]

    def size(self):
        return self.width, self.height

    def place(self, comp):
        if self._config is None:
            # no config added, just put the component spans the width and height
            comp.place(x=0, y=0, width=self.width, height=self.height)
        else:
            y = 0 if self._internal else self._spacing
            for row, row_config in zip(comp, self._config):
                row_height = row_config[0]
                x = 0 if self._internal else self._spacing
                for c, width in zip(row, row_config[1:]):
                    if c is not None:
                        c.place(x=x, y=y, width=width, height=row_height)
                    x += width + self._spacing
                y += row_height + self._spacing


class ScalePair(tk.Frame):
    def __init__(self, master, text, from_, to, command,
                 size_config: TopDownSizeConfig):
        self.size_config = size_config
        super().__init__(master, width=size_config.width,
                         height=size_config.height)
        self.label = None
        self.scale = None
        self.add_item(text, from_, to, command)

    def add_item(self, text, from_, to, command):
        self.size_config.divide([
            [1, 1, 7],
        ])
        self.label = tk.Label(self, text=text, anchor=tk.E)
        self.scale = tk.Scale(
            self, from_=from_, to=to, orient=tk.HORIZONTAL,
            repeatinterval=200, command=command)
        self.size_config.place([
            [self.label, self.scale]
        ])

    def set(self, value):
        self.scale.set(value)

    def get(self):
        return self.scale.get()


class LabelEntryPair(tk.Frame):
    def __init__(self, master, label_text, entry_placeholder,
                 size_config: TopDownSizeConfig):
        self.size_config = size_config
        super().__init__(master, width=size_config.width,
                         height=size_config.height)
        self.label = None
        self.entry = None
        self.add_items(label_text, entry_placeholder)

    def add_items(self, label_text, entry_placeholder):
        self.size_config.divide([
            [1, 1],
            [2, 1],
        ])
        self.label = tk.Label(master=self, text=label_text, anchor=tk.W)
        self.entry = tk.Entry(master=self, bd=2)
        self.entry.insert(tk.END, entry_placeholder)
        self.size_config.place([
            [self.label],
            [self.entry]
        ])
        self.enable()

    def set(self, value):
        set_entry_value(self.entry, value)

    def get(self):
        return self.entry.get()

    def disable(self):
        self.label.config(state="disabled")
        self.entry.config(state="disabled")

    def enable(self):
        self.label.config(state="normal")
        self.entry.config(state="normal")

class DatePair(tk.Frame):
    def __init__(self, master, text, date, size_config: TopDownSizeConfig,
                 spacing_text="-", place_side=False):
        # (height, label_width, unit_width, spacing)
        self.size_config = size_config
        year, month, day = date
        super().__init__(master,
                         width=size_config.width,
                         height=size_config.height)
        self.label = None
        self.entry_year = None
        self.spacing_1 = None
        self.entry_month = None
        self.spacing_2 = None
        self.entry_day = None
        if place_side:
            self.add_side_items(text, spacing_text, year, month, day)
        else:
            self.add_items(text, spacing_text, year, month, day)

    def add_items(self, text, spacing_text, year, month, day):
        self.size_config.divide([
            [1, 1],
            [2, 4, 1, 4, 1, 4],
        ])
        self.label = tk.Label(master=self, text=text, anchor=tk.W)
        self.entry_year = tk.Entry(master=self, bd=2)
        self.entry_year.insert(tk.END, year)
        self.spacing_1 = tk.Label(master=self, text=spacing_text,
                                  anchor=tk.CENTER)
        self.entry_month = tk.Entry(master=self, bd=2)
        self.entry_month.insert(tk.END, month)
        self.spacing_2 = tk.Label(master=self, text=spacing_text,
                                  anchor=tk.CENTER)
        self.entry_day = tk.Entry(master=self, bd=2)
        self.entry_day.insert(tk.END, day)
        self.size_config.place([
            [self.label],
            [self.entry_year, self.spacing_1, self.entry_month,
             self.spacing_2, self.entry_day]
        ])

    def add_side_items(self, text, spacing_text, year, month, day):
        self.size_config.divide([
            [1, 5, 4, 1, 4, 1, 4],
        ])
        self.label = tk.Label(master=self, text=text, anchor=tk.W)
        self.entry_year = tk.Entry(master=self, bd=2)
        self.entry_year.insert(tk.END, year)
        self.spacing_1 = tk.Label(master=self, text=spacing_text,
                                  anchor=tk.CENTER)
        self.entry_month = tk.Entry(master=self, bd=2)
        self.entry_month.insert(tk.END, month)
        self.spacing_2 = tk.Label(master=self, text=spacing_text,
                                  anchor=tk.CENTER)
        self.entry_day = tk.Entry(master=self, bd=2)
        self.entry_day.insert(tk.END, day)
        self.size_config.place([
            [self.label, self.entry_year, self.spacing_1, self.entry_month,
             self.spacing_2, self.entry_day]
        ])

    def set(self, date):
        year, month, day = date
        set_entry_value(self.entry_year, year)
        set_entry_value(self.entry_month, month)
        set_entry_value(self.entry_day, day)

    def get(self):
        year, month, day = self.entry_year.get(), self.entry_month.get(), self.entry_day.get()
        return [year, month, day]


class SimpleDatePair(tk.Frame):
    def __init__(self, master, date, text, size_config: TopDownSizeConfig,
                 spacing_text="-"):
        self.size_config = size_config
        year, month = date
        super().__init__(master, width=size_config.width,
                         height=size_config.height)
        self.label = None
        self.entry_year = None
        self.spacing_1 = None
        self.entry_month = None
        self.add_items(text, spacing_text, year, month)

    def add_items(self, text, spacing_text, year, month):
        self.size_config.divide([
            [1, 1],
            [2, 2, 1, 2],
        ])
        self.label = tk.Label(master=self, text=text, anchor=tk.W)
        self.entry_year = tk.Entry(master=self, bd=2)
        self.entry_year.insert(tk.END, year)
        self.spacing_1 = tk.Label(master=self, text=spacing_text,
                                  anchor=tk.CENTER)
        self.entry_month = tk.Entry(master=self, bd=2)
        self.entry_month.insert(tk.END, month)
        self.size_config.place([
            [self.label],
            [self.entry_year, self.spacing_1, self.entry_month]
        ])

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
