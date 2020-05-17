import datetime

class stock:

	# Initializer with:
	#	Name, Abbreviation, Price, Percent Change, and Price Change!
	#	Also the last time updated!
	def __init__(self, name="none", abbrv="none", price="0", diff="0", percent="0", time="Never"):
		self.name = name
		self.nick = abbrv
		self.cur_price = price
		self.percent_change = percent
		self.price_change = diff
		self.updated = time + " EST " + datetime.datetime.now().strftime("%m/%d/%Y")

	def __repr__(self):
		return "Stock data of " + self.name

			
	def __str__(self):
		content = "\n" + self.name + ": " + self.nick + "\n"
		content += self.price() + "\n"
		content += self.change() + "\n"
		content += self.timeStamp(True) + "\n"
		return content

		# Time of last upadated system
	def timeStamp(self, updated=True):
		if updated:
			timestamp = "Last Updated at "
		else:
			timestamp = "as of "
		return timestamp + self.updated + "."

	# (Last Updated) Price of Stock
	def price(self):
		result = "Price of " + self.nick + " is: $" + self.cur_price + "."
		return result

	# (Last Updated) Change of Percent/Price
	def change(self):
		pert_change = "% Change of " + self.nick + " is: " + self.percent_change + "."
		value_change = "$ Change of " + self.nick + " is: " + self.price_change + "."
		result = value_change + "\n" + pert_change
		return result

	# Updates the stock's:
	#	Current Price, Percent/Price Changes, and Time
	def update(self, price, percent, diff, time):
		self.cur_price = price
		self.percent_change = percent
		self.price_change = diff
		self.updated = time