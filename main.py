from stuff import stock
from stuff import mySorts 				# Needs to have the __init__.py in folder of these imports
from stuff import account 				# Also needs to have a direct python path to this file
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
	another_end = "&.tsrc=fin-srch"										# abrv?p=abbrv + this
	stock_data_access = "My(6px) Pos(r) smartphone_Mt(6px)"
	stock_name_access = "Mt(15px)"
	stock_float_pattern = "[-+]?\d*\.?\d*%?$"
	stock_time_pattern = "\d+:\d*"+ "(AM|PM)$"

	# PROXY GATHERING
	proxy_link = "https://free-proxy-list.net/"
	proxies = []
	safe_proxies = []
	rotated = False
	failed_per_proxy = 0
	proxy_num = 0
	cur_prox = {}
	proxing = False


	# LIST OF COMMANDS
	commands = ["add","admin", "check", "listings", "update", "help", "exit", "delete"]
	admin_comm = ["store"]

	# Data Storage Stuff
	Stocks_day_data = {} 				# Dictionary keeping track of the date to now
	Sorts_day_data = {} 				# Dictionary keeping track of sorted data
	Stocks = {} 						# Main dictionary of all stocks
	sorties = mySorts([[]],[[]],[[]]) 	# Keeps tracks of the sorts done
	active = False 						# Change to True for wanting input on system
	t_num = 25							# number of threads for updating the system
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


	def get_link(abbrv):
		link = main.link_begin + abbrv
		x = random.randrange(0, 2)
		if x == 0:
			end = "/".join(random.choice(string.ascii_letters) for x in range(random.randrange(3,10)))
			link += main.link_ending + end
			return link
		else:
			end = "?p=" + abbrv + main.another_end
			link += end
			return link


	# Get name thru the abbrv link RETURNS a STRING(NAME)
	def get_name(soup, abbrv, proxy=None):
		try:
			title = soup.find("div", {"class" : main.stock_name_access}).find_all("h1")
			name = ""
			for i in title:
				for j in i.text.split():
					if re.match("[A-Z]{1}[a-z]+", j):
						name += j + " "
			return name.strip()
		except AttributeError:
			if main.cur_prox == proxy:
				main.failed_per_proxy += 1
			main.failed.append(abbrv)
			print("Failed name reqs on " + abbrv)
			return ""

	# Get's the updated info of a stock by the soup content
	# RETURNS A LIST: [PRICE, VALUE CHANGE, PERECENT CHANGE, TIME]
	def get_data(soup, abbrv, proxy=None):
		try:
			#trial = soup.find("div", {"class" : main.stock_data_access}).find_all("span")
			trial = soup.find("div", class_=main.stock_data_access).find_all("span")
			count = 0
			results = []
			for i in trial:
				for j in i.text.split():
					j = re.sub("[(,)]", "", j)
					if count < 4 and (re.match(main.stock_float_pattern, j) or re.match(main.stock_time_pattern, j)): #Set to 4 so I don't get Pre/Post Market
						count += 1
						results.append(j)
			return results
		except Exception as e:
			if main.cur_prox == proxy:
				main.failed_per_proxy += 1
			main.failed.append(abbrv)
			print("Failed data reqs on " + abbrv + " Because " + str(e))
			return "fail"

	def in_list(abbrv):
		return abbrv in main.listings()


	#################### ADDING/STORING DATA ####################


	# Might add one for name of stock sooo yeah
	def add_by_abbrv(abbrv, store=True, redo=False, num=0):
		try:
			if redo:
				x = num
			else:
				main.update_num += 1
				x = main.update_num
			link = main.get_link(abbrv)
			if main.proxing:
				rando_prox = main.get_safe_proxy()
				content = requests.get(link, proxies=rando_prox, timeout=35)
				print(str(x) + " - " + abbrv + ": " + str(rando_prox["http"]))
			else:
				rando_prox = "No proxy"
				print(str(main.update_num) + " " + abbrv)
				content = requests.get(link)
			soup = BeautifulSoup(content.text, "html.parser")
			if abbrv not in main.Stocks:
				name = main.get_name(soup, abbrv, rando_prox)
				if name == "":
					name = abbrv
			else:
				name = main.Stocks[abbrv].name
			data = main.get_data(soup, abbrv, rando_prox)
			if data != "fail":
				addition = stock(name, abbrv, data[0], data[1], data[2], data[3])
				main.Stocks[addition.nick] = addition
				if store:
					main.storing()
		except Exception as e:
			if main.cur_prox == rando_prox:
				print(abbrv + " Failed to aquire data! " + str(rando_prox["http"])+ "\nBecause " + str(e))
				main.failed_per_proxy += 1
			else:
				time.sleep(5)
			main.failed.append(abbrv)

	def proxy_update():
		main.test_proxies()
		main.cur_prox = main.get_safe_proxy()
		possible = main.t_num * (len(main.safe_proxies) // 2)
		main.t_num = max(min(250, possible), 25)
		main.proxing = True
		main.fast_update()

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
			time.sleep(.05)
		for t_wait in threads:
			t_wait.join()
		main.storing()
		myThread.count = 0
		main.safe_update()

	def safe_update():
		main.update_num = 0
		redo = main.failed
		main.failed = []
		if len(redo) == 0:
			print("Finished update")
			main.reduced = False
		else:
			print(len(redo))
			time.sleep(8)
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
	def cur_day_losers(num=10, desire="Percent", bound=1):
		message = "Here are the top " + str(num)
		if desire == "Percent":
			message += " percent losers currently"
			data = main.sort("percent_change")
			print(message)
			main.print_sort(data, num, 0, 1, bound)
		elif desire == "Price":
			message += " price losers currently"
			data = main.sort("price_change")
			print(message)
			main.print_sort(data, num, 0, 1, bound)
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


	#################### PROXY GATHERING ####################

	# Helps gather a list of availble proxies
	def proxy_gathering():
		requ = requests.get(main.proxy_link)
		soupy = BeautifulSoup(requ.text, "html.parser")
		content = soupy.select("tr")
		for i in content:
			#print(str(i) + "\n")
			try:
				if i.find_all("td", class_="hx")[0].text == "yes" and i.find_all("td")[4].text == "elite proxy":
					main.proxies.append(str(i.find_all("td")[0].text) + ":" + str(i.find_all("td")[1].text))
			except:
				# Do nothing
				x = 4

	# Tests which Proxies can acutally connect to YAHOO
	def proxy_testing(proxy, abbrv):
		link = main.link_begin + abbrv + main.link_ending
		p = {"http": "http://" + proxy, "https": "https://" + proxy}
		try:
			content = requests.get(link, proxies=p, timeout=5)
			soupy = BeautifulSoup(content.text, "html.parser")
			main.safe_proxies.append(p)
		except Exception as e:
			# Do nothing
			print(str(proxy) + " Failed")

	# Starts and runs the proxy threads that test all availble PROXIES
	def filter_proxies():
		p_threads = []
		for i in range(len(main.proxies)):
			p_threads.append(proxyThread(i))
		for thread in p_threads:
			thread.start()
		for t in p_threads:
			t.join()
		print("Finished filtering proxies to " + str(len(main.safe_proxies)))

	# Returns a safe proxy number
	def get_safe_proxy():
		try:
			return main.safe_proxies[main.proxy_num]
		except Exception as e:
			return "None"

	# Starts to get new proxies or update last one
	def update_proxy():
		print("Updating the Proxy Number!!!")
		if main.proxy_num >= len(main.safe_proxies) - 1:
			main.proxies = []
			main.safe_proxies = []
			main.test_proxies()
			main.proxy_num = 0
		else:
			main.proxy_num += 1
		main.cur_prox = main.safe_proxies[main.proxy_num]
		time.sleep(5)

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
				print(stock)
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

	# Just tests how many safe proxies are gathered
	def test_proxies():
		main.proxy_gathering()
		main.filter_proxies()


	# Get's rid of names of stocks not STOCKS
	#def filter_names():
	#	new_names = []
	#	for abbrv in main.names:
	#		if abbrv in main.Stocks.keys():
	#			new_names.append(abbrv)
	#	main.names = new_names
	#	main.storing()


################### THREADING CLASSES ###################

class myThread (threading.Thread):

	max_t = 3
	min_t = 1
	count = 0

	def __init__(self, threadID, listings):
		threading.Thread.__init__(self)
		self.ID = threadID
		self.listings = listings
		main.t_active += 1

	# STORAGE is the list of all abbrvs in main.stocks
	# Helps run each thread to match it's own ID
	def run(self):
		print("Starting Thread " + str(self.ID))
		while myThread.count < len(self.listings):
			#delay = random.randint(myThread.min_t, myThread.max_t) + random.random()
			if main.failed_per_proxy >= 10 and not main.rotated:
				main.failed_per_proxy = 0
				main.rotated = True
				main.update_proxy()
				main.rotated = False
			elif main.rotated:
				time.sleep(10)
			else:
				stock = self.listings[myThread.count]
				myThread.count += 1
				main.add_by_abbrv(stock, False)
				if myThread.count >= len(self.listings):
					break
				else:
					time.sleep(random.randint(myThread.min_t, myThread.max_t))
				#main.google_search(stock)
				#time.sleep(delay)
		print("Ending Thread: " + str(self.ID))
		main.t_active -= 1
		#if (main.t_active <= (main.t_num // 1.5) + 1) and not main.reduced:
		#	print("Reducing delay max time!!!")
		#	myThread.max_t = myThread.max_t // 2
		#	main.reduced = True


# Helps with gathering new working proxy numbers and stores them in MAIN.PROXIES
class proxyThread (threading.Thread):

	# Have an Id match every thread in MAIN.PROXIES
	def __init__(self, ID):
		threading.Thread.__init__(self)
		self.ID = ID

	def run(self):
		print("Starting Proxy Thread " + str(self.ID))
		proxy_num = main.proxies[self.ID]
		main.proxy_testing(proxy_num, "CVX")
		print("Ending Proxy Thread " + str(self.ID))

############ TESTING COMMANDS ###########

if __name__ == "__main__":
	test = main()
	main.proxy_update()
	main.sort_all()
	main.day_storage()
	main.cur_day_losers(bound=2) 
	#main.cur_day_gainers()
	#main.proxy_gathering()
	#main.print_consecutive_gainers()
	#main.print_consecutive_losers()
	#main.check_stock("CVX")
	#main.checking_day_storage()


