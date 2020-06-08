from stuff import stock
from stuff import mySorts
from stuff import account
import urllib.request
import requests
from bs4 import BeautifulSoup 			# Needs a Pip install
import re
import pickle 							# Just do frist in first out type of storage?
from datapackage import Package 		# Needs a Pip install
import os
import datetime
import threading
import random
import string
import time

class main:

	# Stock package
	#package = Package('https://datahub.io/core/nyse-other-listings/datapackage.json')
	#nas_pack = Package('https://datahub.io/core/nasdaq-listings/datapackage.json')

	# YAHOO SEARCH LINKS TO HELP FOR SEARCHING!
	link_begin = "https://finance.yahoo.com/quote/"
	link_ending = "?ltr=1"
	stock_data_access = "My(6px) Pos(r) smartphone_Mt(6px)"
	stock_name_access = "Mt(15px)"
	stock_float_pattern = "[-+]?\d*\.?\d*%?$"
	stock_time_pattern = "\d+:\d*"+ "(AM|PM)$"

	# GOOGLE SEARCH LINKS
	goog_begin = "https://www.google.com/search?q="
	goog_mid = "+stocks&rlz="
	goog_end = "=chrome"
	time_stamp_class = "ZINbbc xpd O9g5cc uUPGi"
	goog_error = 0

	# LIST OF COMMANDS
	commands = ["add","admin", "check", "listings", "update", "help", "exit", "delete"]
	admin_comm = ["store"]

	# Data Storage Stuff
	Stocks_day_data = {} 				# Dictionary keeping track of the date to now
	Sorts_day_data = {} 				# Dictionary keeping track of sorted data
	Stocks = {} 						# Main dictionary of all stocks
	sorties = mySorts([[]],[[]],[[]]) 	# Keeps tracks of the sorts done
	active = False 						# Change to True for wanting input on system
	t_num = 30							# number of threads for updating the system
	t_active = 0						# number of threads still active
	reduced = False						# Tells if the timer to search has been reduced
	update_num = 0						# FOR DEBUGGING USE OF COUNTING STOCK DATA RETRIEVAL
	failed = []							# Tracks the symbols of stocks that failed data retrieval
	user_tracks = []					# Tracks a list of stocks that the user wants
	gainers = []						# A list of stocks that gained
	losers = []							# A list of stocks that lost

	# Account data
	accounts = {}

	# Saving directories/file names
	storing_dir = os.getcwd() + "/saved_data/"  # Main Storage directory file
	stocks_saved = storing_dir + "Stocks"		# Storage for stocks in the system
	other_saved = storing_dir + "Other"			# Storage for end of day stocks/sorting lists
	sorts_saved = storing_dir + "Sorts"			# Storage for current time sorting
	user_saved = storing_dir + "User_data"		# Storage for user tracked stocks
	accs_saved = storing_dir + "Accounts"		# Storage for the accounts made


	#################### INITIALIZATION STEPS ####################


	def __init__(self):
		self.name = "StockClass"
		main.loading()
		while main.active:
			action = input("WHAT U WANT? ")
			main.action_checker(action)


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
				main.fast_update()
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

	# Prints all abbrevations of stocks the user is tracking
	def tracking(tracker=""):
		if tracker == "":
			tracker = main.user_tracks
		print("You are currently tracking:")
		for abbrv in tracker:
			print(main.Stocks[abbrv])

	# Adds the abbreviation to user_tracks if it's in the system
	def track(abbrv, place=""):
		if place == "":
			place = main.user_tracks
		if abbrv in place:
			print("Already tracking " + abbrv)
		elif abbrv not in main.listings():
			print("That stocks isn't in the system!")
		else:
			place.append(abbrv)
			main.storing()
			print("Added " + abbrv + " to the watchlist")

	# Updates the stocks in WATCHLIST to current time
	def update_watchlist():
		main.fast_update(main.user_tracks)

	# Deletes stocks from user_tracks
	def stop_watching(abbrv):
		try:
			main.user_tracks.remove(abbrv)
		except ValueError:
			print("You already aren't watching " + abbrv)

	# Sorts lists by default being the watchlist
	def sort_watch(data=""):
		if data == "":
			main.user_tracks = main.norm_quicksort(main.user_tracks)
		else:
			data = main.norm_quicksort(data)
		main.storing()

	# Helps clear the whole watchlist(user_tracks)
	def clear_watch():
		main.user_tracks = []
		main.storing()

	# Tracks a set NUM of consecutive losers to the LOSERS.
	def track_losers(num=10):
		losers = main.consecutive_losers()
		for i in range(num):
			main.track(losers[i][1], main.losers)
		main.storing()

	# Tracks a set NUM of consecutive losers to the GAINERS.
	def track_gainers(num=10):
		gainers = main.consecutive_gainers()
		i = len(gainers) - 1
		while num > 0:
			main.track(gainers[i][1], main.gainers)
			i -= 1
			num -= 1
		main.storing()

	#################### HELPER FUNCTIONS ####################


	# Get name thru the abbrv link RETURNS a STRING(NAME)
	def get_name(soup, abbrv):
		try:
			title = soup.find("div", {"class" : main.stock_name_access}).find_all("h1")
			name = ""
			for i in title:
				for j in i.text.split():
					if re.match("[A-Z]{1}[a-z]+", j):
						name += j + " "
			return name.strip()
		except AttributeError:
			main.failed.append(abbrv)
			print("Failed name reqs on " + abbrv)
			return ""

	# Get's the updated info of a stock by the soup content
	# RETURNS A LIST: [PRICE, VALUE CHANGE, PERECENT CHANGE, TIME]
	def get_data(soup, abbrv):
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
			main.failed.append(abbrv)
			print("Failed data reqs on " + abbrv)
			return "fail"

	def in_list(abbrv):
		return abbrv in main.listings()


	#################### ADDING/STORING DATA ####################


	# Might add one for name of stock sooo yeah
	def add_by_abbrv(abbrv, store=True):
		try:
			main.update_num += 1
			print(main.update_num)
			ending = "/".join(random.choice(string.ascii_letters) for x in range(random.randrange(3,8)))
			link = main.link_begin + abbrv + main.link_ending + ending
			content = requests.get(link)
			soup = BeautifulSoup(content.text, "html.parser")
			if abbrv not in main.Stocks:
				name = main.get_name(soup, abbrv)
				if name == "":
					name = abbrv
			else:
				name = main.Stocks[abbrv].name
			data = main.get_data(soup, abbrv)
			if data != "fail":
				addition = stock(name, abbrv, data[0], data[1], data[2], data[3])
				main.Stocks[addition.nick] = addition
				if store:
					main.storing()
		except:
			main.failed.append(abbrv)
			print(abbrv + " Failed to aquire data!")
			time.sleep(random.randrange(2, 4))

	# Attempt 1 at finding stuff through google search
	def google_search(abbrv):
		main.update_num += 1
		print(main.update_num)
		after_mid = "".join(random.choice(string.ascii_letters) for x in range(random.randrange(3,8)))
		link = main.goog_begin + abbrv + main.goog_mid + after_mid + main.goog_end
		req = requests.get(link)
		souper = BeautifulSoup(req.text, "html.parser")
		content = souper.find("body").find_all("div", {"class", main.time_stamp_class})
		try:
			wanted = content[1].text.split()
			name = ""
			wanted_pos = 0
			count = 0
			for i in wanted:
				if i == "/":
					name.strip()
					wanted_pos = count + 2
					break
				name += i + " "
				count += 1
			price = wanted[wanted_pos][5:]
			wanted_pos += 1
			price_change = wanted[wanted_pos]
			wanted_pos += 1
			perecent = price_change[0]
			total_percent = wanted[wanted_pos]
			for j in range(1, len(total_percent)):
				if total_percent[j] == ")":
					perecent.strip()
					break
				perecent += total_percent[j]
			time = wanted[-9] + wanted[-8]
			price.replace(",", "")
			price_change.replace(",", "")
			perecent.replace(",", "")
			try:
				trial = float(price)
			except ValueError:
				print(abbrv + " has no good Price found")
			print("\n" + name)
			print(price)
			print(price_change)
			print(perecent)
			print(time + "\n")
		except Exception as e:
			main.goog_error += 1
			print("\n" + abbrv + " had an error in something " + str(e) + "\n")

	# Updates every stock in listings.
	def fast_update(stuff=[]):
		if stuff == []:
			stuff = main.listings()
		threads = []
		for i in range(main.t_num):
			#n = len(main.listings())-1-i
			threads.append(myThread(i, stuff))
		for t in threads:
			t.start()
			time.sleep(.35)
		for t_wait in threads:
			t_wait.join()
		print(len(main.failed))
		main.storing()
		main.safe_update()

	def safe_update():
		redo = main.failed
		main.failed = []
		if len(redo) == 0:
			print("Finished update")
			main.reduced = False
		else:
			time.sleep(10)
			print("Redoing some updates")
			main.t_num = min(len(redo), main.t_num)
			main.fast_update(redo)

	# Attempt to store data as a file
	def storing():
		print("STORING DATA...")
		with open(main.stocks_saved, "wb") as main_file:
			pickle.dump(main.Stocks, main_file)
		with open(main.sorts_saved, "wb") as price_file:
			pickle.dump(main.sorties, price_file)
		with open(main.user_saved, "wb") as user_file:
			pickle.dump(main.user_tracks, user_file)
			pickle.dump(main.gainers, user_file)
			pickle.dump(main.losers, user_file)
		with open(main.accs_saved, "wb") as account_file:
			pickle.dump(main.accounts, account_file)

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
			with open(main.user_saved, "rb") as user_file:
				main.user_tracks = pickle.load(user_file)
				main.gainers = pickle.load(user_file)
				main.losers = pickle.load(user_file)
			with open(main.accs_saved, "rb") as accs_file:
				main.accounts = pickle.load(accs_file)
		except FileNotFoundError:
			print("Files haven't been made yet")


	#################### SORTING DATA ####################


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

	# An attempt at quick sorting data(list of [x, y])!
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

	# Sorts a normal list of symbols by their percent changes
	def norm_quicksort(data):
		if len(data) <= 1:
			return data
		part_key = data[0]
		partition = float(main.Stocks[part_key].percent_change.replace("%", ""))
		left = []
		right = []
		middle = []
		for sym in data:
			compare = float(main.Stocks[sym].percent_change.replace("%", ""))
			if compare > partition:
				right.append(sym)
			elif compare < partition:
				left.append(sym)
			else:
				middle.append(sym)
		real_l = main.norm_quicksort(left)
		real_r = main.norm_quicksort(right)
		return real_l + middle + real_r

	################### ORGANIZING/ACQUIRING DATA ###################
	
	# Attempts to returns MYSORTS CLASS by checking if DAY is valid
	# DAY = mm/dd/yyyy format (starting 05/24/2020)
	def get_by_date(day, attempt=0):
		try:
			return main.Sorts_day_data[day]
		except KeyError:
			print("Invalid date")
			return ""

	# Helps print the top "NUM" losers by either "Price" or "Percent" for a DAY(mm/dd/yyyy)
	def top_day_losers(day, num=10, desire="Percent"):
		message = "Here are the top " + str(num)
		data = main.get_by_date(day)
		if data == "":
			print("Can't get data due to wrong date")
			return
		if desire == "Percent":
			message += " percent losers of " + day
			print(message)
			main.print_sort(data.getPer_change(), num, 0, 1)
		elif desire == "Price":
			message += " price losers of " + day
			print(message)
			main.print_sort(data.getP_change(), num, 0, 1)
		else:
			print("Invalid DEISRE!")

	# Helps find the top "NUM" losers by "Price" or "Percent" currently
	def cur_day_losers(num=10, desire="Percent"):
		message = "Here are the top " + str(num)
		if desire == "Percent":
			message += " percent losers currently"
			data = main.sort("percent_change")
			print(message)
			main.print_sort(data, num, 0, 1)
		elif desire == "Price":
			message += " price losers currently"
			data = main.sort("price_change")
			print(message)
			main.print_sort(data, num, 0, 1)
		else:
			print("Invalid DEISRE")


	# Helps print the top "NUM" gainers of a DAY(mm/dd/yyyy) by "Price" or "Percent"
	def top_day_gainers(day, num=10, desire="Percent"):
		message = "Here are the top " + str(num)
		data = main.get_by_date(day)
		if data == "":
			print("Can't get data due to wrong date")
			return
		if desire == "Percent":
			message += " percent gainers of " + day
			length = len(data.getPer_change()) - 1
			print(message)
			main.print_sort(data.getPer_change(), num, length, -1)
		elif desire == "Price":
			message += " price gainers of " + day
			length = len(data.getP_change()) - 1
			print(message)
			main.print_sort(data.getP_change(), num, length, -1)
		else:
			print("Invalid DEISRE!")


	# Helps find the top "NUM" losers by "Price" or "Percent" currently
	def cur_day_gainers(num=10, desire="Percent"):
		message = "Here are the top " + str(num)
		if desire == "Percent":
			message += " percent gainers currently"
			data = main.sort("percent_change")
			print(message)
			main.print_sort(data, num, len(data) - 1, -1)
		elif desire == "Price":
			message += " price gainers currently"
			data = main.sort("price_change")
			print(message)
			main.print_sort(data, num, len(data) - 1, -1)
		else:
			print("Invalid DEISRE")


	# Returns the specified STOCK on the specified day (mm/dd/yyyy)
	def specified_stock(abbrv, day): 
		try:
			data = main.Stocks_day_data[day]
			return data[abbrv]
		except KeyError:
			print("\nInvalid Stock or Date: Stocks found :")

	# Returns the most recent 2 consecutive days of stocks dictionaries
	def consecutive_dates():
		length = len(main.Stocks_day_data.keys()) - 1
		now = list(main.Stocks_day_data.keys())[length]
		last = list(main.Stocks_day_data.keys())[length - 1]
		first = main.Stocks_day_data[now]
		second = main.Stocks_day_data[last]
		return first, second

	# Returns a sorted list of ["perecent", abbrv] of all stocks that lost two days consecutively.
	def consecutive_losers():
		lost = []
		first, second = main.consecutive_dates()
		for s in first.keys():
			try:
				stock_1 = first[s]
				stock_2 = second[s]
				pert_change_1 = float(stock_1.percent_change.replace("%",""))
				pert_change_2 = float(stock_2.percent_change.replace("%", ""))
				if pert_change_1 < 0 and pert_change_2 < 0:
					keep = [pert_change_1 + pert_change_2, s]
					lost.append(keep)
			except KeyError:
				print("Not in some of the system: " + s)
		return main.quicksorter(lost)

	# Returns a sorted list of ["percent", abbrv] of all stocks that gained two days consecutrively.
	def consecutive_gainers():
		lost = []
		first, second = main.consecutive_dates()
		for s in first.keys():
			try:
				stock_1 = first[s]
				stock_2 = second[s]
				pert_change_1 = float(stock_1.percent_change.replace("%",""))
				pert_change_2 = float(stock_2.percent_change.replace("%", ""))
				if pert_change_1 > 0 and pert_change_2 > 0:
					keep = [pert_change_1 + pert_change_2, s]
					lost.append(keep)
			except KeyError:
				print("Not in some of the system: " + s)
		return main.quicksorter(lost)

	# Prints a list of consecutive losers
	def print_consecutive_losers(num=10):
		losers = main.consecutive_losers()
		main.print_sort(losers, num, 0, 1)

	def print_consecutive_gainers(num=10):
		gainers = main.consecutive_gainers()
		main.print_sort(gainers, num, len(gainers) - 1, -1)


	#################### ACCOUNT SETUP ####################
	
	# Makes a new account
	def make_account(name, deposit):
		if name in main.accounts.keys():
			print("Account already is in the system")
		else:
			acc = account(name, deposit)
			main.accounts[name] = acc
			main.storing()

	# Adds a stock to an account's watchlist
	def account_watch(name, abbrv):
		try:
			if main.in_list(abbrv):
				main.accounts[name].watch(abbrv)
				main.storing()
			else:
				print("Stock not in the current system")
		except KeyError:
			print("That account is not in the system")

	def account_watchlist(name):
		try:
			names = main.accounts[name].watchlist()
			print("\nHere's " + name + "'s watchlists: ")
			for s in names:
				print(main.Stocks[s])
		except KeyError:
			print("That account is not in the system")

	# Buys a set QUANTITY amount of a stock by the symbol(ABVRV)
	# For a set account(NAME) for a price per stock(AMOUNT)
	def account_buy(name, abbrv, quantity):
		try:
			if main.in_list(abbrv):
				amount = float(main.Stocks[abbrv].cur_price)
				main.accounts[name].buy(abbrv, quantity, amount)
				main.storing()
			else:
				print("That stock isn't in the system")
		except KeyError:
			print("That account is not in the system")


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
		print(main.Stocks_day_data.keys())

	#Adding stocks from names to the system
	def add_all():
		for sym in main.listings():
			try:
				main.add_by_abbrv(sym, False)
			except:
				print("Failed to add: " + sym)
		main.storing()

	# Prints the top NUM of a sorted list DATA of [x,y] (y = stock sym)
	# Start = starting index, 0 for losers, 1980 for gainers
	# Changer is 1 or -1 respectively
	# LOWER_BOUND helps prevent penny stocks to be shown
	def print_sort(data, num, start, changer, lower_bound=1):
		while num and start >= 0 and start <= len(data) - 1:
			sym = data[start][1]
			stock = main.Stocks[sym]
			price = float(stock.cur_price)
			if price > lower_bound:
				print(data[start])
				num -= 1
			start += changer

	# Getting some stock symbols from the package
	def get_names():
		keep = True
		for resource in main.package.resources:
			if resource.descriptor['datahub']['type'] == 'derived/csv' and keep:
				data = resource.read()
				keep = False
				nasdaq = []
				for stock in data:
					if stock[0].isalpha() and not main.in_list(stock[0]):
						nasdaq.append(stock[0])
				print(len(nasdaq))
				main.fast_update(nasdaq)

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

	max_t = 12
	min_t = 2

	def __init__(self, threadID, listings):
		threading.Thread.__init__(self)
		self.ID = threadID
		self.listings = listings
		main.t_active += 1

	# STORAGE is the list of all abbrvs in main.stocks
	# Helps run each thread to match it's own ID
	def run(self):
		print("Starting Thread " + str(self.ID))
		count = self.ID
		while count < len(self.listings):
			delay = random.randint(myThread.min_t, myThread.max_t) + random.random()
			stock = self.listings[count]
			main.add_by_abbrv(stock, False)
			#main.google_search(stock)
			time.sleep(delay)
			count += main.t_num
		print("Ending Thread: " + str(self.ID))
		main.t_active -= 1
		if (main.t_active <= (main.t_num / 2) + 1) and not main.reduced:
			print("Reducing delay max time!!!")
			myThread.max_t = myThread.max_t // 2
			main.reduced = True

############ TESTING COMMANDS ###########

if __name__ == "__main__":
	test = main()
	main.fast_update()
