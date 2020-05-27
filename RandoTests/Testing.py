import datetime

x = datetime.datetime.now().strftime("%m/%d/%Y")
print(x)
y = int(x[3:5]) - 1
z = x[0:2]
year = x[6:]
yes = z + "/" + str(y) + "/" + year
print(yes)
