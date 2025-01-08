with open('discrep.txt', "rb") as f:
	raws = f.read()

print(raws)


for raw in raws:
	print(raw)

	temp = ""

	for r in raw:
		temp += str(ord(r))
		temp += ","
	print(temp)

