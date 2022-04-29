from OST_helper.parameter import finalize, initialize

PATCH = "1.2"


def main():
    from os.path import abspath, join, dirname
    resource_path = abspath(join(dirname(__file__), "resource"))
    initialize(resource_path)
    from OST_helper.UI.UI import Application
    application = Application()
    application.run()
    finalize()


if __name__ == '__main__':
    main()
