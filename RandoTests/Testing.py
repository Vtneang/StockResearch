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
	for j in i.text.split():
		if re.match(regex_form, j):
			for pos in range(len(j)):
				if re.match("[a-z]", j[pos]) or re.match("[A-Z]", j[pos]):
					proxies.append(j[0:pos])
					break
				else:
					pos += 1


def fake_search(abbrv):
	link = link_begin + abbrv + link_ending
	content = requests.get(link, proxies={"http": proxies[1], "https": proxies[1]})
	soupy = BeautifulSoup(content)
	print(soupy.text)


fake_search("CVX")