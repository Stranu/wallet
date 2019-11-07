"""
To do:
Better display of dictionary;
AI to predict monthly gains and losses;

database = sorted(database, key=lambda data: time.mktime(time.strptime(data[3],"%d/%m/%Y")))
#sort the database based on the date
"""

import csv,os,time,getpass
USER_FILE = "user.dat"
USER_WALLET = "wallet.csv" #["Nome Conto","Entrate/Uscite","Causale","Data"]
#USER_WALLET = "test.csv" #For debug
USER_EXPIRATION = "expiration.csv" #["Nome Scadenza","Quantità","Descrizione","Periodico","Data"]
USER_GUESSES = "guess.csv" #["Nome Previsione","Quantità","Descrizione"]
CALENDAR = {1:31,2:28,3:31,4:30,5:31,6:30,7:31,8:31,9:30,10:31,11:30,12:31}

def retrieve(filename):
	if os.path.isfile(filename):
		temp_list = []
		with open(filename, newline='') as csvfile:
			content = csv.reader(csvfile, delimiter=',', quotechar='|')
			next(content)
			for row in content:
				temp_list.append(row)

			return temp_list
	else:
		print(f'\n!Il file -{filename}- non esiste!')
		input("\n\npremi INVIO per proseguire...")
		return []

def store(filename, mode, entry):
	"""Store the data -entry- in CSV format in the file called -filename- in mode -mode- 'can be -w-, -a- or wathever'"""
	if not os.path.isfile(filename):
		mode = 'w'
	with open(filename, mode, newline='') as csvfile:
			content = csv.writer(csvfile, delimiter=',',quotechar='|')
			content.writerow(entry)

def header(filename):
	"""return the first row of the csv as a list"""
	if os.path.isfile(filename):
		with open(filename, newline='') as csvfile:
			content = csv.reader(csvfile, delimiter=',', quotechar='|')
			header = next(content)
			return header
	else:
		print(f'\n!Il file -{filename}- non esiste!')
		input("\n\npremi INVIO per proseguire...")
		return []

def elements_names(filename):
	"""return a list containing all the different 'names'"""
	names = []
	if os.path.isfile(filename):
		with open(filename, newline='') as csvfile:
			content = csv.reader(csvfile, delimiter=',', quotechar='|')
			next(content)
			for row in content:
				if row[0] not in names:
					names.append(row[0])
			return names
	else:
		print(f'\n!Il file -{filename}- non esiste!')
		input("\n\npremi INVIO per proseguire...")
		return []

def time_selection(filename):
	while True:
		database = retrieve(filename)
		new_database = []
		starting_date = input(f"Scrivi la data di inizio [formato gg/mm/yyyy] o 'tutto': ")
		if starting_date!="tutto" and starting_date!="":
			finishing_date = input(f"Scrivi la data di fine [formato gg/mm/yyyy]: ")
			try:
				starting_date += " 00:00.00"
				finishing_date += " 23:59.59"
				starting_date = time.mktime(time.strptime(starting_date,"%d/%m/%Y %H:%M.%S")) #da string a struct a seconds
				finishing_date = time.mktime(time.strptime(finishing_date,"%d/%m/%Y %H:%M.%S"))
				break
			except:
				print("Date non inserite correttamente.")
		else:
			starting_date = time.mktime(time.strptime(database[0][3],"%d/%m/%Y %H:%M.%S")) #da string a struct a seconds
			finishing_date = time.time()
			break
	for row in database:
		row_date = time.mktime(time.strptime(row[3],"%d/%m/%Y %H:%M.%S"))
		if row_date>=starting_date and row_date<=finishing_date:
			new_database.append(row)
	return new_database

def postpone_expiration(expiration_db,erased):
	text_date = ""
	#Check if it needs to be stored again periodically
	if erased[4]!="n": #if it is not only for once
		period = erased[4].split("-")
		if period[0]=="s": #if it is indefinitelly periodical
			repetition = "s"
		else:
			repetition = int(period[0])-1 #else reduce the value by 1
		if repetition!=0: #if it is not already repeated itself for the last time
			new_period = str(repetition)+"-"+period[1]
			old_date = erased[3].split("/")
			if period[1]=="y":
				new_date = old_date[0]+"/"+old_date[1]+"/"+str(int(old_date[2])+1)
			elif period[1]=="m":
				old_month = int(old_date[1])
				if old_month<12: #if month minor than 12 (else +1 year and month =1). Than check if next month is shorter and if the day overflow
					if CALENDAR[old_month+1]<=int(old_date[0]): #if the next month has fewer days than the previous one
						new_day = str(CALENDAR[old_month+1])
					else:
						new_day = old_date[0]
					new_date = new_day+"/"+str(old_month+1)+"/"+old_date[2]
				else:
					new_date = old_date[0]+"/1/"+str(int(old_date[2])+1)
			elif period[1]=="d" or period[1]=="M": #transform the date to second, add the seconds corrispondondint to a day and go back to string
				one_day = 86400
				if period[1]=="M":#if it needs to be repeated exactly each 30 days
					one_day = one_day*30
				date_in_sec = time.mktime(time.strptime(erased[3]+" 23:59.59","%d/%m/%Y %H:%M.%S"))
				date_in_sec += one_day
				new_date = time.strftime("%d/%m/%Y",time.gmtime(date_in_sec))
			erased[3] = new_date
			erased[4] = new_period
			expiration_db.append(erased)
			expiration_db = sorted(expiration_db, key=lambda data: time.mktime(time.strptime(data[3],"%d/%m/%Y")))
			text_date = "Nuova data della scadenza: "+new_date+"\n"

	head = header(USER_EXPIRATION)
	store(USER_EXPIRATION,'w',head)
	for row in expiration_db:
		store(USER_EXPIRATION,'a',row)
	return text_date

def isnumber_check(text,mode=1):#check if the numeric value entered is in fact a numeric value. Return string o float based on -mode-
	while True:
		number = input(text)
		try:
			float(number)
			if mode==1:
				return number
			elif mode==2:
				return float(number)
		except:
			clear()
			print("Valore inserito non corretto\n")

def element_selection(element_list,text,mode=1):#if mode not 1, doesn't print --Torna al menù precedente--
	while True:
		print(text)
		for i,element in enumerate(element_list):
			print(f"{i+1}){element}")
		if mode==1:
			print(f"{len(element_list)+1})--Torna al menù precedente--")
		choice = input(": ")
		try:
			choice = int(choice)
		except:
			choice = -1
		if choice>0 and choice<=len(element_list)+1:
			return choice
		else:
			clear()
			print("\nHai digitato un input invalido!\n")

def print_db(element_list):#print the content of a list of lists in columns and rows as a DB.
	row_lenght = []
	temp_list = []
	max_l = 40
	for i in range(len(element_list[0])): #create a list with a number of element equals to the header.
		row_lenght.append(0)
	for x,row in enumerate(element_list):
		for i,r in enumerate(row):
			if len(r)>max_l:#if the text is longer than 40 character, the text get splitted and a new list is generated with empty value (except the splitted text), than inserted into the main list
				element_list[x][i] = r[:max_l]
				for e in range(len(row_lenght)):
					if e==i:
						temp_list.append(r[max_l:])
					else:
						temp_list.append("  ")
				element_list.insert(x+1,temp_list)
				temp_list = []
				r = r[:max_l]
			if len(r)>row_lenght[i]:
				row_lenght[i] = len(r)
	for row in element_list:
		for i,r in enumerate(row):
			left_spaces = int((row_lenght[i]-len(r))/2)
			right_spaces = int((row_lenght[i]-len(r))/2)+((row_lenght[i]-len(r))%2)
			print("|"+" "*(left_spaces)+r+" "*(right_spaces)+"|",end=" ")
		print()

#344
"""________________________________________________________________________________________________________"""
clear = lambda: os.system('cls' if os.name=='nt' else 'clear')
"""This lambda function clear the console"""
clear()

if not os.path.isfile(USER_FILE):
	"""if there is no user file saved"""
	user_name = input("Per iniziare, dimmi come ti dovrò chiamare da ora in poi...\n")
	print(f"Bene {user_name}, ora inserisci la tua password (assicurati di non avere guardoni alle spalle) [La password viene registrata anche se non appaiono lettere]...\n")
	while True:
		user_pass = getpass.getpass('Password: ')
		pass_confirm = getpass.getpass('Ripeti la password: ')
		if user_pass==pass_confirm:
			break
		else:
			print("Hai sbagliato a ridigitare la password. Riprendi da zero...")
	user_hint = input("Se vuoi impostare un suggerimento per permettermi di ricordarti la password quando l'avrai inevitabilmente dimenticata, digita ora (o premi invio per lasciare il campo vuoto)...\n")
	with open(USER_FILE,'w') as file:
		file.writelines([user_name+"\n",user_pass+"\n",user_hint])
	if not os.path.isfile(USER_WALLET):
		store(USER_WALLET,'w',["Nome Conto","Entrate/Uscite","Causale","Data"])
	if not os.path.isfile(USER_EXPIRATION):
		store(USER_EXPIRATION,'w',["Nome Scadenza","Quantità","Descrizione","Data","Periodico"])
	if not os.path.isfile(USER_GUESSES):
		store(USER_GUESSES,'w',["Nome Previsione","Quantità","Descrizione"])
	input("\nDati inseriti correttamente\npremi INVIO per proseguire...")
else:
	with open(USER_FILE) as file:
		user_name,user_pass,user_hint = file.readlines()
		user_name = user_name.strip()
		user_pass = user_pass.strip()
		user_hint = user_hint.strip()
	print(f"Sei {user_name}?")
	while True:
		pass_confirm = getpass.getpass('Inserisci la password: ')
		if pass_confirm==user_pass:
			break
		elif pass_confirm=="aiuto" or pass_confirm=="-aiuto-":
			print(f"\nIl tuo suggerimento è: {user_hint}")
		else:
			print("\nPassword errata...\n[Password dimenticata? scrivi -aiuto-]")
	clear()
	print("Bentornato, proseguiamo.")
	input("\n\npremi INVIO per proseguire...")



while True:
	clear()
	expiration_db = retrieve(USER_EXPIRATION)
	if len(expiration_db)>0:
		"""check if there is some expiration pending"""
		e = 0
		e_exp = 0
		exp_names = []
		exp_names_expired = []
		temp_time = time.localtime()
		for i,row in enumerate(expiration_db):
			exp_time = time.strptime(row[3],"%d/%m/%Y")
			"""Convert from string to time struct to compare month, year and day to see if there is some expiration to signal"""
			if temp_time.tm_mon==exp_time.tm_mon and temp_time.tm_year==exp_time.tm_year:
				"""Check if there are some expiration this month"""
				if temp_time.tm_mday<=exp_time.tm_mday:
					"""check if it is not already expired"""
					exp_names_expired.append(row[0])
					e+=1
					
			if time.mktime(exp_time)<time.time():
				"""Check if there are some expiration already expired"""
				exp_names_expired.append(row[0])
				e_exp+=1

		if e==1:
			print(f"\nHai {e} scadenza questo mese.")
			if len(exp_names)>0:
				print(exp_names)
		elif e>0:
			print(f"\nHai {e} scadenze questo mese.")
			if len(exp_names)>0:
				print(exp_names)
		if e_exp>0:
			print(f"\nScadenze scadute: {e_exp}")
			print(exp_names_expired)



	print("\nCosa desideri fare? [Digita il numero]")
	choice = input("""1)Entrate/Uscite\n2)Resoconto\n3)Ricerca\n4)Gestione scadenze\n5)Altre opzioni\n6)Esci\n:""")
	clear()
	
	if choice=="1":
		wallets = []
		wallets = elements_names(USER_WALLET)
		wallets.append("--Aggiungi un nuovo conto--")
		choice = element_selection(wallets,"Seleziona il conto per inserire le entrate/uscite:")
		if choice==len(wallets):
			wallet_name = input("Inserisci il nome del nuovo conto: ")
		elif choice==len(wallets)+1:
			continue
		else:
			wallet_name = wallets[choice-1]
		quantity = isnumber_check("Inserisci la quantità di denaro entrante o uscente: ")
		reason = input("Inserisci la casuale: ")

		store(USER_WALLET,'a',[wallet_name,quantity,reason,time.strftime("%d/%m/%Y %H:%M.%S")])
		input("\nDati inseriti correttamente\npremi INVIO per proseguire...")

	elif choice=="2":
		"""To make it better"""
		temp_time = time.localtime() #for expiration
		wallets = {}
		expiration = "    "
		guesses = "    "
		report_money = 0
		expiration_money = 0
		guesses_money = 0
		totalMoney = 0
		database_report = retrieve(USER_WALLET)
		database_expiration = retrieve(USER_EXPIRATION)
		database_guesses = retrieve(USER_GUESSES)

		for row in database_report:
			if row[0] not in wallets:
				wallets[row[0]] = 0
			wallets[row[0]] = wallets[row[0]]+float(row[1])
			report_money += float(row[1])

		for row in database_expiration:
			exp_time = time.strptime(row[3],"%d/%m/%Y")
			if temp_time.tm_mon==exp_time.tm_mon and temp_time.tm_year==exp_time.tm_year:
				"""check expiration for the current month"""
				if temp_time.tm_mday<exp_time.tm_mday:
					"""check if it is not already expired. Omit current day"""
					expiration_money += float(row[1])
					expiration += f"|{row[0]}={row[1]}| "
			if time.mktime(exp_time)<time.time():
				"""Check if there are some expiration already expired"""
				expiration_money += float(row[1])
				expiration += f"|{row[0]}={row[1]}| "

		for row in database_guesses:
			guesses_money += float(row[1])
			guesses += f"|{row[0]}={row[1]}| "

		totalMoney = report_money - expiration_money - guesses_money

		print(f"\nResoconto: {report_money}\n{wallets}")
		print(f"\n()Scadenze del mese e scadute: {expiration_money}\n{expiration}")
		print(f"()Previsione spese: {guesses_money}\n{guesses}")
		print(f"\nTotale utilizzabile: {totalMoney}")

		input("\n\npremi INVIO per proseguire...")

	elif choice=="3":
		"""Research fase."""
		while True:
			clear()
			print("Ricerca per:")
			choice = input("1)Nome del conto\n2)Casuale\n3)Guadagni/Spese\n4)Da data a data\n: ")
			clear()
			if choice=="1":
				wallets = []
				to_display = []
				to_display.append(header(USER_WALLET))
				tot = 0
				wallets = elements_names(USER_WALLET)#get the names of the various wallet used
				choice = element_selection(wallets,"Seleziona il nome del conto tra quelli esistenti:")
				if choice==len(wallets)+1:
					break
				database = time_selection(USER_WALLET)#ask for the time period and return a list containing the results
				clear()
				wallet_name = wallets[choice-1]
				for row in database:
					if row[0] in wallet_name:
						tot = tot+float(row[1])
						to_display.append(row)
						#print(row)
				print_db(to_display)
				print(f"Tot: {tot}")
				input("\n\npremi INVIO per proseguire...")
				break

			elif choice=="2":
				to_display = []
				to_display.append(header(USER_WALLET))
				why = input("Scrivi una parola o frase (non è case sensitive) per cui compiere la ricerca: ")
				database = time_selection(USER_WALLET)
				tot = 0
				clear()
				print(f"Termine di ricerca: {why.lower()}\n")
				for row in database:
					if why.lower() in row[2].lower():
						tot = tot+float(row[1])
						to_display.append(row)
						#print(row)
				print_db(to_display)
				print(f"Tot: {tot}")
				input("\n\npremi INVIO per proseguire...")
				break

			elif choice=="3":
				tot = 0
				while True:
					clear()
					print("Seleziona il range in cui cercare:")
					choice = input("1)Maggiore di...\n2)Minore di...\n3)Compreso tra...\n: ")
					clear()
					if choice=="1":
						to_display = []
						to_display.append(header(USER_WALLET))
						bigger_than = isnumber_check("Ricerca entrate/uscite maggiori di [Inserire un numero (es: 5 o 12.57), positivo o negativo]... ",2)
						database = time_selection(USER_WALLET)
						clear()
						print(f"\nRicerco entrate/uscite maggiori di: {bigger_than}")
						for row in database:
							if float(row[1])>=bigger_than:
								tot = tot+float(row[1])
								to_display.append(row)
						print_db(to_display)
						print(f"Tot: {tot}")
						input("\n\npremi INVIO per proseguire...")
						break
					elif choice=="2":
						to_display = []
						to_display.append(header(USER_WALLET))
						smaller_than = isnumber_check("Ricerca entrate/uscite minori di [Inserire un numero (es: 5 o 12.57), positivo o negativo]... ",2)
						database = time_selection(USER_WALLET)
						clear()
						print(f"\nRicerco entrate/uscite minori di: {smaller_than}")
						for row in database:
							if float(row[1])<=smaller_than:
								tot = tot+float(row[1])
								to_display.append(row)
						print_db(to_display)
						print(f"Tot: {tot}")
						input("\n\npremi INVIO per proseguire...")
						break
					elif choice=="3":
						to_display = []
						to_display.append(header(USER_WALLET))
						bigger_than = isnumber_check("Ricerca entrate/uscite comprese tra due valori [Inserire il primo numero (es: 5 o 12.57), positivo o negativo]... ",2)
						smaller_than = isnumber_check("[Inserire il secondo numero (es: 5 o 12.57), positivo o negativo]... ",2)
						database = time_selection(USER_WALLET)
						clear()
						print(f"\nRicerco entrate/uscite comprese tra {bigger_than} e {smaller_than}")
						for row in database:
							if float(row[1])>=bigger_than and float(row[1])<=smaller_than:
								tot = tot+float(row[1])
								to_display.append(row)
						print_db(to_display)
						print(f"Tot: {tot}")
						input("\n\npremi INVIO per proseguire...")
						break
				break

			elif choice=="4":
				to_display = []
				to_display.append(header(USER_WALLET))
				tot = 0
				database = time_selection(USER_WALLET)
				for row in database:
					tot = tot+float(row[1])
					to_display.append(row)
				print_db(to_display)
				print(f"Tot: {tot}")
				input("\n\npremi INVIO per proseguire...")
				break

	elif choice=="4":
		#["Nome Scadenza","Quantità","Descrizione","Data","Periodico"]
		while True:
			clear()
			choice = input("1)Inserisci nuova scadenza\n2)Elimina una scadenza\n3)Visualizza scadenze\n4)Paga scadenza\n5)Modifica scadenza\n6)Menù precedente\n: ")
			if choice=="1":
				clear()
				expiration_name = input("Digita il nome della scadenza da inserire... ")
				expiration_quantity = isnumber_check("Inserisci la quantità di soldi... ")
				expiration_why = input("Inserisci una descrizione... ")
				while True:
					expiration_date = input("Inserisci la data di scadenza [formato gg/mm/yyyy]... ")
					try:
						time.strptime(expiration_date,"%d/%m/%Y")
						break
					except:
						print("\nData non inserita correttamente, prestare attenzione al formato\n")
				while True:
					expiration_period = input("Se è una scadenza periodica, scrivi una delle sigle seguenti [y/m/M/d] (y=annuale, m=mensile sempre stesso giorno, M=ogni 30 giorni esatti, d=giornaliera), altrimenti [n] se non è periodica... ")
					if expiration_period=="y" or expiration_period=="m" or expiration_period=="M" or expiration_period=="d" or expiration_period=="n":
						break
					else:
						clear()
						print("\nNon hai inserito una sigla valida. Riprova.\n")
				expiration_repetition = ""
				if expiration_period!="n":
					expiration_repetition = input("Quante volte? [Inserire un numero di ripetizioni o [s] se da ripetersi indefinitivamente]: ")
					expiration_repetition = expiration_repetition+"-"
				expiration_header = header(USER_EXPIRATION)
				database = retrieve(USER_EXPIRATION)
				database.append([expiration_name,expiration_quantity,expiration_why,expiration_date,expiration_repetition+expiration_period])
				database = sorted(database, key=lambda data: time.mktime(time.strptime(data[3],"%d/%m/%Y")))
				#sorted the database based on the date

				store(USER_EXPIRATION,'w',expiration_header)
				for row in database:
					store(USER_EXPIRATION,'a',row)

				#store(USER_EXPIRATION,'a',[expiration_name,expiration_quantity,expiration_why,expiration_date,expiration_repetition+expiration_period])
				input("\n\npremi INVIO per proseguire...")
				break
			elif choice=="2":
				clear()
				database = retrieve(USER_EXPIRATION)
				text_date = ""
				choice = element_selection(database,"Quale scadenza voi eliminare? [Inserisci un numero]:")
				if choice<len(database)+1:
					erased = database.pop(int(choice)-1)

					if erased[4]!="n": #if it's not a periodical expiration
						while True:
							choice = input("1)Eliminare solo questa ricorrenza\n2)Eliminare tutte le ricorrnze\n: ")
							if choice=="1" or choice=="2":
								break
							else:
								clear()
								print("\nHai digitato un input invalido!\n")
						if choice=="2":
							erased[4] = "n"
					text_date = postpone_expiration(database,erased)

					clear()
					print(f"La scadenza -{erased[0]}- è stata eliminata")
					print(text_date)
					input("\npremi INVIO per proseguire...")
				break
			elif choice=="3":
				clear()
				to_display = []
				to_display.append(header(USER_EXPIRATION))
				database = retrieve(USER_EXPIRATION)
				for row in database:
					to_display.append(row)
				print_db(to_display)

				input("\n\npremi INVIO per proseguire...")
			elif choice=="4":
				clear()
				expiration_db = retrieve(USER_EXPIRATION)
				text_date = ""
				text_old_date = "(Scadenza del: "
				choice = element_selection(expiration_db,"Quale scadenza voi pagare? [Inserisci un numero]: ")
				if int(choice)<len(expiration_db)+1:
					erased = expiration_db.pop(int(choice)-1)
					text_old_date = text_old_date + erased[3] + ")"

					text_date = postpone_expiration(expiration_db,erased)

					wallets = elements_names(USER_WALLET)
					choice = element_selection(wallets,"Seleziona il conto dove inserire il pagamento:",2)
					wallet_name = wallets[choice-1]
					#now store the popped expiration into the chosen wallet
					store(USER_WALLET,'a',[wallet_name,str(float(erased[1])*(-1)),erased[0]+" "+erased[2]+" "+text_old_date,time.strftime("%d/%m/%Y %H:%M.%S")])
					clear()
					print(f"La scadenza -{erased[0]}- è stata pagata sul conto -{wallet_name}-\n{text_date}")
					input("premi INVIO per proseguire...")
				break
			elif choice=="5":
				clear()
				database = retrieve(USER_EXPIRATION)
				text_date = ""
				choice = element_selection(database,"Quale scadenza voi modificare? [Inserisci un numero]:")
				if choice<len(database)+1:
					to_change = database.pop(int(choice)-1)
					while True:
						period = "nessuna"
						if to_change[4]!="n":
							periodicity = to_change[4].split("-")
							if periodicity[1]=="y":
								period = "annuale"
							elif periodicity[1]=="m":
								period = "mensile"
							elif periodicity[1]=="M":
								period = "ogni 30 giorni"
							elif periodicity[1]=="d":
								period = "giornaliera"
							if periodicity[0]!="s":
								period += " ("+periodicity[0]+" ricorrenze restanti)"
						clear()
						print(f"Cosa vuoi cambiare?")
						print(f"1)Nome: {to_change[0]}")
						print(f"2)Quantità: {to_change[1]}")
						print(f"3)Descrizione: {to_change[2]}")
						print(f"4)Data: {to_change[3]}")
						print(f"5)Periodicità: {period}")
						print("6)--Termina modifica e salva--")
						print("7)--Torna al menù precedente senza salvare--")
						choice = input(": ")
						if choice=="1":
							to_change[0] = input("Digita il nuovo nome della scadenza... ")
						elif choice=="2":
							to_change[1] = isnumber_check("Inserisci la nuova quantità di soldi [Inserire un numero (es: 5 o 12.57), positivo o negativo]... ")
						elif choice=="3":
							to_change[2] = input("Inserisci una nuova descrizione... ")
						elif choice=="4":
							while True:
								expiration_date = input("Inserisci la nuova data di scadenza [formato gg/mm/yyyy]... ")
								try:
									time.strptime(expiration_date,"%d/%m/%Y")
									break
								except:
									print("\nData non inserita correttamente, prestare attenzione al formato\n")
							to_change[3] = expiration_date
						elif choice=="5":
							while True:
								expiration_period = input("Se è una scadenza periodica, scrivi una delle sigle seguenti [y/m/M/d] (y=annuale, m=mensile sempre stesso giorno, M=ogni 30 giorni esatti, d=giornaliera), altrimenti [n] se non è periodica... ")
								if expiration_period=="y" or expiration_period=="m" or expiration_period=="M" or expiration_period=="d" or expiration_period=="n":
									break
								else:
									clear()
									print("\nNon hai inserito una sigla valida. Riprova.\n")
							expiration_repetition = ""
							if expiration_period!="n":
								expiration_repetition = input("Quante volte? [Inserire un numero di ripetizioni o [s] se da ripetersi indefinitivamente]: ")
								expiration_repetition = expiration_repetition+"-"+expiration_period
							to_change[4] = expiration_repetition
						elif choice=="6":
							expiration_header = header(USER_EXPIRATION)
							database.append(to_change)
							database = sorted(database, key=lambda data: time.mktime(time.strptime(data[3],"%d/%m/%Y")))
							#sorted the database based on the dates
							store(USER_EXPIRATION,'w',expiration_header)
							for row in database:
								store(USER_EXPIRATION,'a',row)
							clear()
							input("Modifiche eseguite correttamente.\n\npremi INVIO per proseguire...")
							break
						elif choice=="7":
							break
				break
			elif choice=="6":
				break

	elif choice=="5":
		while True:
			clear()
			choice = input("1)Previsioni spese\n2)Modifica nome di un conto\n3)Trasferimento tra due conti\n4)Cambia password\n5)Menù precedente\n: ")
			clear()
			if choice=="1":
				#["Nome Previsione","Quantità","Descrizione"]
				while True:
					clear()
					choice = input("1)Inserisci Previsione\n2)Elimina Previsioni\n3)Visualizza Previsioni\n4)Modifica Previsione\n5)Menù precedente\n: ")
					if choice=="1":
						clear()
						guesses_name = input("Digita il nome sintetico della previsione da inserire... ")
						guesses_quantity = isnumber_check("Inserisci la quantità di soldi... ")
						guesses_why = input("Inserisci una descrizione completa... ")
						store(USER_GUESSES,'a',[guesses_name,guesses_quantity,guesses_why])
						input("\nDati inseriti correttamente\npremi INVIO per proseguire...")
						break
					elif choice=="2":
						clear()
						database = retrieve(USER_GUESSES)
						choice = element_selection(database,"Quale previsione voi eliminare? [Inserisci un numero]:")
						if choice<len(database)+1:
							erased = database.pop(int(choice)-1)
							head = header(USER_GUESSES)
							store(USER_GUESSES,'w',head)
							for row in database:
								store(USER_GUESSES,'a',row)
							clear()
							print(f"->{erased}<-\n è stata eliminata")
							input("premi INVIO per proseguire...")
						break
					elif choice=="3":
						clear()
						to_display = []
						to_display.append(header(USER_GUESSES))
						database = retrieve(USER_GUESSES)
						print(header(USER_GUESSES))
						for row in database:
							to_display.append(row)
						print_db(to_display)
						input("\n\npremi INVIO per proseguire...")
					elif choice=="4":
						clear()
						database = retrieve(USER_GUESSES)
						text_date = ""
						while True:
							print("Quale previsione voi modificare? [Inserisci un numero]:")
							for i,row in enumerate(database):
								print(f"{i+1}-> {row}")
							print(f"{len(database)+1}-> --Nessuna--")
							choice = input(": ")
							try:
								choice = int(choice)
							except:
								choice = -1
							if choice>0 and choice<=len(database)+1:
								break
							else:
								clear()
								print("\nHai digitato un input invalido!\n")
						if int(choice)<len(database)+1:
							to_change = database.pop(int(choice)-1)
							while True:
								clear()
								print(f"Cosa vuoi cambiare?")
								print(f"1)Nome: {to_change[0]}")
								print(f"2)Quantità: {to_change[1]}")
								print(f"3)Descrizione: {to_change[2]}")
								print("4)--Termina modifica e salva--")
								print("5)--Torna al menù precedente senza salvare--")
								choice = input(": ")
								if choice=="1":
									to_change[0] = input("Digita il nuovo nome della scadenza... ")
								elif choice=="2":
									to_change[1] = isnumber_check("Inserisci la nuova quantità di soldi [Inserire un numero (es: 5 o 12.57), positivo o negativo]... ")
								elif choice=="3":
									to_change[2] = input("Inserisci una nuova descrizione... ")
								elif choice=="4":
									expiration_header = header(USER_GUESSES)
									database.append(to_change)
									store(USER_GUESSES,'w',expiration_header)
									for row in database:
										store(USER_GUESSES,'a',row)
									clear()
									input("Modifiche eseguite correttamente.\n\npremi INVIO per proseguire...")
									break
								elif choice=="5":
									break
						break
					elif choice=="5":
						break
				break
				clear()
				input("\n\npremi INVIO per proseguire...")
				break

			elif choice=="2":
				wallets = []
				wallets = elements_names(USER_WALLET)
				choice = element_selection(wallets,"Seleziona il nome del conto da modificare:")
				if choice==len(wallets)+1:
					break
				else:
					wallet_name = wallets[choice-1]
					new_wallet_name = input("Inserisci il nuovo nome del conto: ")
					database = retrieve(USER_WALLET)
					head = header(USER_WALLET)
					store(USER_WALLET,'w',head)
					for row in database:
						if row[0]==wallet_name:
							row[0] = new_wallet_name
						store(USER_WALLET,'a',row)
					print(f"\nIl conto -{wallet_name}- è stato rinominato con successo come -{new_wallet_name}-")
					input("\n\npremi INVIO per proseguire...")

				break

			elif choice=="3":
				wallets = elements_names(USER_WALLET)
				choice1 = element_selection(wallets,"Seleziona il nome del conto da cui prelevare:")
				if choice1==len(wallets)+1:
					break
				choice2 = element_selection(wallets,"Seleziona il nome del conto su cui depositare:")
				if choice2==len(wallets)+1:
					break
				wallet_name1 = wallets[choice1-1]
				wallet_name2 = wallets[choice2-1]

				quantity = isnumber_check("Inserisci la quantità di denaro da trasferire [Numero positivo, es: 5 o 12.5]: ")
				reason = "Trasferimento dal conto -"+wallet_name1+"- al conto -"+wallet_name2+"-"
				store(USER_WALLET,'a',[wallet_name1,str(int(quantity)*(-1)),reason,time.strftime("%d/%m/%Y %H:%M.%S")])
				store(USER_WALLET,'a',[wallet_name2,quantity,reason,time.strftime("%d/%m/%Y %H:%M.%S")])
				input("\nDati inseriti correttamente\npremi INVIO per proseguire...")
				break
			elif choice=="4":
				choice = input("Vuoi davvero cambiare la password? [Y/N] ")
				if choice.lower()=="y":

					with open(USER_FILE) as file:
						user_name,user_pass,user_hint = file.readlines()
						user_name = user_name.strip()
						user_pass = user_pass.strip()
						user_hint = user_hint.strip()
						print(f"Conferma la tua identità, {user_name}.")
					while True:
						pass_confirm = getpass.getpass('Inserisci la vecchia password: ')
						clear()
						if pass_confirm==user_pass:
							break
						elif pass_confirm=="aiuto" or pass_confirm=="-aiuto-":
							print(f"\nIl tuo suggerimento è: {user_hint}")
						else:
							print("\nPassword errata...\n[Password dimenticata? scrivi -aiuto-]")

					while True:
						user_pass = getpass.getpass('Inserisci la nuova password: ')
						pass_confirm = getpass.getpass('Ripeti la nuova password: ')
						if user_pass==pass_confirm:
							break
						else:
							clear()
							print("Hai sbagliato a ridigitare la password. Riprendi da zero...")
					clear()
					choice = input(f"Vuoi cambiare anche il suggerimento?\nAttualmente è -{user_hint}- [Y/N] ")
					if choice.lower()=="y":
						user_hint = input("Inserisci il nuovo suggerimento: ")

					with open(USER_FILE,'w') as file:
						file.writelines([user_name+"\n",user_pass+"\n",user_hint])

					input("\nPassword sostituita correttamente\npremi INVIO per proseguire...")
				else:
					input("\npremi INVIO per proseguire...")
				break
			elif choice=="5":
				break

	elif choice=="6":
		clear()
		print("Arrivederci")
		input("\n\npremi INVIO per proseguire...")
		break
