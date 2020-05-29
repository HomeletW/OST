import json


def from_json(path):
    with open(path, "r") as js:
        data = json.load(js)
    return data


def to_json(path, data):
    with open(path, "w+") as js:
        json.dump(data, js, indent=4)


PATCH = "1.0"


def main():
    from OST_helper.UI import Application
    application = Application()
    application.run()


if __name__ == '__main__':
    main()
