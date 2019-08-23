from typing import *


default_value = {
	"date": (2000, 1, 1),
	"date_simplify": (2000, 1),
	"name_of_district_school_board": "Toronto Private Inspected",
	"district_school_board_number": "",
	"name_of_school": "McCanny Secondary School",
	"school_number": "668901",
	"authorization": "Dr. Alireza Rafiee"
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
	             course_grade_level: str = "",
	             course_title: str = "",
	             course_code: str = "",
	             percentage_grade: str = "",
	             credit: str = "",
	             compulsory: str = "",
	             note: str = ""
	             ):
		self.date = date
		self.course_grade_level = course_grade_level
		self.course_title = course_title
		self.course_code = course_code
		self.percentage_grade = percentage_grade
		self.credit = credit
		self.compulsory = compulsory
		self.note = note


class OST_info:
	"""
	Each OST_info object contains the all the info associated with this OST
	"""
	
	
	def __init__(self,
	             OST_date_of_issue: List[int, int, int] = default_value["date"],
	             name: List[str, str] = ("", ""),
	             OEN: str = "",
	             student_number: str = "",
	             gender: str = "M",
	             date_of_birth: List[int, int, int] = default_value["date"],
	             name_of_district_school_board: str = default_value["name_of_district_school_board"],
	             district_school_board_number: str = default_value["district_school_board_number"],
	             name_of_school: str = default_value["name_of_school"],
	             school_number: str = default_value["school_number"],
	             date_of_entry: List[int, int, int] = default_value["date"],
	             community_involvement_flag=True,
	             provincial_secondary_school_literacy_requirement_flag=True,
	             specialized_program: str = "",
	             diploma_or_certificate: str = "",
	             diploma_or_certificate_date_of_issue: List[int, int] = default_value["date_simplify"],
	             authorization: str = default_value["authorization"]
	             ):
		self.OST_date_of_issue = [OST_date_of_issue[0], OST_date_of_issue[1], OST_date_of_issue[2]]
		self.name = [name[0], name[1]]
		self.OEN = OEN
		self.student_number = student_number
		self.gender = gender
		self.date_of_birth = [date_of_birth[0], date_of_birth[1], date_of_birth[2]]
		self.name_of_district_school_board = name_of_district_school_board
		self.district_school_board_number = district_school_board_number
		self.name_of_school = name_of_school
		self.school_number = school_number
		self.date_of_entry = [date_of_entry[0], date_of_entry[1], date_of_entry[2]]
		self.course_list = []
		self.community_involvement_flag = community_involvement_flag
		self.provincial_secondary_school_literacy_requirement_flag = provincial_secondary_school_literacy_requirement_flag
		self.specialized_program = specialized_program
		self.diploma_or_certificate = diploma_or_certificate
		self.diploma_or_certificate_date_of_issue = [diploma_or_certificate_date_of_issue[0], diploma_or_certificate_date_of_issue[1]]
		self.authorization = authorization
