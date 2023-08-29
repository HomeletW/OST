from OST_helper.parameter import finalize, initialize
from platformdirs import user_data_dir

APP_NAME = "OST_Helper"
PATCH = "2.1"

import os
DEBUG_MODE = bool(os.environ.get('OST_HELPER_DEBUG', False))

def main():
    from os.path import abspath, join, realpath, dirname
    from sys import argv
    
    if DEBUG_MODE:
        print("DEBUG MODE ACTIVE")

    local_dir = dirname(argv[0])
    user_dir = user_data_dir(appname=APP_NAME)
    
    resource_path = abspath(join(local_dir, "resource"))

    if DEBUG_MODE:
        shared_path = abspath(join(local_dir, "shared_data"))
    else:
        shared_path = abspath(join(user_dir, "shared_data"))

    # make sure the shared_path exists
    os.makedirs(shared_path, exist_ok=True)

    initialize(resource_path, shared_path)
    
    from OST_helper.UI.UI import Application
    application = Application()
    application.run()
    
    finalize()


if __name__ == '__main__':
    main()
