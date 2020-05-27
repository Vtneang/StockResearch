from .bought import bought

class account:

	# NAME is a symbol for the account, deposit is the down payment
	def __init__(self, name, deposit):
		self.name = name
		self.balance = deposit
		self.tracking = []
		self.positions = {}

	# Adds the abbrv of a stock to the watchlist
	def watch(self, abbrv):
		if abbrv in self.tracking:
			print("This " + abbrv + " is already in the watchlist")
		else:
			self.tracking.append(abbrv)

	# Returns the WATCHLIST of an account so main.py can print it
	def watchlist(self):
		return self.tracking

	# Stops watching a stock from the watchlist
	def stop_watch(self, abbrv):
		try:
			self.tracking.remove(abbrv)
		except ValueError:
			print("Already not in the watchlist")

	# Buys a set QUANTITY amount of a stock for a certain amount 
	def buy(self, abbrv, amount, quantity):
		total = amount * quantity
		if self.balance < total:
			print("Insufficient funds")
			return
		elif abbrv in self.positions:
			b = self.positions[abbrv]
			b.buy_more(quantity, amount)
		else:
			b = bought(abbrv, amount, quantity)
			self.positions[abbrv] = b
			#STUFF



################## DEBUGGING HELP #################

	def check_buy(self):
		for s in list(self.positions.keys()):
			print(s)
			print(self.positions[s].quantity)


############ TESTING COMMANDS ###########

if __name__ == "__main__":
	hi = account("V", 600)
	hi.buy("CVX", 5, 93)
	print(hi.positions)
	hi.check_buy()