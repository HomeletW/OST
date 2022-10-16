from OST_helper.parameter import finalize, initialize

PATCH = "1.3"


def main():
    from os.path import abspath, join, realpath, dirname
    from sys import argv
    resource_path = abspath(join(dirname(argv[0]), "resource"))
    print(resource_path)
    initialize(resource_path)
    from OST_helper.UI.UI import Application
    application = Application()
    application.run()
    finalize()


if __name__ == '__main__':
    main()
