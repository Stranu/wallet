USER_WALLET = "wallet.csv"
with open(USER_WALLET) as file:
	content = file.readlines()
for row in content:
	print(row.strip())

with open("wallet3.csv",'w') as file:
	for row in content:
		file.write(row)