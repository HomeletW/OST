import Main
from PIL import Image, ImageDraw
from typing import *


coordinates = {
	"Size": (0, 0),
	"Offset": (0, 0),
	"OST_DateOfIssue": (0, 0, 0, 0, 10),
	"Page_1": (0, 0, 0, 0, 10),
	"Page_2": (0, 0, 0, 0, 10),
	"Surname": (0, 0, 0, 0, 10),
	"GivenName": (0, 0, 0, 0, 10),
	"OEN": (0, 0, 0, 0, 10),
	"StudentNumber": (0, 0, 0, 0, 10),
	"Gender": (0, 0, 0, 0, 10),
	"DateOfBirth_Y": (0, 0, 0, 0, 10),
	"DateOfBirth_M": (0, 0, 0, 0, 10),
	"DateOfBirth_D": (0, 0, 0, 0, 10),
	"NameOfDSB": (0, 0, 0, 0, 10),
	"NumberOfDSB": (0, 0, 0, 0, 10),
	"NameOfSchool": (0, 0, 0, 0, 10),
	"NumberOfSchool": (0, 0, 0, 0, 10),
	"DateOfEntry_Y": (0, 0, 0, 0, 10),
	"DateOfEntry_M": (0, 0, 0, 0, 10),
	"DateOfEntry_D": (0, 0, 0, 0, 10),
	# (x, y, width, height)
	"Course": (0, 0, 0, 0),
	# (x_offset, width)
	"Course_date_offset": (0, 0),
	"Course_level_offset": (0, 0),
	"Course_title_offset": (0, 0),
	"Course_code_offset": (0, 0),
	"Course_percentage_offset": (0, 0),
	"Course_credit_offset": (0, 0),
	"Course_compulsory_offset": (0, 0),
	"Course_note_offset": (0, 0),
	"SummaryOfCredit": (0, 0, 0, 0, 10),
	"SummaryOfCompulsory": (0, 0, 0, 0, 10),
	"CommunityInvolvement_True": (0, 0),
	"CommunityInvolvement_False": (0, 0),
	"ProvincialSecondarySchoolLiteracy_True": (0, 0),
	"ProvincialSecondarySchoolLiteracy_False": (0, 0),
	"SpecializedProgram": (0, 0, 0, 0, 10),
	"DiplomaOrCertificate": (0, 0, 0, 0, 10),
	"DiplomaOrCertificate_DateOfIssue_Y": (0, 0, 0, 0, 10),
	"DiplomaOrCertificate_DateOfIssue_M": (0, 0, 0, 0, 10),
	"Authorization": (0, 0, 0, 0, 10),
}

# alignment flag
flag_left = 0
flag_center = 1
flag_right = 2


def draw(info: Main.OST_info, font):
	img = Image.new(mode="LA", size=coordinates["Size"])
	drawer = ImageDraw.Draw(img)
	# draw the courses
	# draw OST Date of Issue
	draw_text(drawer=drawer,
	          text=info.OST_date_of_issue(),
	          config=coordinates["OST_DateOfIssue"],
	          font=font,
	          alignment_flag=flag_left)
	# draw Surname
	draw_text(drawer=drawer,
	          text=info.surname(),
	          config=coordinates["Surname"],
	          font=font,
	          alignment_flag=flag_left)
	# draw Given Name
	draw_text(drawer=drawer,
	          text=info.given_name(),
	          config=coordinates["GivenName"],
	          font=font,
	          alignment_flag=flag_left)
	# draw OEN
	draw_text(drawer=drawer,
	          text=info.OEN(),
	          config=coordinates["OEN"],
	          font=font,
	          alignment_flag=flag_left)
	# draw student number
	draw_text(drawer=drawer,
	          text=info.student_number(),
	          config=coordinates["StudentNumber"],
	          font=font,
	          alignment_flag=flag_left)
	# draw gender
	draw_text(drawer=drawer,
	          text=info.gender(),
	          config=coordinates["Gender"],
	          font=font,
	          alignment_flag=flag_left)
	# draw date of birth year
	draw_text(drawer=drawer,
	          text=info.date_of_birth_y(),
	          config=coordinates["DateOfBirth_Y"],
	          font=font,
	          alignment_flag=flag_left)
	# draw date of birth month
	draw_text(drawer=drawer,
	          text=info.date_of_birth_m(),
	          config=coordinates["DateOfBirth_M"],
	          font=font,
	          alignment_flag=flag_left)
	# draw date of birth day
	draw_text(drawer=drawer,
	          text=info.date_of_birth_d(),
	          config=coordinates["DateOfBirth_D"],
	          font=font,
	          alignment_flag=flag_left)
	# draw name of district school board
	draw_text(drawer=drawer,
	          text=info.name_of_district_school_board(),
	          config=coordinates["NameOfDSB"],
	          font=font,
	          alignment_flag=flag_left)
	# draw number of district school board
	draw_text(drawer=drawer,
	          text=info.district_school_board_number(),
	          config=coordinates["NumberOfDSB"],
	          font=font,
	          alignment_flag=flag_left)
	# draw name of school
	draw_text(drawer=drawer,
	          text=info.name_of_school(),
	          config=coordinates["NameOfSchool"],
	          font=font,
	          alignment_flag=flag_left)
	# draw number of school
	draw_text(drawer=drawer,
	          text=info.school_number(),
	          config=coordinates["NumberOfSchool"],
	          font=font,
	          alignment_flag=flag_left)
	# draw date of entry year
	draw_text(drawer=drawer,
	          text=info.date_of_entry_y(),
	          config=coordinates["DateOfEntry_Y"],
	          font=font,
	          alignment_flag=flag_left)
	# draw date of entry month
	draw_text(drawer=drawer,
	          text=info.date_of_entry_m(),
	          config=coordinates["DateOfEntry_M"],
	          font=font,
	          alignment_flag=flag_left)
	# draw date of entry day
	draw_text(drawer=drawer,
	          text=info.date_of_entry_d(),
	          config=coordinates["DateOfEntry_D"],
	          font=font,
	          alignment_flag=flag_left)
	# draw specialized program
	draw_text(drawer=drawer,
	          text=info.specialized_program(),
	          config=coordinates["SpecializedProgram"],
	          font=font,
	          alignment_flag=flag_left)
	# draw diploma or certificate
	draw_text(drawer=drawer,
	          text=info.diploma_or_certificate(),
	          config=coordinates["DiplomaOrCertificate"],
	          font=font,
	          alignment_flag=flag_left)
	# draw diploma or certificate date year
	draw_text(drawer=drawer,
	          text=info.diploma_or_certificate_date_of_issue_y(),
	          config=coordinates["DiplomaOrCertificate_DateOfIssue_Y"],
	          font=font,
	          alignment_flag=flag_center)
	# draw date of birth month
	draw_text(drawer=drawer,
	          text=info.diploma_or_certificate_date_of_issue_m(),
	          config=coordinates["DiplomaOrCertificate_DateOfIssue_M"],
	          font=font,
	          alignment_flag=flag_center)
	# draw authorization
	draw_text(drawer=drawer,
	          text=info.authorization(),
	          config=coordinates["Authorization"],
	          font=font,
	          alignment_flag=flag_left)
	# save the image
	img.save(info.full_name() + " OST.png")


def draw_text(drawer, text, config: List[int, int, int, int, int], font, offset=coordinates["Offset"], alignment_flag=flag_left):
	# determine how long the text is going to be and apply the alignment flag
	width, height = drawer.textsize(text=text, font=font, spacing=0)
	# get the final position of the text and apply the alignment
	offset_x, offset_y = offset
	box_x, box_y, box_width, box_height, text_size = config
	x = offset_x + box_x
	if alignment_flag is flag_right:
		x = x + box_width - width
	elif alignment_flag is flag_center:
		x = x + box_width / 2 - width / 2
	else:
		x = x
	y = offset_y + box_y + box_height / 2 - height / 2
	drawer.text(xy=(x, y), text=text)


def plan_courses(drawer, courses: List[Main.Course], font, font_size, spacing):
	# plan the font
	course_x, course_y, course_width, course_height = coordinates["Course"]
	offset_x, offset_y = coordinates["Offset"]
	course_x += offset_x
	course_y += offset_y
	# get the height of the font
	_, test_height = drawer.textsize(text="ABCD", font=font, spacing=0)
	# minus the spacing from the top
	avaliHeight = course_height - spacing
	# calculate how much space does the course takes
	unit_height = test_height + spacing
	total_height = unit_height * len(courses)
	# calculate how many page does it takes
	pages, reminder = int(total_height // avaliHeight), total_height % avaliHeight
	if reminder > spacing:
		pages += 1
