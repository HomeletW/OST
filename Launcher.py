from OST_helper.parameter import finalize, initialize
from platformdirs import user_data_dir

APP_NAME = "OST_Helper"
PATCH = "2.1"

import os
DEBUG_MODE = bool(os.environ.get('OST_HELPER_DEBUG', False))
USE_LOCAL_DIR = DEBUG_MODE

def main():
    from os.path import abspath, join, realpath, dirname
    from sys import argv
    
    if DEBUG_MODE:
        print("DEBUG MODE ACTIVE")
    
    if USE_LOCAL_DIR:
        local_dir = dirname(argv[0])
        resource_path = abspath(join(local_dir, "resource"))
        shared_path = abspath(join(local_dir, "shared_resource"))
    else:
        major_version = PATCH.split('.')[0]
        user_dir = user_data_dir(appname=APP_NAME)
        resource_path = abspath(join(user_dir, f"V{major_version}", "resource"))
        shared_path = abspath(join(user_dir, "shared_resource"))

    initialize(resource_path, shared_path)
    
    from OST_helper.UI.UI import Application
    application = Application()
    application.run()
    
    finalize()


if __name__ == '__main__':
    main()
