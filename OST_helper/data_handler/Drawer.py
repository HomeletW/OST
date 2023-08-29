from PIL import ImageDraw, ImageFont

from OST_helper.data_handler import Course, OST_info, \
    SECONDARY_SCHOOL_ONLINE_LEARNING_REQUIREMENT_TRUE_TEXT, \
    SECONDARY_SCHOOL_ONLINE_LEARNING_REQUIREMENT_FALSE_TEXT, \
    SECONDARY_SCHOOL_ONLINE_LEARNING_REQUIREMENT_TITLE
from OST_helper.parameter import *

# alignment flag
flag_left = 0
flag_center = 1
flag_right = 2

WHITE_TRANSPARENT = (0, 0, 0, 0)
BLACK = (255, 255, 255, 255)

def draw(info: OST_info,
         draw_ost_template,
         draw_with_old_paper,
         offset=COORDINATES["Offset"],
         font=TFONT):
    course_images = draw_courses(courses=info.course(), font=font,
                                 font_size=info.course_font_size(),
                                 spacing=info.course_spacing())
    total_page = len(course_images)
    images = []
    for page_index in range(total_page):
        image = course_images[page_index]
        img = Image.new(mode="RGBA", size=COORDINATES["Size"],
                        color=WHITE_TRANSPARENT)
        drawer = ImageDraw.Draw(img)
        if draw_ost_template:
            template = OST_SAMPLE_IMAGE.copy() if draw_with_old_paper else OST_SAMPLE_2023_IMAGE.copy()
            draw_image(img, template, config=(0, 0), offset=(0, 0))
        # draw the courses
        course_x, course_y, _, _ = COORDINATES["Course"]
        draw_image(img, image, config=(course_x, course_y), offset=offset)
        # draw credit summary
        draw_text(drawer=drawer,
                  text=str(info.course_credit_summary()),
                  config=COORDINATES["SummaryOfCredit"],
                  font=font,
                  offset=offset,
                  alignment_flag=flag_center)
        # draw compulsory summary
        draw_text(drawer=drawer,
                  text=str(info.course_compulsory_summary()),
                  config=COORDINATES["SummaryOfCompulsory"],
                  font=font,
                  offset=offset,
                  alignment_flag=flag_center)
        # draw page number
        draw_text(drawer=drawer,
                  text=str(page_index + 1),
                  config=COORDINATES["Page_1"],
                  font=font,
                  offset=offset,
                  alignment_flag=flag_center)
        draw_text(drawer=drawer,
                  text=str(total_page),
                  config=COORDINATES["Page_2"],
                  font=font,
                  offset=offset,
                  alignment_flag=flag_center)
        # draw OST Date of Issue
        draw_text(drawer=drawer,
                  text=info.OST_date_of_issue(),
                  config=COORDINATES["OST_DateOfIssue"],
                  font=font,
                  offset=offset,
                  alignment_flag=flag_left)
        # draw Surname
        draw_text(drawer=drawer,
                  text=info.surname(),
                  config=COORDINATES["Surname"],
                  font=font,
                  offset=offset,
                  alignment_flag=flag_left)
        # draw Given Name
        draw_text(drawer=drawer,
                  text=info.given_name(),
                  config=COORDINATES["GivenName"],
                  font=font,
                  offset=offset,
                  alignment_flag=flag_left)
        # draw OEN
        draw_text(drawer=drawer,
                  text=info.OEN(),
                  config=COORDINATES["OEN"],
                  font=font,
                  offset=offset,
                  alignment_flag=flag_left)
        # draw student number
        draw_text(drawer=drawer,
                  text=info.student_number(),
                  config=COORDINATES["StudentNumber"],
                  font=font,
                  offset=offset,
                  alignment_flag=flag_left)
        # draw gender
        draw_text(drawer=drawer,
                  text=info.gender(),
                  config=COORDINATES["Gender"],
                  font=font,
                  offset=offset,
                  alignment_flag=flag_left)
        # draw date of birth year
        draw_text(drawer=drawer,
                  text=info.date_of_birth_y(),
                  config=COORDINATES["DateOfBirth_Y"],
                  font=font,
                  offset=offset,
                  alignment_flag=flag_left)
        # draw date of birth month
        draw_text(drawer=drawer,
                  text=info.date_of_birth_m(),
                  config=COORDINATES["DateOfBirth_M"],
                  font=font,
                  offset=offset,
                  alignment_flag=flag_left)
        # draw date of birth day
        draw_text(drawer=drawer,
                  text=info.date_of_birth_d(),
                  config=COORDINATES["DateOfBirth_D"],
                  font=font,
                  offset=offset,
                  alignment_flag=flag_left)
        # draw name of district school board
        draw_text(drawer=drawer,
                  text=info.name_of_district_school_board(),
                  config=COORDINATES["NameOfDSB"],
                  font=font,
                  offset=offset,
                  alignment_flag=flag_left)
        # draw number of district school board
        draw_text(drawer=drawer,
                  text=info.district_school_board_number(),
                  config=COORDINATES["NumberOfDSB"],
                  font=font,
                  offset=offset,
                  alignment_flag=flag_left)
        # draw name of school
        draw_text(drawer=drawer,
                  text=info.name_of_school(),
                  config=COORDINATES["NameOfSchool"],
                  font=font,
                  offset=offset,
                  alignment_flag=flag_left)
        # draw number of school
        draw_text(drawer=drawer,
                  text=info.school_number(),
                  config=COORDINATES["NumberOfSchool"],
                  font=font,
                  offset=offset,
                  alignment_flag=flag_left)
        # draw date of entry year
        draw_text(drawer=drawer,
                  text=info.date_of_entry_y(),
                  config=COORDINATES["DateOfEntry_Y"],
                  font=font,
                  offset=offset,
                  alignment_flag=flag_left)
        # draw date of entry month
        draw_text(drawer=drawer,
                  text=info.date_of_entry_m(),
                  config=COORDINATES["DateOfEntry_M"],
                  font=font,
                  offset=offset,
                  alignment_flag=flag_left)
        # draw date of entry day
        draw_text(drawer=drawer,
                  text=info.date_of_entry_d(),
                  config=COORDINATES["DateOfEntry_D"],
                  font=font,
                  offset=offset,
                  alignment_flag=flag_left)
        # draw specialized program
        specialized_program_offset = offset[0] + 10, offset[1]
        draw_text(drawer=drawer,
                  text=info.specialized_program(),
                  config=COORDINATES["SpecializedProgram"],
                  font=font,
                  offset=specialized_program_offset,
                  alignment_flag=flag_left)
        # draw diploma or certificate
        draw_text(drawer=drawer,
                  text=info.diploma_or_certificate(),
                  config=COORDINATES["DiplomaOrCertificate"],
                  font=font,
                  offset=offset,
                  alignment_flag=flag_left)
        # draw diploma or certificate date year
        draw_text(drawer=drawer,
                  text=info.diploma_or_certificate_date_of_issue_y(),
                  config=COORDINATES["DiplomaOrCertificate_DateOfIssue_Y"],
                  font=font,
                  offset=offset,
                  alignment_flag=flag_center)
        # draw date of birth month
        draw_text(drawer=drawer,
                  text=info.diploma_or_certificate_date_of_issue_m(),
                  config=COORDINATES["DiplomaOrCertificate_DateOfIssue_M"],
                  font=font,
                  offset=offset,
                  alignment_flag=flag_center)
        # draw authorization
        authorization_offset = offset[0] + 10, offset[1]
        draw_text(drawer=drawer,
                  text=info.authorization(),
                  config=COORDINATES["Authorization"],
                  font=font,
                  offset=authorization_offset,
                  alignment_flag=flag_left)
        if draw_with_old_paper:
            # draw community involvement
            draw_checkmark(img, condition=info.community_involvement(), 
                    true_config=COORDINATES["CommunityInvolvement_True_2023_oldversionpaper"], 
                    false_config=COORDINATES["CommunityInvolvement_False_2023_oldversionpaper"], 
                    offset=offset)
            # draw provincial secondary school literacy requirement
            draw_checkmark(img, condition=info.provincial_secondary_school_literacy_requirement(), 
                    true_config=COORDINATES["ProvincialSecondarySchoolLiteracy_True_2023_oldversionpaper"], 
                    false_config=COORDINATES["ProvincialSecondarySchoolLiteracy_False_2023_oldversionpaper"], 
                    offset=offset)
            # draw secondary school online learning requirement
            draw_checkmark(img, condition=info.secondary_school_online_learning_requirement(), 
                    true_config=COORDINATES["SecondarySchoolOnlineLearningRequirements_True_2023_oldversionpaper"], 
                    false_config=COORDINATES["SecondarySchoolOnlineLearningRequirements_False_2023_oldversionpaper"], 
                    offset=offset)
            # draw secondary school online learning requirement divider
            draw_line(drawer=drawer, 
                    config=COORDINATES["SecondarySchoolOnlineLearningRequirements_Divider_2023_oldversionpaper"],
                    offset=offset)
            # draw secondary school online learning requirement title
            draw_text(drawer=drawer,
                    text=SECONDARY_SCHOOL_ONLINE_LEARNING_REQUIREMENT_TITLE,
                    config=COORDINATES["SecondarySchoolOnlineLearningRequirements_Title_2023_oldversionpaper"],
                    font=font,
                    offset=offset,
                    alignment_flag=flag_left)
            # draw secondary school online learning requirement box
            draw_box(drawer, 
                    config=COORDINATES["SecondarySchoolOnlineLearningRequirements_TrueBox_2023_oldversionpaper"],
                    offset=offset)
            draw_box(drawer, 
                    config=COORDINATES["SecondarySchoolOnlineLearningRequirements_FalseBox_2023_oldversionpaper"],
                    offset=offset)
            # draw secondary school online learning requirement boxText    
            draw_text(drawer=drawer,
                    text=SECONDARY_SCHOOL_ONLINE_LEARNING_REQUIREMENT_TRUE_TEXT,
                    config=COORDINATES["SecondarySchoolOnlineLearningRequirements_TrueText_2023_oldversionpaper"],
                    font=font,
                    offset=offset,
                    alignment_flag=flag_left)  
            draw_text(drawer=drawer,
                    text=SECONDARY_SCHOOL_ONLINE_LEARNING_REQUIREMENT_FALSE_TEXT,
                    config=COORDINATES["SecondarySchoolOnlineLearningRequirements_FalseText_2023_oldversionpaper"],
                    font=font,
                    offset=offset,
                    alignment_flag=flag_left)
        else:
            # draw community involvement
            draw_checkmark(img, condition=info.community_involvement(), 
                    true_config=COORDINATES["CommunityInvolvement_True_2023"], 
                    false_config=COORDINATES["CommunityInvolvement_False_2023"], 
                    offset=offset)
            # draw provincial secondary school literacy requirement
            draw_checkmark(img, condition=info.provincial_secondary_school_literacy_requirement(), 
                    true_config=COORDINATES["ProvincialSecondarySchoolLiteracy_True_2023"], 
                    false_config=COORDINATES["ProvincialSecondarySchoolLiteracy_False_2023"], 
                    offset=offset)
            # draw secondary school online learning requirement
            draw_checkmark(img, condition=info.secondary_school_online_learning_requirement(), 
                    true_config=COORDINATES["SecondarySchoolOnlineLearningRequirements_True_2023"], 
                    false_config=COORDINATES["SecondarySchoolOnlineLearningRequirements_False_2023"], 
                    offset=offset)
        # save the image
        image_name = info.get_file_name(
            sub=str(page_index + 1) if total_page > 1 else "",
            file_type=".png"
        )
        images.append((img, image_name))
    return images, info.get_file_name()


def draw_checkmark(img, condition, true_config, false_config, offset):
    if condition:
        draw_image(img, OST_CHECKMARK_IMAGE, true_config, offset=offset)
    else:
        draw_image(img, OST_CHECKMARK_IMAGE, false_config, offset=offset)


def draw_box(drawer, config, offset):
    offset_x, offset_y = offset
    box_x, box_y, box_width, box_height, line_width = config
    x, y = box_x + offset_x, box_y + offset_y
    drawer.rectangle(xy=(x, y, x + box_width, y + box_height),
                     outline="black", width=line_width)


def draw_line(drawer, config, offset):
    offset_x, offset_y = offset
    x1, y1, x2, y2, line_width = config
    drawer.line(xy=(x1 + offset_x, y1 + offset_y, x2 + offset_x, y2 + offset_y), 
                fill="black", 
                width=line_width)


def draw_text(drawer, text, config, font, offset, alignment_flag=flag_left):
    # get the final position of the text and apply the alignment
    offset_x, offset_y = offset
    box_x, box_y, box_width, box_height, font_size = config
    x = offset_x + box_x
    font = ImageFont.truetype(font, size=font_size) if isinstance(font,
                                                                  str) else font
    # determine how long the text is going to be and apply the alignment flag
    left, top, right, bottom = drawer.textbbox((0,0), text, font=font)
    width, height = right, bottom
    if alignment_flag == flag_right:
        x = x + box_width - width
    elif alignment_flag == flag_center:
        x = x + box_width / 2 - width / 2
    else:
        x = x
    y = offset_y + box_y + box_height // 2 - height // 2
    # drawer.rectangle(xy=(box_x, box_y, box_x + box_width, box_y + box_height), outline="black", width=1)
    drawer.text(xy=(x, y), text=text, font=font, fill="black")


def draw_image(img, image, config, offset):
    x, y = config
    x += offset[0]
    y += offset[1]
    img.paste(image, (x, y), image)


def draw_courses(courses, font, font_size, spacing):
    # get the info needed to draw courses
    _, _, course_width, course_height = COORDINATES["Course"]
    date_x, date_width = COORDINATES["Course_date_offset"]
    level_x, level_width = COORDINATES["Course_level_offset"]
    title_x, title_width = COORDINATES["Course_title_offset"]
    code_x, code_width = COORDINATES["Course_code_offset"]
    percentage_x, percentage_width = COORDINATES["Course_percentage_offset"]
    credit_x, credit_width = COORDINATES["Course_credit_offset"]
    compulsory_x, compulsory_width = COORDINATES["Course_compulsory_offset"]
    note_x, note_width = COORDINATES["Course_note_offset"]
    font = ImageFont.truetype(font, size=font_size)
    # draw the courses on a new image
    # to make sure there are at least one image
    img = Image.new(mode="RGBA", size=(course_width, course_height),
                    color=WHITE_TRANSPARENT)
    img_drawer = ImageDraw.Draw(img)
    images = [img]

    def get_height(course):
        # get the maximum height in line
        left, top, right, bot = font.getbbox(" ".join(course.get()))
        return bot

    def draw_course(drawer, course: Course, height, y):
        # draw date
        draw_text(drawer=drawer,
                  text=course.date,
                  config=(date_x, y, date_width, height, 0),
                  font=font,
                  offset=(0, 0),
                  alignment_flag=flag_center)
        # draw level
        draw_text(drawer=drawer,
                  text=course.level,
                  config=(level_x, y, level_width, height, 0),
                  font=font,
                  offset=(0, 0),
                  alignment_flag=flag_center)
        # draw title
        draw_text(drawer=drawer,
                  text=course.title,
                  config=(title_x, y, title_width, height, 0),
                  font=font,
                  offset=(10, 0),
                  alignment_flag=flag_left)
        # draw code
        draw_text(drawer=drawer,
                  text=course.code,
                  config=(code_x, y, code_width, height, 0),
                  font=font,
                  offset=(0, 0),
                  alignment_flag=flag_center)
        # draw percentage
        draw_text(drawer=drawer,
                  text=course.percentage,
                  config=(percentage_x, y, percentage_width, height, 0),
                  font=font,
                  offset=(0, 0),
                  alignment_flag=flag_center)
        # draw credit
        draw_text(drawer=drawer,
                  text=course.credit,
                  config=(credit_x, y, credit_width, height, 0),
                  font=font,
                  offset=(0, 0),
                  alignment_flag=flag_center)
        # draw compulsory
        draw_text(drawer=drawer,
                  text=course.compulsory,
                  config=(compulsory_x, y, compulsory_width, height, 0),
                  font=font,
                  offset=(0, 0),
                  alignment_flag=flag_center)
        # draw note
        draw_text(drawer=drawer,
                  text=course.note,
                  config=(note_x, y, note_width, height, 0),
                  font=font,
                  offset=(0, 0),
                  alignment_flag=flag_center)

    accum_y = spacing
    for c in courses:
        # if the height exceed the limit then proceed to next page
        c_height = get_height(c)
        unit_height = c_height + spacing
        if accum_y + unit_height > course_height:
            new_img = Image.new(mode="RGBA", size=(course_width, course_height),
                                color=(0, 0, 0, 0))
            new_img_drawer = ImageDraw.Draw(new_img)
            images.append(new_img)
            # img = new_img
            img_drawer = new_img_drawer
            accum_y = spacing
        draw_course(img_drawer, c, c_height, accum_y)
        accum_y += unit_height
    return images
