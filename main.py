from stuff import stock
import urllib.request
import requests
from bs4 import BeautifulSoup
import re
import pickle
from datapackage import Package 
import os

class main:

	# Stock package
	package = Package('https://datahub.io/core/nyse-other-listings/datapackage.json')
	names = []

	# YAHOO SEARCH LINKS TO HELP FOR SEARCHING!
	link_begin = "https://finance.yahoo.com/quote/"
	link_ending = "?ltr=1"
	stock_data_access = "My(6px) Pos(r) smartphone_Mt(6px)"
	stock_name_access = "Mt(15px)"
	stock_float_pattern = "[-+]?\d*\.?\d*%?$"
	stock_time_pattern = "\d+:\d*"+ "(AM|PM)$"

	# LIST OF COMMANDS
	commands = ["add", "check","listings", "update", "help", "exit"]

	Stocks = {} # Main dictionary of all stocks
	data_gathered = False # Seeing if the data is put into the dictionary yet
	active = True # Change to True for wanting input on system

	# Saving directories/file names
	storing_dir = os.getcwd() + "/saved_data/"
	stocks_saved = storing_dir + "Stocks"
	other_saved = storing_dir + "Other"

	# Initializer of the main class
	def __init__(self):
		self.name = "AllStocks"
		self.loading()
		while self.active:
			action = input("WHAT U WANT? ")
			self.action_checker(action)
	# Repr of main
	def __repr__(self):
		return "The totally MAssive data class"

	# Str of main
	def __str__(self):
		return "Printing data of myself?"

	##### HELPER FUNCTIONS #####

	# Get name thru the abbrv link RETURNS a STRING(NAME)
	def get_name(soup):
		try:
			title = soup.find("div", {"class" : self.stock_name_access}).find_all("h1")
		except AttributeError:
			return ""
		name = ""
		for i in title:
			for j in i.text.split():
				if re.match("[A-Z]{1}[a-z]+", j):
					name += j + " "
		return name.strip()

	# Get's the updated info of a stock by the soup content
	# RETURNS A LIST: [PRICE, VALUE CHANGE, PERECENT CHANGE, TIME]
	def get_data(soup):
		try:
			trial = soup.find("div", {"class" : self.stock_data_access}).find_all("span")
		except AttributeError:
			return "fail"
		count = 0
		results = []
		for i in trial:
			for j in i.text.split():
				j = re.sub("[(,)]", "", j)
				if count < 4 and (re.match(self.stock_float_pattern, j) or re.match(self.stock_time_pattern, j)): #Set to 4 so I don't get Pre/Post Market
					count += 1
					results.append(j)
		return results

	def action_checker(self, action):
		if action in self.commands:
			if action == "exit":
				self.storing()
				exit()
			elif action == "update":
				self.update()
			elif action == "help":
				self.help()
			elif action == "listings":
				print(str(self.listings()))
			elif action == "add":
				cur = input("Please enter the desired stock symbol: ")
				self.add_by_abbrv(cur)
			elif action == "check":
				cur = input("Please enter the desired stock symbol: ")
				keys = self.listings()
				if cur not in keys:
					reply = "Sorry that stock isn't available in the system yet!" + "\n"
					reply += "Here's the available stock symbol's: " + str(keys)
					print(reply)
					self.action_checker(action)
				else:
					self.check_stock(cur)
		else:
			print(action + " is invalid. Please enter another one!")

	##### ADDING/STORING DATA #####

	# Might add one for name of stock sooo yeah
	def add_by_abbrv(self, abbrv, store=True):
		print(abbrv)
		link = self.link_begin + abbrv + self.link_ending
		content = requests.get(link)
		soup = BeautifulSoup(content.text, "html.parser")
		if abbrv not in self.Stocks:
			name = self.get_name(soup)
			if name == "":
				name = abbrv
		else:
			name = self.Stocks[abbrv].name
		data = self.get_data(soup)
		if data != "fail":
			addition = stock(name, abbrv, data[0], data[1], data[2], data[3])
			self.Stocks[addition.nick] = addition
			if store:
				self.storing()

	#Updating the stocks in the sytem and storing
	def update(self):
		print("This gonna take a while :(")
		for i in self.Stocks.keys():
			self.add_by_abbrv(i, False)
		self.storing()

	# Getting some stock symbols from the package
	def get_names(self):
		keep = True
		for resource in self.package.resources:
			if resource.descriptor['datahub']['type'] == 'derived/csv' and keep:
				data = resource.read()
				keep = False
				for stock in data:
					if stock[0].isalpha():
						self.names.append(stock[0])

	# Adding stocks from names to the system
	def add_all(self):
		for sym in self.names:
			try:
				self.add_by_abbrv(sym, False)
			except:
				print("Failed to add: " + sym)
	# Attempt to store data as a file
	def storing(self):
		with open(self.stocks_saved, "wb") as main_file:
			pickle.dump(self.Stocks, main_file)

	# Loading data from past save files
	def loading(self):
		self.get_names()
		try:
			with open(self.stocks_saved, "rb") as main_file:
				self.Stocks = pickle.load(main_file)
			print("Loaded data of " + str(len(self.Stocks)) + " stocks!")
		except FileNotFoundError:
			print("File hasn't been made yet")

	##### PRINTING FOR OUTPUT #####

	# Prints the Price, changes, and updated time of a given Stock abbreviation in STOCKS
	def check_stock(self, abbrv):
		current = self.Stocks[abbrv]
		print(current)

	# Prints the number of stocks in STOCKS
	def how_many(self):
		print(len(self.Stocks))

	# Prints the abbrv of each stock in STOCKS
	def listings(self):
		keys = self.Stocks.keys()
		return list(keys)

	# Prints all the valid actions!
	def help(self):
		print("The valid commands are: " + str(self.commands))


	##### DEBUGGING PURPOSES #####

	#Helps print out stocks that should be included
	def not_included(self):
		count = 0
		for abbrv in self.names:
			if abbrv not in self.Stocks and count < 10:
				count += 1
				print(abbrv)

############ TESTING COMMANDS ###########

main()

