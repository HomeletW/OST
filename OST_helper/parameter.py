# constant
import json
import logging
import os
import platform
import subprocess
from datetime import date
from os.path import exists, expanduser, isdir, isfile, join, abspath, dirname

from PIL import Image

logging.basicConfig(
    style="{",
    format="{threadName:<10s} <{levelname:<7s}> [{asctime:<15s}] {message}",
    level=logging.DEBUG
)


# paths
CCCL_PATH = None
SETTING_PATH = None
APP_LOGO = None
OST_SAMPLE = None
DEFAULT_OST_PATH = None
TFONT = None
DEFAULT_COORDINATES_PATH = None

# os
DEVICE_OS = platform.system()

# ost sample
OST_SAMPLE_IMAGE = None

# today
today = None

PRODUCTION_SUCCESS = 0
PRODUCTION_FILE_EXISTS = 1
PRODUCTION_FILE_NOT_RECOGNIZED = 2


def update_today():
    global today
    day = date.today()
    year, month, day = day.year, day.month, day.day
    today = str(year), str(month), str(day)


update_today()


def from_json(path):
    with open(path, "r") as js:
        data = json.load(js)
    return data


def to_json(path, data):
    with open(path, "w+") as js:
        json.dump(data, js, indent=4)


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


def open_path(abs_path):
    if not exists(abs_path):
        raise ValueError("Path Not Exist!")
    if DEVICE_OS in ["Darwin"]:
        subprocess.Popen(["open", "-R", "{}".format(abs_path)])
    elif DEVICE_OS in ["Windows"]:
        subprocess.Popen('cmd /c start "START" "{}"'.format(abs_path))
    elif DEVICE_OS in ["Linux"]:
        subprocess.Popen(["nautilus", "--browser", "{}".format(abs_path)])
    else:
        raise Exception(
            "Not Supported Operating System [{}]!".format(DEVICE_OS))


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
    "name_of_school": "",
    "school_number": "",
    "date_of_entry": ["", "", ""],
    "community_involvement_flag": False,
    "provincial_secondary_school_literacy_requirement_flag": False,
    "specialized_program": "",
    "diploma_or_certificate": "Ontario Secondary School Diploma",
    "diploma_or_certificate_date_of_issue": ["", ""],
    "authorization": "",
    "course_list": [],
    "course_font_size": 50,
    "course_spacing": 5,
}
default_coordinates = {
    "Size": (3300, 2532),
    "Offset": (0, 0),
    # (x, y, width, height)
    "OST_DateOfIssue": (2301, 73, 532, 85, 55),
    "Page_1": (2826, 73, 183, 85, 50),
    "Page_2": (3046, 73, 183, 85, 50),
    "Surname": (85, 204, 645, 94, 50),
    "GivenName": (730, 204, 772, 94, 50),
    "OEN": (1502, 204, 537, 94, 50),
    "StudentNumber": (2039, 204, 538, 94, 50),
    "Gender": (2577, 204, 136, 94, 50),
    "DateOfBirth_Y": (2713, 228, 202, 70, 40),
    "DateOfBirth_M": (2915, 228, 202, 70, 40),
    "DateOfBirth_D": (3117, 228, 147, 70, 40),
    "NameOfDSB": (85, 336, 1023, 100, 50),
    "NumberOfDSB": (1108, 338, 397, 100, 50),
    "NameOfSchool": (1505, 338, 807, 100, 50),
    "NumberOfSchool": (2311, 338, 402, 100, 50),
    "DateOfEntry_Y": (2713, 368, 202, 70, 40),
    "DateOfEntry_M": (2915, 368, 202, 70, 40),
    "DateOfEntry_D": (3117, 368, 147, 70, 40),
    # (x, y, width, height)
    "Course": (35, 564, 3230, 1419),
    # (x_offset, width)
    "Course_date_offset": (35 - 35, 268),
    "Course_level_offset": (306 - 35, 183),
    "Course_title_offset": (491 - 35, 1637),
    "Course_code_offset": (2131 - 35, 244),
    "Course_percentage_offset": (2378 - 35, 175),
    "Course_credit_offset": (2563 - 35, 183),
    "Course_compulsory_offset": (2748 - 35, 207),
    "Course_note_offset": (2965 - 35, 299),
    "SummaryOfCredit": (2562, 1992, 184, 69, 55),
    "SummaryOfCompulsory": (2748, 1992, 207, 69, 55),
    "CommunityInvolvement_True": (75, 2125),
    "CommunityInvolvement_False": (385, 2125),
    "ProvincialSecondarySchoolLiteracy_True": (623, 2125),
    "ProvincialSecondarySchoolLiteracy_False": (1173, 2125),
    "SpecializedProgram": (1436, 2104, 1828, 96, 40),
    "DiplomaOrCertificate": (77, 2240, 1622, 90, 40),
    "DiplomaOrCertificate_DateOfIssue_Y": (1702, 2273, 180, 57, 40),
    "DiplomaOrCertificate_DateOfIssue_M": (1885, 2273, 180, 57, 40),
    "Authorization": (2070, 2240, 1148, 90, 40),
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


def initialize(resource_path):
    global COMMON_COURSE_CODE_LIBRARY
    global SETTING
    global DEFAULT_OST_INFO
    global COORDINATES

    global CCCL_PATH
    global SETTING_PATH
    global APP_LOGO
    global OST_SAMPLE
    global DEFAULT_OST_PATH
    global TFONT
    global DEFAULT_COORDINATES_PATH

    global OST_SAMPLE_IMAGE

    CCCL_PATH = join(resource_path, "CCCL.json")
    SETTING_PATH = join(resource_path, "setting.json")
    APP_LOGO = join(resource_path, "logo.ico")
    OST_SAMPLE = join(resource_path, "ost_sample.png")
    DEFAULT_OST_PATH = join(resource_path, "default_ost.json")
    TFONT = join(resource_path, "font.ttf")
    DEFAULT_COORDINATES_PATH = join(resource_path, "default_coordinates.json")

    OST_SAMPLE_IMAGE = Image.open(OST_SAMPLE)

    logger = logging.getLogger()
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
