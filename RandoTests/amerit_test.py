import urllib.request
import requests
from bs4 import BeautifulSoup
import re
import random
import string



web = "https://www.google.com/search?q=CVX+stocks" + "&rlz=1C5CHFA_en139r230&oq=cvx&aqs=chrome"
goog_begin = "https://www.google.com/search?q="
goog_mid = "+stocks&rlz="
goog_end = "=chrome"
data_class = "BNeawe iBp4i Ap7Wnd"
time_stamp_class = "ZINbbc xpd O9g5cc uUPGi"
requ = requests.get(web)
soupy = BeautifulSoup(requ.text, "html.parser")
con = soupy.find("body").find_all("div")
count = 0
for j in con:
	print(count)
	count += 1
	print(j)
#print(con[1].text.split())
#for jk in con:
#	x = jk.find_all("div", {"class", "ZINbbc xpd 09g5cc uUPGi"})
#	if x is not None:
#		for idk in x:
#			for kk in idk.text.split():
#				print(kk)
#c = con[103].text
#for data in c.split():
#	print(data)

def google_search(abbrv):
	after_mid = "".join(random.choice(string.ascii_letters) for x in range(random.randrange(3,8)))
	link = goog_begin + abbrv + goog_mid + after_mid + goog_end
	req = requests.get(link)
	souper = BeautifulSoup(req.text, "html.parser")
	content = souper.find("body").find_all("div", {"class", time_stamp_class})
	print(content)
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
		trial = float(price)
		print(name)
		print(price)
		print(price_change)
		print(perecent)
		print(time + "\n")
	except Exception as e:
		print(abbrv + " had an error in something " + str(e))


stocks = ["ACB", "BA", "CVX", "SHRMF", "NBR", "HTZ", "GE"]
#for stock in stocks:
#	google_search(stock)

#### CHECK DATA FOR FLOATS (EXCEPTIONS = VALUE ERROR) TO DOUBLE CHECK COMPLETION ####



######## GETING THE TIME STAMP FROM GOOGLE ##########
#con = soupy.find("body").find_all("div", {"class", "ZINbbc xpd O9g5cc uUPGi"})
#keep = []
#for i in con:
#	x = i.find_all("div", {"class", "BNeawe uEec3 AP7Wnd"})
#	if x is not None:
#		for jk in x:
#			for kk in jk.text.split():
#				keep.append(kk)
#time = keep[2]
#indic = keep[3]
#total = time + indic
#print(total)