class mySorts:

	# Each is a sorted list of [num, abbrv] for each stock
	def __init__(self, p_change, pert_change, cur_price):
		self.price_change = p_change
		self.percent_change = pert_change
		self.cur_price = cur_price

	# Returns a list of [price, abbrv] for each stock
	def getCur_price(self):
		return self.cur_price

	# Returns a list of [percent_change, abbrv] for each stock
	def getPer_change(self):
		return self.percent_change

	# Returns a list of [price_change, abbrv] for each stock
	def getP_change(self):
		return self.price_change