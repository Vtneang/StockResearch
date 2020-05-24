import random

idk = []

for i in range(10000):
	idk.append([random.randint(0,10000), "CVX"])


def quicksort(A):
	if len(A) <= 1:
		return A
	lower = []
	higher = []
	cur = []
	for l in A:
		num = l[0]
		if num < A[0][0]:
			lower.append(l)
		elif num > A[0][0]:
			higher.append(l)
		else:
			cur.append(l)
	left = quicksort(lower)
	right = quicksort(higher)
	cur.append(A[0])
	return left + cur + right

print(quicksort(idk))
