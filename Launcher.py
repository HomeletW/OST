import json


def from_json(path):
	with open(path, "r") as js:
		data = json.load(js)
	return data


def to_json(path, data):
	with open(path, "w+") as js:
		json.dump(data, js, indent=4)


import Data
import Drawer
import UI


def main():
	main = UI.Main()
	main.run()
	Data.finalize()
	Drawer.finalize()
	UI.finalize()


if __name__ == '__main__':
	try:
		main()
	except Exception as expc:
		print(str(expc))
