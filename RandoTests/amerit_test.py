import urllib.request
import requests
from bs4 import BeautifulSoup
import re



web = "https://www.google.com/search?q=CVX+stocks&rlz=1C5CHFA_en139r230&oq=cvx&aqs=chrome"
data_class = "BNeawe iBp4i Ap7Wnd"
time_stamp_class = "ZINbbc xpd O9g5cc uUPGi"
requ = requests.get(web)
soupy = BeautifulSoup(requ.text, "html.parser")
con = soupy.find("body").find_all("div", {"class", "ZINbbc xpd O9g5cc uUPGi"})
count = 0
#for j in con:
#	print(count)
#	count += 1
#	print(j)
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


x = con[1].text.split()
name = ""
time = ""
pos = 0
for i in x:
	if i =="/":
		name.strip()
		pos = count + 2
		break
	name += i + " "
	count += 1
price = x[pos][5:]
pos += 1
price_change = x[pos]
perct_change = price_change[0]
pos += 1
perct_change_total = x[pos]
for i in range(1, len(perct_change_total)):
	if perct_change_total[i] == ")":
		perct_change.replace("(", "")
		break
	perct_change += perct_change_total[i]
time = x[-9] + x[-8]
print(name)
print(price)
print(price_change)
print(perct_change)
print(time)



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