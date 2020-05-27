class bought:
	
	# ABBRV is the stock symbol that is bought
	# TOTAL is the total amount the stocks were bought for
	# QUANTITY is the number of stocks bought
	def __init__(self, abbrv, amount, quantity):
		self.name = abbrv
		self.total = amount * quantity
		self.quantity = quantity
		self.per_stock = amount

	def __str__(self):
		print("You have " + str(self.quantity) + " of " + self.name)

	def buy_more(quantity, amount):
		self.quantity += quantity
		self.total += quantity * amount
		self.per_stock = self.total / self.quantity

	def sell(quantity, amount):
		if quantity > self.quantity:
			print("Not enough to sell")
		else:
			return
			# STUFF