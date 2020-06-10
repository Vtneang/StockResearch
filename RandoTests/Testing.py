import urllib.request
import requests
from bs4 import BeautifulSoup
import re
import random
import string
import re


web = "https://free-proxy-list.net/"
regex_form = "(\\d+\.){3}(\\d+.+)"
proxies = []
link_begin = "https://finance.yahoo.com/quote/"
link_ending = "?ltr=1"

requ = requests.get(web)
soupy = BeautifulSoup(requ.text, "html.parser")
content = soupy.select("tr")
for i in content:
	#print(str(i) + "\n")
	try:
		if i.find_all("td", class_="hx")[0].text == "yes":
			proxies.append(str(i.find_all("td")[0].text) + ":" + str(i.find_all("td")[1].text))
	except:
		c = ""


def fake_search(abbrv):
	link = link_begin + abbrv + link_ending
	for i in range(len(proxies)):
		prox = proxies[i]
		try:
			content = requests.get(link, proxies={"http": "http://" + prox, "https": "https://" + prox}, timeout=2)
			soupy = BeautifulSoup(content.text, "html.parser")
			print(str(i) + " had a sucess + " + "\n")
			print(soupy.text)
		except Exception as e:
			print(str(i) + " had a problem " + str(e))

def idk_search(abbrv):
	link = link_begin + abbrv + link_ending
	content = requests.get(link, proxies={"http": "http://" + "168.232.188.209:40968", "https": "https://" + "168.232.188.209:40968"})
	soupy = BeautifulSoup(content)
	print(soupy.text)

fake_search("CVX")


