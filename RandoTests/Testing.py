from googlesearch import *
import webbrowser
from datapackage import Package

package = Package('https://datahub.io/core/nyse-other-listings/datapackage.json')

# print list of all resources:
print(package.resource_names)

# print processed tabular data (if exists any)
#for resource in package.resources:
#    if resource.descriptor['datahub']['type'] == 'derived/csv':
#        print(resource.read())
#to search, will ask search query at the time of execution
#query = input("Input your query:")
searches = ["SHRMF"]
#iexplorer_path = r'C:\Program Files (x86)\Internet Explorer\iexplore.exe %s'
chrome_path = r'C:\Program Files (x86)\Google\Chrome\Application\chrome.exe %s'
for i in range(len(searches)):
	for url in search(searches[i], tld="co.in", num=1, stop = 1, pause = 1):
		webbrowser.open("https://google.com/search?q=%s" % searches[i])