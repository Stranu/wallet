import csv,os,time
OLD_DATA = "old_data 2015.csv" #["Nome Conto","Entrate/Uscite","Causale","Data"]

def store(filename, mode, entry):
	"""Store the data -entry- in CSV format in the file called -filename- in mode -mode- 'can be -w-, -a- or wathever'"""
	if not os.path.isfile(filename):
		mode = 'w'
	with open(filename, mode, newline='') as csvfile:
			content = csv.writer(csvfile, delimiter=',',quotechar='|')
			content.writerow(entry)

with open("movimenti 13-06-15.txt") as database:
	lines = database.readlines()

#print(lines[1].replace("-","/"))
#delimiter = "______________________________________________________________________________________"
#confirm = "--------------------------------------------------------------------------------------"
confirm = "--------------------------------------------------"
flag = False
counter = 0
carta = 0
monete = 0
totale = 0
causa = ""
data = ""
oresecmin = ""

if not os.path.isfile(OLD_DATA):
	store(OLD_DATA,'w',["Nome Conto","Entrate/Uscite","Causale","Data"])

for row in lines:
	row = row.strip()

	if flag:
		if counter==1:
			print(row.replace("-","/"))
			temp_data = time.strptime(row,"%Y-%m-%d")
			data = time.strftime("%d/%m/%Y",temp_data)
		if counter==2:
			oresecmin = row[:5] + "." + row[6:]
			print(oresecmin)
			data += " "+oresecmin
		if "-carta=" in row:
			print(row[8:])
			carta = row[8:]
		if "-monete=" in row:
			print(row[9:])
			monete = row[9:]
		if "totale=" in row:
			print(row[8:])
			totale = row[8:]
		if "causa:" in row:
			print(row[7:])
			causa = row[7:]
		counter+=1
		if confirm in row and counter>4:
			print(f"___{data} carta: {carta} monete: {monete} causa: {causa}")
			#["Nome Conto","Entrate/Uscite","Causale","Data"]
			"""if float(carta)!=0:
				store(OLD_DATA,'a',["Portafogli",carta,causa,data])
			if float(monete)!=0:
				store(OLD_DATA,'a',["Portafogli",monete,causa,data])"""
			store(OLD_DATA,'a',["Portafogli",totale,causa,data])
			counter = 0
			carta = 0
			monete = 0
			totale = 0
			causa = ""
			data = ""



	elif confirm in row:
		flag = True
		#counter +=1
		print(counter,"Start")
	else:
		flag = False