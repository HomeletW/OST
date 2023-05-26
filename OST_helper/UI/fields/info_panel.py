import tkinter as tk

from OST_helper.UI.tk_objects import DatePair, LabelEntryPair, SimpleDatePair, \
    TopDownSizeConfig


class PersonalInfoPanel(tk.LabelFrame):
    def __init__(self, master, size_config: TopDownSizeConfig):
        self.size_config = size_config
        super().__init__(master, text="Personal Info", width=size_config.width,
                         height=size_config.height)
        # line 1
        self.surname = None
        self.given_name = None
        self.OEN = None
        self.student_number = None
        self.gender = None
        self.date_of_birth = None
        # line 2
        self.name_of_DSB = None
        self.number_of_DSB = None
        self.name_of_school = None
        self.number_of_school = None
        self.date_of_entry = None
        self.add_items()

    def add_items(self):
        divided = self.size_config.divide([
            [1, 3, 3, 2, 2, 2, 4],
            [1, 4, 2, 4, 2, 4],
        ], height_offset=20, width_offset=4, internal=False)
        self.surname = LabelEntryPair(
            self,
            label_text="Surname (Last Name)",
            entry_placeholder="",
            size_config=divided[0][0])
        self.given_name = LabelEntryPair(
            self,
            label_text="Given Name (First Name)",
            entry_placeholder="",
            size_config=divided[0][1])
        self.OEN = LabelEntryPair(
            self,
            label_text="OEN/MIN",
            entry_placeholder="",
            size_config=divided[0][2])
        self.student_number = LabelEntryPair(
            self,
            label_text="Student Number",
            entry_placeholder="",
            size_config=divided[0][3])
        self.gender = LabelEntryPair(
            self,
            label_text="Gender",
            entry_placeholder="",
            size_config=divided[0][4])
        self.date_of_birth = DatePair(
            self,
            text="Date of Birth",
            date=(0, 0, 0),
            size_config=divided[0][5])
        # line 2
        self.name_of_DSB = LabelEntryPair(
            self,
            label_text="Name Of School Board / Authority",
            entry_placeholder="",
            size_config=divided[1][0])
        self.number_of_DSB = LabelEntryPair(
            self,
            label_text="Number Of DSB",
            entry_placeholder="",
            size_config=divided[1][1])
        self.name_of_school = LabelEntryPair(
            self,
            label_text="Name Of School",
            entry_placeholder="",
            size_config=divided[1][2])
        self.number_of_school = LabelEntryPair(
            self,
            label_text="Number Of School",
            entry_placeholder="",
            size_config=divided[1][3])
        self.date_of_entry = DatePair(
            self,
            text="Date of Entry",
            date=(0, 0, 0),
            size_config=divided[1][4])
        self.size_config.place([
            [self.surname, self.given_name, self.OEN, self.student_number,
             self.gender, self.date_of_birth],
            [self.name_of_DSB, self.number_of_DSB, self.name_of_school,
             self.number_of_school, self.date_of_entry],
        ])

    def set(self, data):
        surename, given_name = data["name"]
        gender = data["gender"]
        date_of_birth = data["date_of_birth"]
        OEN = data["OEN"]
        student_number = data["student_number"]
        date_of_entry = data["date_of_entry"]
        name_of_DSB = data["name_of_district_school_board"]
        number_of_DSB = data["district_school_board_number"]
        name_of_school = data["name_of_school"]
        number_of_school = data["school_number"]
        self.surname.set(surename)
        self.given_name.set(given_name)
        self.gender.set(gender)
        self.date_of_birth.set(date_of_birth)
        self.OEN.set(OEN)
        self.student_number.set(student_number)
        self.date_of_entry.set(date_of_entry)
        self.name_of_DSB.set(name_of_DSB)
        self.number_of_DSB.set(number_of_DSB)
        self.name_of_school.set(name_of_school)
        self.number_of_school.set(number_of_school)

    def get(self, data):
        surename = self.surname.get()
        given_name = self.given_name.get()
        gender = self.gender.get()
        date_of_birth = self.date_of_birth.get()
        OEN = self.OEN.get()
        student_number = self.student_number.get()
        date_of_entry = self.date_of_entry.get()
        name_of_DSB = self.name_of_DSB.get()
        number_of_DSB = self.number_of_DSB.get()
        name_of_school = self.name_of_school.get()
        number_of_school = self.number_of_school.get()
        name = [surename, given_name]
        data["name"] = name
        data["gender"] = gender
        data["date_of_birth"] = date_of_birth
        data["OEN"] = OEN
        data["student_number"] = student_number
        data["date_of_entry"] = date_of_entry
        data["name_of_district_school_board"] = name_of_DSB
        data["district_school_board_number"] = number_of_DSB
        data["name_of_school"] = name_of_school
        data["school_number"] = number_of_school


class OtherInfoPanel(tk.LabelFrame):
    def __init__(self, master, size_config: TopDownSizeConfig):
        self.size_config = size_config
        super().__init__(master, text="Other Info", width=size_config.width,
                         height=size_config.height)
        self.community_involvement_var = None
        self.community_involvement = None
        self.literacy_requirement_var = None
        self.literacy_requirement = None
        self.online_learning_requirement_var = None
        self.online_learning_requirement = None
        self.specialized_program = None
        self.diploma_or_certificate = None
        self.diploma_or_certificate_date_of_issue = None
        self.authorization = None
        self.add_items()

    def add_items(self):
        divided = self.size_config.divide([
            [1, 1.8, 2.1, 2.1, 4],
            [1, 5, 1, 4],
        ], height_offset=20, width_offset=4, internal=False)
        self.community_involvement_var = tk.BooleanVar()
        self.community_involvement = tk.Checkbutton(
            self,
            text="Community Involvement",
            variable=self.community_involvement_var)
        self.literacy_requirement_var = tk.BooleanVar()
        self.literacy_requirement = tk.Checkbutton(
            self,
            text="Provincial Literacy Requirement",
            variable=self.literacy_requirement_var)
        self.online_learning_requirement_var = tk.BooleanVar()
        self.online_learning_requirement = tk.Checkbutton(
            self,
            text="Online Learning Requirement",
            variable=self.online_learning_requirement_var)
        self.specialized_program = LabelEntryPair(
            self,
            "Specialized Program",
            "",
            divided[0][3])
        self.diploma_or_certificate = LabelEntryPair(
            self,
            "Diploma or Certificate",
            "",
            divided[1][0]
        )
        self.diploma_or_certificate_date_of_issue = SimpleDatePair(
            self,
            ("2000", "1"),
            "Date of Issue",
            divided[1][1])
        self.authorization = LabelEntryPair(
            self,
            "Authorization",
            "",
            divided[1][2]
        )
        self.size_config.place([
            [self.community_involvement, self.literacy_requirement,
             self.online_learning_requirement, self.specialized_program],
            [self.diploma_or_certificate,
             self.diploma_or_certificate_date_of_issue, self.authorization],
        ])

    def set(self, data):
        community_involvement = data["community_involvement_flag"]
        literacy_requirement = data[
            "provincial_secondary_school_literacy_requirement_flag"]
        online_learning_requirement = data[
            "secondary_school_online_learning_requirement_flag"]
        specialized_program = data["specialized_program"]
        diploma_or_certificate = data["diploma_or_certificate"]
        diploma_or_certificate_date_of_issue = data[
            "diploma_or_certificate_date_of_issue"]
        authorization = data["authorization"]
        self.community_involvement_var.set(community_involvement)
        self.literacy_requirement_var.set(literacy_requirement)
        self.online_learning_requirement_var.set(online_learning_requirement)
        self.specialized_program.set(specialized_program)
        self.diploma_or_certificate.set(diploma_or_certificate)
        self.diploma_or_certificate_date_of_issue.set(
            diploma_or_certificate_date_of_issue)
        self.authorization.set(authorization)

    def get(self, data):
        community_involvement = self.community_involvement_var.get()
        literacy_requirement = self.literacy_requirement_var.get()
        online_learning_requirement = self.online_learning_requirement_var.get()
        specialized_program = self.specialized_program.get()
        diploma_or_certificate = self.diploma_or_certificate.get()
        diploma_or_certificate_date_of_issue = self.diploma_or_certificate_date_of_issue.get()
        authorization = self.authorization.get()
        data["community_involvement_flag"] = community_involvement
        data["provincial_secondary_school_literacy_requirement_flag"] = literacy_requirement
        data["secondary_school_online_learning_requirement_flag"] = online_learning_requirement
        data["specialized_program"] = specialized_program
        data["diploma_or_certificate"] = diploma_or_certificate
        data["diploma_or_certificate_date_of_issue"] = diploma_or_certificate_date_of_issue
        data["authorization"] = authorization
