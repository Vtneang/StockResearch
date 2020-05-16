import urllib.request
import requests
from bs4 import BeautifulSoup
import re

link = "https://finance.yahoo.com/quote/AAC?ltr=1"
idk = "D(ib) Mt(-5px) Mend (20px) Maw(56%)--tab768 Maw(52%) Ov(h) smartphone_Maw(85%) smartphone_Mend(0px)"
content = requests.get(link)
soup = BeautifulSoup(content.text, "html.parser")
trial = soup.find("div", {"class" : idk})
print(trial)
name = ""
for i in trial:
	for j in i.text.split():
		if re.match("[A-Z]{1}[a-z]+$", j):
			name += j + " "
print(name.strip())