import json
import os
from datetime import date


today = None


def update_today():
	global today
	day = date.today()
	year, month, day = day.year, day.month, day.day
	today = str(year), str(month), str(day)


update_today()

default_ost_info = { "OST_date_of_issue": today,
                     "name": ["", ""],
                     "OEN": "",
                     "student_number": "",
                     "gender": "",
                     "date_of_birth": ["", "", ""],
                     "name_of_district_school_board": "Toronto Private Inspected",
                     "district_school_board_number": "",
                     "name_of_school": "McCanny Secondary School",
                     "school_number": "668908",
                     "date_of_entry": ["", "", ""],
                     "community_involvement_flag": True,
                     "provincial_secondary_school_literacy_requirement_flag": True,
                     "specialized_program": "",
                     "diploma_or_certificate": "Ontario Secondary School Diploma",
                     "diploma_or_certificate_date_of_issue": ["", ""],
                     "authorization": "Dr. Alireza Rafiee",
                     "course_list": [],
                     "course_font_size": 50,
                     "course_spacing": 5,
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
	
	
	def to_json(self):
		return [self.date, self.level, self.title, self.code, self.percentage, self.credit, self.compulsory, self.note]
	
	
	@classmethod
	def from_json(cls, data):
		_date, level, title, code, percentage, credit, compulsory, note = data
		return cls(_date, level, title, code, percentage, credit, compulsory, note)


class OST_info:
	"""
	Each OST_info object contains the all the info associated with this OST
	"""
	
	
	def __init__(self,
	             OST_date_of_issue=default_ost_info["OST_date_of_issue"],
	             name=default_ost_info["name"],
	             OEN=default_ost_info["OEN"],
	             student_number=default_ost_info["student_number"],
	             gender=default_ost_info["gender"],
	             date_of_birth=default_ost_info["date_of_birth"],
	             name_of_district_school_board=default_ost_info["name_of_district_school_board"],
	             district_school_board_number=default_ost_info["district_school_board_number"],
	             name_of_school=default_ost_info["name_of_school"],
	             school_number=default_ost_info["school_number"],
	             date_of_entry=default_ost_info["date_of_entry"],
	             community_involvement_flag=default_ost_info["community_involvement_flag"],
	             provincial_secondary_school_literacy_requirement_flag=default_ost_info["provincial_secondary_school_literacy_requirement_flag"],
	             specialized_program=default_ost_info["specialized_program"],
	             diploma_or_certificate=default_ost_info["diploma_or_certificate"],
	             diploma_or_certificate_date_of_issue=default_ost_info["diploma_or_certificate_date_of_issue"],
	             authorization=default_ost_info["authorization"]
	             ):
		self._OST_date_of_issue = [OST_date_of_issue[0], OST_date_of_issue[1], OST_date_of_issue[2]]
		# last name(surname), first name(given name)
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
		return "{}{}".format(self._name[0], " " + self._name[1] if self._name[1] != "" else "")
	
	
	def OST_date_of_issue(self):
		year, month, day = self._OST_date_of_issue
		return month + "/" + day + "/" + year
	
	
	def update_date_of_issue(self, date):
		year, month, day = date
		self._OST_date_of_issue = (year, month, day)
	
	
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
	
	
	def set_font_size(self, font_size):
		self._course_font_size = font_size
	
	
	def set_spacing(self, spacing):
		self._course_spacing = spacing
	
	
	def to_data(self):
		data = { "OST_date_of_issue": self._OST_date_of_issue,
		         "name": self._name,
		         "OEN": self._OEN,
		         "student_number": self._student_number,
		         "gender": self._gender,
		         "date_of_birth": self._date_of_birth,
		         "name_of_district_school_board": self._name_of_district_school_board,
		         "district_school_board_number": self._district_school_board_number,
		         "name_of_school": self._name_of_school,
		         "school_number": self._school_number,
		         "date_of_entry": self._date_of_entry,
		         "community_involvement_flag": self._community_involvement_flag,
		         "provincial_secondary_school_literacy_requirement_flag": self._provincial_secondary_school_literacy_requirement_flag,
		         "specialized_program": self._specialized_program,
		         "diploma_or_certificate": self._diploma_or_certificate,
		         "diploma_or_certificate_date_of_issue": self._diploma_or_certificate_date_of_issue,
		         "authorization": self._authorization,
		         "course_list": [course.to_json() for course in self._course_list],
		         "course_font_size": self._course_font_size,
		         "course_spacing": self._course_spacing,
		         }
		return data
	
	
	def to_json(self, path: str):
		data = self.to_data()
		ext = os.path.splitext(path)[-1].lower()
		if ext != ".json":
			path += ".json"
		with open(path, 'w+') as js:
			json.dump(data, js, indent=4)
	
	
	@classmethod
	def from_json(cls, path: str):
		with open(path, 'r') as js:
			data = json.load(js)
		return cls.from_data(data)
	
	
	@classmethod
	def from_data(cls, data):
		OST_date_of_issue = data["OST_date_of_issue"]
		name = data["name"]
		OEN = data["OEN"]
		student_number = data["student_number"]
		gender = data["gender"]
		date_of_birth = data["date_of_birth"]
		name_of_district_school_board = data["name_of_district_school_board"]
		district_school_board_number = data["district_school_board_number"]
		name_of_school = data["name_of_school"]
		school_number = data["school_number"]
		date_of_entry = data["date_of_entry"]
		community_involvement_flag = data["community_involvement_flag"]
		provincial_secondary_school_literacy_requirement_flag = data["provincial_secondary_school_literacy_requirement_flag"]
		specialized_program = data["specialized_program"]
		diploma_or_certificate = data["diploma_or_certificate"]
		diploma_or_certificate_date_of_issue = data["diploma_or_certificate_date_of_issue"]
		authorization = data["authorization"]
		course_list = [course if type(course) is Course else Course.from_json(course) for course in data["course_list"]]
		course_font_size = data["course_font_size"]
		course_spacing = data["course_spacing"]
		ost = cls(
				OST_date_of_issue=OST_date_of_issue,
				name=name,
				OEN=OEN,
				student_number=student_number,
				gender=gender,
				date_of_birth=date_of_birth,
				name_of_district_school_board=name_of_district_school_board,
				district_school_board_number=district_school_board_number,
				name_of_school=name_of_school,
				school_number=school_number,
				date_of_entry=date_of_entry,
				community_involvement_flag=community_involvement_flag,
				provincial_secondary_school_literacy_requirement_flag=provincial_secondary_school_literacy_requirement_flag,
				specialized_program=specialized_program,
				diploma_or_certificate=diploma_or_certificate,
				diploma_or_certificate_date_of_issue=diploma_or_certificate_date_of_issue,
				authorization=authorization,
		)
		ost._course_list = course_list
		ost._course_font_size = course_font_size
		ost._course_spacing = course_spacing
		return ost


json_path = "default_ost.json"

try:
	default_ost = OST_info.from_json(json_path)
	default_ost.update_date_of_issue(today)
except Exception as exp:
	print("No default OST info found, restoring from default..., Error: {}".format(str(exp)))
	default_ost = OST_info.from_data(default_ost_info)


def finalize():
	default_ost.to_json(json_path)
