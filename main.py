from stuff import stock
from stuff import mySorts
import urllib.request
import requests
from bs4 import BeautifulSoup
import re
import pickle
from datapackage import Package 
import os
import datetime
import threading

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
	commands = ["add","admin", "check", "listings", "update", "help", "exit", "delete"]
	admin_comm = ["store"]

	Stocks_day_data = {} # Dictionary keeping track of the date to now
	Sorts_day_data = {} # Dictionary keeping track of sorted data
	Stocks = {} # Main dictionary of all stocks
	sorties = mySorts([[]],[[]],[[]]) # Keeps tracks of the sorts done
	active = False # Change to True for wanting input on system
	t_num = 5 # number of threads for updating the system
	update_num = 0

	# Saving directories/file names
	storing_dir = os.getcwd() + "/saved_data/"
	stocks_saved = storing_dir + "Stocks"
	other_saved = storing_dir + "Other"
	sorts_saved = storing_dir + "Sorts"


	#################### INITIALIZATION STEPS ####################


	def __init__(self):
		self.name = "StockClass"
		main.loading()
		while main.active:
			action = input("WHAT U WANT? ")
			main.action_checker(action)
	# Repr of main
	def __repr__(self):
		return "The totally MAssive data class"

	# Str of main
	def __str__(self):
		return "Printing data of myself?"


	#################### HANDLING COMMANDS ####################


	def action_checker(action):
		if action in main.commands:
			if action == "exit":
				main.storing()
				print("BYE BYE")
				exit()
			elif action == "admin":
				main.admin_check()
			elif action == "update":
				print("This gonna take around 45ish minutes...")
				main.update()
			elif action == "help":
				main.help()
			elif action == "listings":
				print(str(main.listings()))
			elif action == "delete":
				name = input("Please enter stock abbrev: ")
				main.delete_stock(name)
			elif action == "add":
				cur = input("Please enter the desired stock symbol: ")
				main.action_add(cur)
			elif action == "check":
				cur = input("Please enter the desired stock symbol: ")
				main.check_stock(cur)
		else:
			print(action + " is an invalid commnad. Please enter another one!")

	# Prints the Price, changes, and updated time of a given Stock abbreviation in STOCKS
	def check_stock(abbrv):
		keys = main.listings()
		if abbrv not in keys:
			reply = "Sorry that stock isn't available in the system yet!" + "\n"
			reply += "Here's the available stock symbol's: " + str(keys)
			print(reply)
			main.action_checker("check")
		else:
			current = main.Stocks[abbrv]
			print(current)

	# Check if a stock can be added
	def action_add(abbrv):
		if abbrv in main.listings():
			print("That stock is already in the system")
			reply = input("Would you like to update it? [Y/N]")
			if reply == "Y":
				main.add_by_abbrv(abbrv)
			else:
				return
		else:
			main.add_by_abbrv(abbrv)

	# Prints the number of stocks in STOCKS
	def how_many():
		print(len(main.Stocks))

	# Prints the abbrv of each stock in STOCKS
	def listings():
		keys = main.Stocks.keys()
		return list(keys)

	# Prints all the valid actions!
	def help():
		print("The valid commands are: " + str(main.commands))


	#################### HELPER FUNCTIONS ####################


	# Get name thru the abbrv link RETURNS a STRING(NAME)
	def get_name(soup):
		try:
			title = soup.find("div", {"class" : main.stock_name_access}).find_all("h1")
			name = ""
			for i in title:
				for j in i.text.split():
					if re.match("[A-Z]{1}[a-z]+", j):
						name += j + " "
			return name.strip()
		except AttributeError:
			print("Failed name reqs")
			return ""

	# Get's the updated info of a stock by the soup content
	# RETURNS A LIST: [PRICE, VALUE CHANGE, PERECENT CHANGE, TIME]
	def get_data(soup):
		try:
			trial = soup.find("div", {"class" : main.stock_data_access}).find_all("span")
			count = 0
			results = []
			for i in trial:
				for j in i.text.split():
					j = re.sub("[(,)]", "", j)
					if count < 4 and (re.match(main.stock_float_pattern, j) or re.match(main.stock_time_pattern, j)): #Set to 4 so I don't get Pre/Post Market
						count += 1
						results.append(j)
			return results
		except AttributeError:
			print("Failed data reqs")
			return "fail"


	#################### ADDING/STORING DATA ####################


	# Might add one for name of stock sooo yeah
	def add_by_abbrv(abbrv, store=True):
		print(abbrv)
		link = main.link_begin + abbrv + main.link_ending
		content = requests.get(link)
		soup = BeautifulSoup(content.text, "html.parser")
		if abbrv not in main.Stocks:
			name = main.get_name(soup)
			if name == "":
				name = abbrv
		else:
			name = main.Stocks[abbrv].name
		data = main.get_data(soup)
		if data != "fail":
			main.update_num += 1
			addition = stock(name, abbrv, data[0], data[1], data[2], data[3])
			main.Stocks[addition.nick] = addition
			print(main.update_num)
			if store:
				main.storing()

	#Updating the stocks in the sytem and storing
	def update():
		print("This gonna take a while :(")
		for i in main.Stocks.keys():
			main.add_by_abbrv(i, False)
		main.storing()

	def fast_update():
		threads = []
		for i in range(main.t_num):
			threads.append(myThread(i, main.listings()))
		for t in threads:
			t.start()
		for t_wait in threads:
			t_wait.join()
		main.storing()

	# Attempt to store data as a file
	def storing():
		print("STORING DATA...")
		with open(main.stocks_saved, "wb") as main_file:
			pickle.dump(main.Stocks, main_file)
		with open(main.sorts_saved, "wb") as price_file:
			pickle.dump(main.sorties, price_file)

	def day_storage():
		date = datetime.datetime.now().strftime("%m/%d/%Y")
		main.Sorts_day_data[date] = main.sorties
		main.Stocks_day_data[date] = main.Stocks
		with open(main.other_saved, "wb") as other_file:
			pickle.dump(main.Stocks_day_data, other_file)
			pickle.dump(main.Sorts_day_data, other_file)

	# Loading data from past save files
	def loading():
		try:
			with open(main.stocks_saved, "rb") as main_file:
				main.Stocks = pickle.load(main_file)
			print("Loaded data of " + str(len(main.Stocks)) + " stocks!")
			with open(main.other_saved, "rb") as other_file:
				main.Stocks_day_data = pickle.load(other_file)
				main.Sorts_day_data = pickle.load(other_file)
			with open(main.sorts_saved, "rb") as price_file:
				main.sorties = pickle.load(price_file)
		except FileNotFoundError:
			print("Files haven't been made yet")

	def sort_all():
		pert_change = main.sort("percent_change")
		p_change = main.sort("price_change")
		cur_p = main.sort("cur_price")
		main.sorties = mySorts(p_change, pert_change, cur_p)
		main.storing()

	# sort by the NEEDED of Stocks and store in s_Price (cur_price, price_change, percent_change)
	def sort(needed):
		values = []
		for s in main.listings():
			if needed == "cur_price":
				data = main.Stocks[s].cur_price
			elif needed == "percent_change":
				data = main.Stocks[s].percent_change.replace("%", "")
			elif needed == "price_change":
				data = main.Stocks[s].price_change
			else:
				print("Invalid Sorting Command Issued")
				return
			want = float(data)
			key = [want, s]
			values.append(key)
		return main.quicksorter(values)

	# An attempt at quick sorting data!
	def quicksorter(data):
		if len(data) <= 1:
			return data
		partition = data[0][0]
		left = []
		right = []
		keep = []
		for stock in data:
			num = stock[0]
			if num == partition:
				keep.append(stock)
			elif num < partition:
				left.append(stock)
			else:
				right.append(stock)
		real_l = main.quicksorter(left)
		real_r = main.quicksorter(right)
		return real_l + keep + real_r

	#################### DEBUGGING/RANDO STATS STUFF ####################

	# checking for acces to do other stuff
	def admin_check():
		code = input("Password pls: ")
		if code == "Stocks":
			print("Access granted!")
			main.admin_action()

	# Able to run day_storage and more later...
	def admin_action():
		reply = input("What would you like to do?")
		if reply == "store all":
			main.day_storage()
		elif reply == "logout":
			print("Logging out and returning to normal...")
		elif reply == "logout":
			print("Logging out and exiting")
			exit()
		else:
			print("Invalid command... Try again")
			main.admin_action()
		main.admin_action()

	#Helps print out stocks that should be included
	def not_included():
		count = 0
		for abbrv in main.Stocks.keys():
			if abbrv not in main.listings() and count < 10:
				count += 1
				print(abbrv)

	# Deletes unwanted stocks from the data
	def delete_stock(abbrv):
		if abbrv in main.listings():
			stock = main.Stocks[abbrv]
			print("Delete " + stock.name)
			reply = input("Y/N")
			if reply == "Y":
				del main.Stocks[abbrv]
				main.storing()
				main.day_storage()
			else:
				return
		else:
			print("Stock is already not in the system")

	# Attempt to get the average price of all the stocks in the system
	def average_price():
		total = 0
		for stock in main.Stocks.values():
			try:
				total += float(stock.cur_price)
			except:
				print(stock.nick + " doesn't have a price?" + stock.cur_price)
		return total/len(main.Stocks)

	# Attempt to check that the day storing is correct
	def checking_day_storage():
		#print(str(main.Stocks_day_data.keys()))
		#print(main.Stocks_day_data["05/24/2020"]["CVX"])
		main.check_sort(0, 10, 1, "Per_change")

	#Adding stocks from names to the system
	def add_all():
		for sym in main.listings():
			try:
				main.add_by_abbrv(sym, False)
			except:
				print("Failed to add: " + sym)
		main.storing()

	# START: starting index of sort, 
	# CHANGER: 1 or -1 for increase/decrease, 
	# NUM = number of prints
	# Desire = get(P_change, Per_change, Cur_price) from mySorts class
	def check_sort(start, num, changer, desire):
		message = "Here is the "
		if start == len(main.listings()):
			message += "top "
		elif start == 0:
			message += "bottom "
		if desire == "P_change":
			message += str(num) + " Price Changes today!"
			wanted = main.sorties.getP_change()
		elif desire == "Per_change":
			message += str(num) + " Percent Changes today!"
			wanted = main.sorties.getPer_change()
		elif desire == "Cur_price":
			message += str(num) + " Current Prices today!"
			wanted = main.sorties.getCur_price()
		else:
			print("Need a new DESIRE please")
			return
		print(message)
		while num:
			print(str(wanted[start]))
			num -= 1
			start += changer

	# Getting some stock symbols from the package
	#def get_names():
	#	keep = True
	#	for resource in main.package.resources:
	#		if resource.descriptor['datahub']['type'] == 'derived/csv' and keep:
	#			data = resource.read()
	#			keep = False
	#			for stock in data:
	#				if stock[0].isalpha():
	#					main.names.append(stock[0])

	# Get's rid of names of stocks not STOCKS
	#def filter_names():
	#	new_names = []
	#	for abbrv in main.names:
	#		if abbrv in main.Stocks.keys():
	#			new_names.append(abbrv)
	#	main.names = new_names
	#	main.storing()


################### THREADING CLASS ###################

class myThread (threading.Thread):

	def __init__(self, threadID, listings):
		threading.Thread.__init__(self)
		self.ID = threadID
		self.listings = listings

	# STORAGE is the list of all abbrvs in main.stocks
	# Helps run each thread to match it's own ID
	def run(self):
		print("Starting Thread " + str(self.ID))
		count = self.ID
		while count < len(self.listings):
			stock = self.listings[count]
			main.add_by_abbrv(stock, False)
			count += main.t_num
		print("Ending Thread: " + str(self.ID))

############ TESTING COMMANDS ###########

if __name__ == "__main__":
	test = main()
	main.checking_day_storage()
