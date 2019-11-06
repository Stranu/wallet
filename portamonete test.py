import csv,os,time

FILENAME = "test.csv"

def retrieve(filename):
	with open(filename, newline='') as csvfile:
		content = csv.reader(csvfile, delimiter=',', quotechar='|')
		header = next(content)
		for row in content:
			print(', '.join(row))

def store(filename, mode, entry):
	"""Store the data -entry- in CSV format in the file called -filename- in mode -mode- 'can be -w-, -a- or wathever'"""
	with open(filename, mode, newline='') as csvfile:
			content = csv.writer(csvfile, delimiter=',',quotechar='|')
			content.writerow(entry)

choice = input("Read or write? [r/w]\n")
if choice=="r":
	retrieve(FILENAME)
else:
	"""if the file does not exist, creates the header and then proceed"""
	if not os.path.isfile(FILENAME):
		store(FILENAME,'w',['Nome Conto','Entrate/Uscite','Causale','Data'])

	while True:
		choice = input("Do you want to insert a new entry? [y/n]\n")
		if choice =="n":
			print("Ok bye")
			break
		else:
			name = input("Account name: ")
			money = input("How much? ")
			why = input("Why? ")
			entry = [name,money,why,time.time()]
			store(FILENAME,'a',entry)

with open(FILENAME, newline='') as csvfile:
	content = csv.reader(csvfile, delimiter=',', quotechar='|')
	header = next(content)
	totalMoney = 0
	for row in content:
		totalMoney = totalMoney+int(row[1])
	print(f"\nTot: {totalMoney}")
