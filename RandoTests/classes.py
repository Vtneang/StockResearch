from datapackage import Package
import re

package = Package('https://datahub.io/core/nyse-other-listings/datapackage.json')

# print list of all resources:
#print(package.resource_names)

keep = True
keeper = []
# print processed tabular data (if exists any)
for resource in package.resources:
	if resource.descriptor['datahub']['type'] == 'derived/csv' and keep:
		data = resource.read()
		keep = False
		for stock in data:
			if stock[0].isalpha():
				keeper.append(stock[0])
		print(keeper)