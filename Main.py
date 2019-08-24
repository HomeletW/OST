default_value = {
	"date": ("2000", "1", "1"),
	"date_simplify": ("2000", "1"),
	"name_of_district_school_board": "Toronto Private Inspected",
	"district_school_board_number": "",
	"name_of_school": "McCanny Secondary School",
	"school_number": "668901",
	"authorization": "Dr. Alireza Rafiee",
}

# "course_code": ["course_title", "course_level"]
common_course_code_index = {
}


class Course:
	"""
	Each course object represent a course in the OST
	"""
	
	
	def __init__(self,
	             date: str = "",
	             level: str = "",
	             title: str = "",
	             code: str = "",
	             percentage: str = "",
	             credit: str = "",
	             compulsory: str = "",
	             note: str = ""
	             ):
		self.date = date
		self.level = level
		self.title = title
		self.code = code
		self.percentage = percentage
		self.credit = credit
		self.compulsory = compulsory
		self.note = note
	
	
	def is_course(self):
		return self.code != ""
	
	
	def is_compulsory_active(self):
		return self.is_course() and self.compulsory != ""
	
	
	def calculate_credit(self):
		if not self.is_course():
			return 0
		try:
			return float(self.credit)
		except ValueError:
			return 0


class OST_info:
	"""
	Each OST_info object contains the all the info associated with this OST
	"""
	
	
	def __init__(self,
	             OST_date_of_issue=default_value["date"],
	             name=("", ""),
	             OEN="",
	             student_number="",
	             gender="M",
	             date_of_birth=default_value["date"],
	             name_of_district_school_board=default_value["name_of_district_school_board"],
	             district_school_board_number=default_value["district_school_board_number"],
	             name_of_school=default_value["name_of_school"],
	             school_number=default_value["school_number"],
	             date_of_entry=default_value["date"],
	             community_involvement_flag=True,
	             provincial_secondary_school_literacy_requirement_flag=True,
	             specialized_program="",
	             diploma_or_certificate="",
	             diploma_or_certificate_date_of_issue=default_value["date_simplify"],
	             authorization=default_value["authorization"]
	             ):
		self._OST_date_of_issue = [OST_date_of_issue[0], OST_date_of_issue[1], OST_date_of_issue[2]]
		self._name = [name[0], name[1]]
		self._OEN = OEN
		self._student_number = student_number
		self._gender = gender
		self._date_of_birth = [date_of_birth[0], date_of_birth[1], date_of_birth[2]]
		self._name_of_district_school_board = name_of_district_school_board
		self._district_school_board_number = district_school_board_number
		self._name_of_school = name_of_school
		self._school_number = school_number
		self._date_of_entry = [date_of_entry[0], date_of_entry[1], date_of_entry[2]]
		self._community_involvement_flag = community_involvement_flag
		self._provincial_secondary_school_literacy_requirement_flag = provincial_secondary_school_literacy_requirement_flag
		self._specialized_program = specialized_program
		self._diploma_or_certificate = diploma_or_certificate
		self._diploma_or_certificate_date_of_issue = [diploma_or_certificate_date_of_issue[0], diploma_or_certificate_date_of_issue[1]]
		self._authorization = authorization
		self._course_list = []
		self._course_font_size = 50
		self._course_spacing = 5
	
	
	def course(self):
		return self._course_list
	
	
	def count_course_credit(self):
		return sum([c.calculate_credit() for c in self._course_list])
	
	
	def count_course_compulsory(self):
		return len([c for c in self._course_list if c.is_compulsory_active()])
	
	
	def course_font_size(self):
		return self._course_font_size
	
	
	def course_spacing(self):
		return self._course_spacing
	
	
	def full_name(self):
		return self._name[0] + " " + self._name[1]
	
	
	def OST_date_of_issue(self):
		year, month, day = self._OST_date_of_issue
		return month + "/" + day + "/" + year
	
	
	def surname(self):
		return self._name[0]
	
	
	def given_name(self):
		return self._name[1]
	
	
	def OEN(self):
		return self._OEN
	
	
	def student_number(self):
		return self._student_number
	
	
	def gender(self):
		return self._gender
	
	
	def date_of_birth_y(self):
		return self._date_of_birth[0]
	
	
	def date_of_birth_m(self):
		return self._date_of_birth[1]
	
	
	def date_of_birth_d(self):
		return self._date_of_birth[2]
	
	
	def name_of_district_school_board(self):
		return self._name_of_district_school_board
	
	
	def district_school_board_number(self):
		return self._district_school_board_number
	
	
	def name_of_school(self):
		return self._name_of_school
	
	
	def school_number(self):
		return self._school_number
	
	
	def date_of_entry_y(self):
		return self._date_of_entry[0]
	
	
	def date_of_entry_m(self):
		return self._date_of_entry[1]
	
	
	def date_of_entry_d(self):
		return self._date_of_entry[2]
	
	
	def community_involvement(self):
		return self._community_involvement_flag
	
	
	def provincial_secondary_school_literacy_requirement(self):
		return self._provincial_secondary_school_literacy_requirement_flag
	
	
	def specialized_program(self):
		return self._specialized_program
	
	
	def diploma_or_certificate(self):
		return self._diploma_or_certificate
	
	
	def diploma_or_certificate_date_of_issue_y(self):
		return self._diploma_or_certificate_date_of_issue[0]
	
	
	def diploma_or_certificate_date_of_issue_m(self):
		return self._diploma_or_certificate_date_of_issue[1]
	
	
	def authorization(self):
		return self._authorization
