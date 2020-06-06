from OST_helper.parameter import finalize, initialize

PATCH = "1.1"


def main():
    initialize()
    from OST_helper.UI.UI import Application
    application = Application()
    application.run()
    finalize()


if __name__ == '__main__':
    main()
