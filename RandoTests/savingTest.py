import pickle
import os
import datetime

class savingTest:

	cwd = os.getcwd()
	savd_dir = cwd + "/saving_data/tester"

	keywords = {"saved": False}
	saved = "saved"
	master = {}

	def __init__(self):
		self.name = "SAVE"

	def check_save(self):
		self.loading()
		print(self.keywords[self.saved])
		print(str(self.master["11/24"]))
		self.keywords[self.saved] = False
		print(str(self.master["11/24"]))
		print(self.keywords[self.saved])

	def storing(self):
		self.master["11/24"] = self.keywords
		self.keywords[self.saved] = True
		with open(self.savd_dir, "wb") as saving_file:
			pickle.dump(self.keywords, saving_file)
			pickle.dump(self.master, saving_file)

	def loading(self):
		try:
			with open(self.savd_dir, "rb") as saving_file:
				self.keywords = pickle.load(saving_file)
				self.master = pickle.load(saving_file)
		except FileNotFoundError:
			print("NOT SAVED YET")

x = datetime.datetime.now()
test = {}
test[x.strftime("%m/%d/%Y")] = savingTest()
print(test)
print(test["05/16/22"])

