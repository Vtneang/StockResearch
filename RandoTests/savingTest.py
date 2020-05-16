import pickle
import os

class savingTest:

	cwd = os.getcwd()
	savd_dir = cwd + "/saving_data/tester"

	keywords = {"saved": False}
	saved = "saved"
	idk = [1,2,3,4]

	def __init__(self):
		self.loading()
		self.name = "SAVE"

	def check_save(self):
		print(self.keywords[self.saved])
		print(str(self.idk))

	def storing(self):
		self.keywords[self.saved] = True
		self.idk[1] = 8
		with open(self.savd_dir, "wb") as saving_file:
			pickle.dump(self.keywords, saving_file)
			pickle.dump(self.idk, saving_file)

	def loading(self):
		try:
			with open(self.savd_dir, "rb") as saving_file:
				self.keywords = pickle.load(saving_file)
				self.idk = pickle.load(saving_file)
		except FileNotFoundError:
			print("NOT SAVED YET")



test_1 = savingTest()
test_1.check_save()
