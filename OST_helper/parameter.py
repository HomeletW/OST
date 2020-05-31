# constant
import json
import logging
import os
import platform
from datetime import date
from os.path import expanduser, isdir, isfile, join

from PIL import Image

logging.basicConfig(
    style="{",
    format="{threadName:<10s} <{levelname:<7s}> [{asctime:<15s}] {message}",
    level=logging.DEBUG
)

# paths
CCCL_PATH = "./resource/default_cccl.json"
SETTING_PATH = "./resource/setting.json"
MCCANNY_LOGO = "./resource/mccanny_logo.ico"
OST_SAMPLE = "./resource/ost_sample.png"
DEFAULT_OST_PATH = "./resource/default_ost.json"
TFONT = "./resource/times-new-roman.ttf"
DEFAULT_COORDINATES_PATH = "./resource/default_coordinates.json"

# os
DEVICE_OS = platform.system()

# ost sample
OST_SAMPLE_IMAGE = Image.open(OST_SAMPLE)

# today
today = None

PRODUCTION_SUCCESS = 0
PRODUCTION_FILE_EXISTS = 1
PRODUCTION_FILE_NOT_RECOGNIZED = 2


def from_json(path):
    with open(path, "r") as js:
        data = json.load(js)
    return data


def to_json(path, data):
    with open(path, "w+") as js:
        json.dump(data, js, indent=4)


def update_today():
    global today
    day = date.today()
    year, month, day = day.year, day.month, day.day
    today = str(year), str(month), str(day)


def get_desktop_directory():
    if DEVICE_OS in ["Linux", "Darwin"]:
        home_dir = join(expanduser("~"), "Desktop")
    elif DEVICE_OS in ["Windows"]:
        home_dir = join(os.environ["USERPROFILE"], "Desktop")
    else:
        home_dir = None
    if home_dir is not None and isdir(home_dir):
        return home_dir
    else:
        return "/"


DEFAULT_DIR = get_desktop_directory()

# "course_code": ["course_title", "course_level", "credit", "compulsory"]
default_common_course_code_library = {

}
default_setting = {
    "draw_ost_template": True,
    "smart_fill": True,
    "train": True,
    "json_dir": DEFAULT_DIR,
    "img_dir": DEFAULT_DIR,
    "last_session": None,
}
default_ost = {
    "OST_date_of_issue": today,
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
default_coordinates = {
    "Size": (3300, 2532),
    "Offset": (0, 0),
    # (x, y, width, height)
    "OST_DateOfIssue": (2309, 91, 508, 89, 55),
    "Page_1": (2822, 91, 177, 89, 50),
    "Page_2": (3031, 91, 177, 89, 50),
    "Surname": (164, 221, 619, 89, 50),
    "GivenName": (783, 221, 755, 89, 50),
    "OEN": (1538, 221, 518, 89, 50),
    "StudentNumber": (2056, 221, 524, 89, 50),
    "Gender": (2580, 221, 134, 89, 50),
    "DateOfBirth_Y": (2714, 248, 195, 62, 40),
    "DateOfBirth_M": (2909, 248, 196, 62, 40),
    "DateOfBirth_D": (3105, 248, 139, 62, 40),
    "NameOfDSB": (148, 352, 1009, 93, 50),
    "NumberOfDSB": (1157, 352, 381, 93, 50),
    "NameOfSchool": (1538, 352, 789, 93, 50),
    "NumberOfSchool": (2327, 352, 387, 93, 50),
    "DateOfEntry_Y": (2714, 378, 195, 67, 40),
    "DateOfEntry_M": (2909, 378, 196, 67, 40),
    "DateOfEntry_D": (3105, 378, 139, 67, 40),
    # (x, y, width, height)
    "Course": (111, 572, 3134, 1363),
    # (x_offset, width)
    "Course_date_offset": (0, 261),
    "Course_level_offset": (264, 177),
    "Course_title_offset": (444, 1589),
    "Course_code_offset": (2036, 236),
    "Course_percentage_offset": (2275, 171),
    "Course_credit_offset": (2452, 180),
    "Course_compulsory_offset": (2635, 201),
    "Course_note_offset": (2842, 292),
    "SummaryOfCredit": (2567, 1941, 176, 66, 55),
    "SummaryOfCompulsory": (2746, 1941, 201, 66, 55),
    "CommunityInvolvement_True": (148, 2068),
    "CommunityInvolvement_False": (449, 2068),
    "ProvincialSecondarySchoolLiteracy_True": (680, 2068),
    "ProvincialSecondarySchoolLiteracy_False": (1215, 2068),
    "SpecializedProgram": (1494, 2049, 1750, 89, 40),
    "DiplomaOrCertificate": (129, 2187, 1578, 64, 40),
    "DiplomaOrCertificate_DateOfIssue_Y": (1734, 2213, 168, 52, 40),
    "DiplomaOrCertificate_DateOfIssue_M": (1911, 2213, 168, 52, 40),
    "Authorization": (2106, 2180, 1092, 85, 40),
}

COMMON_COURSE_CODE_LIBRARY = None
SETTING = None
DEFAULT_OST_INFO = None
COORDINATES = None


def finalize():
    logger = logging.getLogger()
    # save CCCL
    to_json(CCCL_PATH, COMMON_COURSE_CODE_LIBRARY)
    logger.info("Common Course Code Library saved!")
    # save setting
    to_json(SETTING_PATH, SETTING)
    logger.info("Setting saved!")


def initialize():
    global COMMON_COURSE_CODE_LIBRARY
    global SETTING
    global DEFAULT_OST_INFO
    global COORDINATES
    logger = logging.getLogger()
    # update today
    update_today()
    # initialize CCCL
    try:
        COMMON_COURSE_CODE_LIBRARY = from_json(CCCL_PATH)
        logger.info(f"Loaded CCCL [{len(COMMON_COURSE_CODE_LIBRARY)} courses]!")
    except Exception:
        COMMON_COURSE_CODE_LIBRARY = default_common_course_code_library
        logger.warning("No CCCL found, restoring from default...")
    # initialize settings
    try:
        SETTING = from_json(SETTING_PATH)
        if not isdir(SETTING["json_dir"]):
            SETTING["json_dir"] = DEFAULT_DIR
            logger.warning("json dir no longer is dir, resetting to default")
        if not isdir(SETTING["img_dir"]):
            SETTING["img_dir"] = DEFAULT_DIR
            logger.warning("image dir no longer is dir, resetting to default")
        if SETTING["last_session"] is not None and not isfile(
                SETTING["last_session"]):
            SETTING["last_session"] = None
            logger.warning(
                "last session ost file no longer exist, resetting to default")
        logger.info("Loaded setting!")
    except Exception:
        SETTING = default_setting
        logger.info("No setting found, restoring from default...")
    # initialize OST
    from OST_helper.data_handler.Data import OST_info
    try:
        DEFAULT_OST_INFO = OST_info.from_json(DEFAULT_OST_PATH)
        DEFAULT_OST_INFO.update_date_of_issue(today)
        logger.info("Loaded ost!")
    except Exception:
        DEFAULT_OST_INFO = OST_info.from_data(default_ost)
        logger.warning("No default OST info found, using default...")
    # initialize coordinate
    try:
        COORDINATES = from_json(DEFAULT_COORDINATES_PATH)
        logger.info("Loaded coordinates!")
    except Exception:
        COORDINATES = default_coordinates
        logger.warning("No default coordinates found, using default...")
