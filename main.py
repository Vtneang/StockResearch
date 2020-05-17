from stuff import stock
import urllib.request
import requests
from bs4 import BeautifulSoup
import re
import pickle
from datapackage import Package 
import os
import datetime

class main:

	# Stock package
	package = Package('https://datahub.io/core/nyse-other-listings/datapackage.json')

	# YAHOO SEARCH LINKS TO HELP FOR SEARCHING!
	link_begin = "https://finance.yahoo.com/quote/"
	link_ending = "?ltr=1"
	stock_data_access = "My(6px) Pos(r) smartphone_Mt(6px)"
	stock_name_access = "Mt(15px)"
	stock_float_pattern = "[-+]?\d*\.?\d*%?$"
	stock_time_pattern = "\d+:\d*"+ "(AM|PM)$"

	# LIST OF COMMANDS
	commands = ["add","admin", "check", "listings", "update", "help", "exit"]
	admin_comm = ["store"]

	Stocks_day_data = {} # Dictionary keeping track of the date to 
	Stocks = {} # Main dictionary of all stocks
	active = False # Change to True for wanting input on system

	# Saving directories/file names
	storing_dir = os.getcwd() + "/saved_data/"
	stocks_saved = storing_dir + "Stocks"
	other_saved = storing_dir + "Other"


	#################### INITIALIZATION STEPS ####################


	def __init__(self):
		self.name = "StockClass"
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


	#################### HANDLING COMMANDS ####################


	def action_checker(self, action):
		if action in self.commands:
			if action == "exit":
				self.storing()
				print("BYE BYE")
				exit()
			elif action == "admin":
				self.admin_check()
			elif action == "update":
				print("This gonna take around 45ish minutes...")
				self.update()
			elif action == "help":
				self.help()
			elif action == "listings":
				print(str(self.listings()))
			elif action == "add":
				cur = input("Please enter the desired stock symbol: ")
				self.action_add(cur)
			elif action == "check":
				cur = input("Please enter the desired stock symbol: ")
				self.check_stock(cur)
		else:
			print(action + " is an invalid commnad. Please enter another one!")

	# Prints the Price, changes, and updated time of a given Stock abbreviation in STOCKS
	def check_stock(self, abbrv):
		keys = self.listings()
		if abbrv not in keys:
			reply = "Sorry that stock isn't available in the system yet!" + "\n"
			reply += "Here's the available stock symbol's: " + str(keys)
			print(reply)
			self.action_checker("check")
		else:
			current = self.Stocks[abbrv]
			print(current)

	# Check if a stock can be added
	def action_add(self, abbrv):
		if abbrv in self.listings():
			print("That stock is already in the system")
			reply = input("Would you like to update it? [Y/N]")
			if reply == "Y":
				print("Not available ATM")
			else:
				return
		else:
			self.add_by_abbrv(abbrv)

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


	#################### HELPER FUNCTIONS ####################


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


	#################### ADDING/STORING DATA ####################


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

	# Attempt to store data as a file
	def storing(self):
		with open(self.stocks_saved, "wb") as main_file:
			pickle.dump(self.Stocks, main_file)

	def day_storage(self):
		date = datetime.datetime.now().strftime("%m/%d/%Y")
		self.Stocks_day_data[date] = self.Stocks
		with open(self.other_saved, "wb") as other_file:
			pickle.dump(self.Stocks_day_data, other_file)

	# Loading data from past save files
	def loading(self):
		try:
			with open(self.stocks_saved, "rb") as main_file:
				self.Stocks = pickle.load(main_file)
			print("Loaded data of " + str(len(self.Stocks)) + " stocks!")
			with open(self.other_saved, "rb") as other_file:
				self.Stocks_day_data = pickle.load(other_file)
		except FileNotFoundError:
			print("Files haven't been made yet")


	#################### DEBUGGING/RANDO STATS STUFF ####################

	# checking for acces to do other stuff
	def admin_check(self):
		code = input("Password pls: ")
		if code == "Stocks":
			print("Access granted!")
			self.admin_action()

	# Able to run day_storage and more later...
	def admin_action(self):
		reply = input("What would you like to do?")
		if reply == "store all":
			self.day_storage()
		elif reply == "logout":
			print("Logging out and returning to normal...")
		elif reply == "logout":
			print("Logging out and exiting")
			exit()
		else:
			print("Invalid command... Try again")
			self.admin_action()
		self.admin_action()

	#Helps print out stocks that should be included
	def not_included(self):
		count = 0
		for abbrv in self.Stocks.keys():
			if abbrv not in self.listings() and count < 10:
				count += 1
				print(abbrv)

	# Deletes unwanted stocks from the data
	def delete_stock(self, abbrv):
		if abbrv in self.listings():
			stock = self.Stocks[abbrv]
			print("Delete " + stock.name)
			reply = input("Y/N")
			if reply == "Y":
				del self.Stocks[abbrv]
			else:
				return
		else:
			print("Stock is already not in the system")

	# Attempt to get the average price of all the stocks in the system
	def average_price(self):
		total = 0
		for stock in self.Stocks.values():
			try:
				total += float(stock.cur_price)
			except:
				print(stock.nick + " doesn't have a price?" + stock.cur_price)
		return total/len(self.Stocks)

	def checking_day_storage(self):
		print(len(self.Stocks_day_data["05/16/2020"]))
		print(self.Stocks_day_data["05/16/2020"]["CVX"])

	# Getting some stock symbols from the package
	#def get_names(self):
	#	keep = True
	#	for resource in self.package.resources:
	#		if resource.descriptor['datahub']['type'] == 'derived/csv' and keep:
	#			data = resource.read()
	#			keep = False
	#			for stock in data:
	#				if stock[0].isalpha():
	#					self.names.append(stock[0])

	# Get's rid of names of stocks not STOCKS
	#def filter_names(self):
	#	new_names = []
	#	for abbrv in self.names:
	#		if abbrv in self.Stocks.keys():
	#			new_names.append(abbrv)
	#	self.names = new_names
	#	self.storing()

	# Adding stocks from names to the system
	#def add_all(self):
	#	for sym in self.names:
	#		try:
	#			self.add_by_abbrv(sym, False)
	#		except:
	#			print("Failed to add: " + sym)


############ TESTING COMMANDS ###########


test = main()
test.checking_day_storage()

