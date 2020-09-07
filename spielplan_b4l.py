import numpy as np
import time
import plotly.graph_objects as go
import pandas
import plotly.express as px
import os
import csv
import yaml
from random import shuffle
#from pydrive.drive import GoogleDrive 
#from pydrive.auth import GoogleAuth 


class Spielplan():
	def __init__(self, config):
		startzeit = config.get("startzeit")
		datum = config.get("datum")
		self.startzeit = self.str_to_time(startzeit, datum)
		startzeit_finale = config.get("finals_start")
		self.startzeit_finale = self.str_to_time(startzeit_finale, datum)
		self._preferred_groupsize = config.get("gewuenschte_gruppengroesse")
		self.finale = config.get("finale")
		self.plaetze = config.get("plaetze")
		self.spielzeit = config.get("spielzeit")
		self.pause = config.get("pause")
		self.folder = config.get("folder")

	def str_to_time(self, startzeit, datum):
		startzeit = datum + " " + startzeit
		startzeit = time.mktime(time.strptime(startzeit, "%d.%m.%Y %H:%M"))
		startzeit /= 60
		return startzeit

	def write_csv(self, file_name, values):
		headers = list(values.keys())
		with open("tables/"+file_name, 'w') as csv_file:
			writer = csv.writer(csv_file, dialect='excel', quoting=csv.QUOTE_NONNUMERIC)
			writer.writerow(headers)
			for i in range(len(values[headers[0]])):
				row = []
				for header in headers:
					if i < len(values[header]):
						row.append(values[header][i])
				writer.writerow(row)


	def read_csv(self, file_name):
		values = {}
		with open("tables/"+file_name, 'r') as csv_file:
			reader = csv.reader(csv_file, dialect='excel')#, quoting=csv.QUOTE_NONNUMERIC)
			for i, row in enumerate(reader):
				if i == 0:
					headers = row
				else:
					for j in range(len(row)):
						values.setdefault(headers[j], []).append(row[j])
		return values



	def create_table(self, table, title):
		"""  """
		headers = list(table.keys())
		print(headers)
		cell_values = [table[key] for key in headers]
		if len(table[headers[0]]) < 6:
			height = 300
		else:
			height = len(table[headers[0]]) * 45
		fig = go.Figure(data = [go.Table(header=dict(values=headers), cells=dict(values=cell_values))])
		fig.update_layout(title=title, height=height)
		image_name = "_".join(title.lower().split(" "))+".jpeg"
		path = os.path.join(self.folder, image_name)
		fig.write_image(path)
		return image_name

	def finale_name(self, finale):
		""" """
		if finale == 8:
			return "Achtelfinale"
		elif finale == 4:
			return "Viertelfinale"
		elif finale == 2:
			return "Halbfinale"
		elif finale == 1:
			return "Finale"


	def get_teams(self):
		self.teams = self.read_csv("teams.csv")
		#print(self.teams)
		anzahl_teams = len(self.teams["Team"])
		print("Es gibt ", anzahl_teams, " Teams.")
		number_groups = int(anzahl_teams / self._preferred_groupsize)
		print(f"Es gibt {number_groups} Gruppen.")
		anzahl_dritte = (self.finale-number_groups)*2
		print("Damit kommen die besten",anzahl_dritte,"Dritten weiter.")
		return anzahl_dritte

	def get_toepfe(self):
		""" Lostoepfe - es gibt so viele Toepfe wie die max_i(len(group_i)); 
		der erste Topf darf höchstens ein Element mehr haben als jeder andere und nicht weniger """

		self.toepfe = {}
		team_list = self.teams["Team"]
		topf_list = self.teams["Topf"]
		for i, team in enumerate(team_list):
			topf = self.teams
			topf_name = 'Topf ' + str(topf_list[i])
			self.toepfe.setdefault(topf_name, []).append(team)

	def generate_groups(self):
		""" Erstelle die Gruppen """
		self.groups = {}
		i = 0
		np.random.seed(42)
		toepfe_keys = list(self.toepfe.keys())

		while len(self.toepfe[toepfe_keys[0]])>0:
			i += 1
			group_name = 'Gruppe ' + str(i)
			
			size_randoms = 0
			for key in toepfe_keys:
				if len(self.toepfe[key]) > 0:
					size_randoms += 1
			
			randoms = [np.random.randint(len(self.toepfe[toepfe_keys[j]])) for j in range(size_randoms)]
			group = []
			for k, random in enumerate(randoms):
				group.append(self.toepfe[toepfe_keys[k]].pop(random))
			self.groups[group_name] = group
		self.write_csv("groups.csv", self.groups)

	def get_group(self, team):
		if ". " in team: 
			return team.split(". ")[1]
		for group_name, group in self.groups.items():
			if team in group:
				return group_name
		

	def load_results(self):
		pass
		#self.results = #read csv with results and translate it into a dict

	def save_groups(self):
		pass

	def load_groups(self):
		self.groups = self.read_csv("groups.csv") 

	def determine_spielplan_vorrunde(self):
		self.load_groups()
		pairings = {}
		for group_name, group in self.groups.items():
			pairings[group_name] = []
			teams_1_played  = []
			for team1 in group:
				teams_1_played.append(team1)
				for team2 in group:
					if team2 not in teams_1_played:
						pairing = [team1, team2]
						pairings[group_name].append(pairing)
		#print("Gruppenpaarungen innerhalb der Gruppen: ", pairings,"\n")  

		# mische die Paarungen innerhalb jeder Gruppe

		for group_name in pairings:
			#print(pairings[group_name])
			shuffle(pairings[group_name])
			#print(pairings[group_name])

		#print("Gruppenpaarungen innerhalb der Gruppen: ", pairings) 

		pairings_sorted = []

		condition = True
		i = 0
		while condition:
			condition = False
			for group_name, group_pairings in pairings.items():
				if len(group_pairings) > i:
					pairings_sorted.append(pairings[group_name][i])
					condition = True
			i += 1


		aktuelle_zeit = self.startzeit
		spielplan_vorrunde = {}
		spielplan_vorrunde_table = {}   

		for i, game in enumerate(pairings_sorted):
			zeit = time.asctime(time.localtime(aktuelle_zeit * 60)).split(" ")[-2]
			spielplan_vorrunde.setdefault(zeit, []).append(game)
			aktueller_platz = i % self.plaetze + 1
			spielplan_vorrunde_table.setdefault("Platz", []).append(aktueller_platz)
			if aktueller_platz == self.plaetze:
				aktuelle_zeit += self.spielzeit + self.pause
					
		for zeit, spiele in spielplan_vorrunde.items():
			for spiel in spiele:
				spielplan_vorrunde_table.setdefault("Uhrzeit", []).append(zeit[:-3])
				spielplan_vorrunde_table.setdefault("Heim", []).append(spiel[0])
				spielplan_vorrunde_table.setdefault("Gast", []).append(spiel[1])
		self.create_table(spielplan_vorrunde_table, "Spielplan Vorrunde")
		ergebnisse_vorrunde = spielplan_vorrunde_table
		ergebnisse_vorrunde["Punkte Heim"] = []
		ergebnisse_vorrunde["Punkte Gast"] = []
		self.write_csv("ergebnisse_vorrunde.csv",ergebnisse_vorrunde)
        

	def determine_table(self):
		""" Ergebnisse und Tabellen """

		self.load_groups()
		self.vorrunde_ergebnisse = self.read_csv("ergebnisse_vorrunde.csv")
		anzahl_dritte = self.get_teams()
		results = {}
		for i in range(len(self.vorrunde_ergebnisse["Uhrzeit"])):
			if not (self.vorrunde_ergebnisse["Punkte Heim"][i]== "" or self.vorrunde_ergebnisse["Punkte Gast"][i]==""):
				#for teams, ergebnis in self.vorrunde_ergebnisse.items():
				#if len(ergebnis)==2:
				team1 = self.vorrunde_ergebnisse["Heim"][i]
				team2 = self.vorrunde_ergebnisse["Gast"][i]
				diff_team1 = int(self.vorrunde_ergebnisse["Punkte Heim"][i])-int(self.vorrunde_ergebnisse["Punkte Gast"][i])
				if diff_team1 == 0:
					pts_team1 = 1
				else:
					pts_team1 = (diff_team1>0)*2
				for group_name, group in self.groups.items():
					if team1 in group:
						if not group_name in results.keys():
							results[group_name] = {}
							results[group_name][team1] = {"Punkte": pts_team1, "Differenz": diff_team1}
							results[group_name][team2] = {"Punkte": 2-pts_team1, "Differenz": -diff_team1}
						else:
							if not team1 in results[group_name].keys():
								results[group_name][team1] = {"Punkte": pts_team1, "Differenz": diff_team1}
							else: 
								results[group_name][team1]["Punkte"] += pts_team1
								results[group_name][team1]["Differenz"] += diff_team1
							if not team2 in results[group_name].keys():
								results[group_name][team2] = {"Punkte": 2-pts_team1, "Differenz": -diff_team1}
							else: 
								results[group_name][team2]["Punkte"] += 2-pts_team1
								results[group_name][team2]["Differenz"] -= diff_team1

		results_sorted = {}
		table = {}
		for group_name, group_results in results.items():
			table[group_name] = {}
			group_results_sorted = {key: value for key, value in reversed(sorted(group_results.items(), key=lambda item: (item[1]["Punkte"], item[1]["Differenz"])))}
			results_sorted[group_name] = group_results_sorted
			i = 0
			for team, team_results in group_results_sorted.items():
				i+=1
				table[group_name].setdefault("Platz", []).append(i)
				table[group_name].setdefault("Team", []).append(team)
				table[group_name].setdefault("Punkte", []).append(team_results["Punkte"])
				table[group_name].setdefault("Differenz", []).append(team_results["Differenz"])


		die_dritten = {}
		for group_name in results_sorted:
			if len(results_sorted[group_name]) >= 3:
				die_dritten[list(results_sorted[group_name])[2]] = results_sorted[group_name][list(results_sorted[group_name])[2]]

		die_dritten_sorted = {key: value for key, value in reversed(sorted(die_dritten.items(), key=lambda item: (item[1]["Punkte"], item[1]["Differenz"])))}
		beste_dritte = list(die_dritten_sorted)[:anzahl_dritte]

		gruppen_mit_bd = [self.get_group(team) for team in beste_dritte]
		if beste_dritte != []:
			table_dritte = {}
			for i, team in enumerate(die_dritten_sorted):   
				table_dritte.setdefault("Platz", []).append(i+1)
				table_dritte.setdefault("Team", []).append(team)
				images = [self.create_table(table_dritte, "Platzierungen der Gruppendritten")]

			gruppen_ohne_bd = [group for group in self.groups if not group in gruppen_mit_bd]
		if not table=={}:
			data = []        
			for group_name in self.groups:
				images.append(self.create_table(table[group_name], "Tabelle "+group_name))
		
		images.append(self.create_table(self.vorrunde_ergebnisse, "Ergebnisse Vorrunde"))

		#self.upload_images(images)
		return results_sorted, gruppen_mit_bd, gruppen_ohne_bd


	def finalespiele(self):
		""" Finalspiele 

		es ist wichtig, dass hier nicht die ersten gegen die ersten spielen werden 
		und die Teams dürfen nicht aus der gleichen Gruppe sein
		"""
		self.load_groups()
		results_sorted, gruppen_mit_bd, gruppen_ohne_bd = self.determine_table()
		#print(results)
		"""
		if results == {}:
			for group_name, group in self.groups.items():
				results[group_name] = {}
				i = 0
				for team in group:
					i+=1
					results[group_name][str(i)+". "+group_name] = {}
					
		#results_sorted = results

		#print(results_sorted)
		"""					
		teams_finale = []
		i = 0
		j = 0
		group_names = list(results_sorted.keys())
		#print(self.finale)
		#print(teams_finale)
		while self.finale*2 > len(teams_finale):
			teams_finale.append(list(results_sorted[group_names[i]].keys())[j])
			i = (i+1)%len(results_sorted)
			if i == 0 and len(teams_finale) != 0:
				j += 1


		finalspiele = {}

		for i in range(int(len(gruppen_mit_bd)/2)):
			gruppe1 = gruppen_mit_bd[2*i]
			#print(list(results_sorted[gruppe1]))
			gruppe2 = gruppen_mit_bd[2*i+1]
			#print(list(results_sorted[gruppe2]))
			for j in range(3):
				team1 = list(results_sorted[gruppe1])[j]
				team2 = list(results_sorted[gruppe2])[3-j-1]
				finalspiele.setdefault(self.finale_name(self.finale), []).append([team1, team2]) #"Sieger " + prev_finale + " " + str(spiel+1), "Sieger " + prev_finale + " " + str(spiel+2)])

				
		for i,_ in enumerate(gruppen_ohne_bd):
			team1 = list(results_sorted[gruppen_ohne_bd[i]])[0]
			if i == len(gruppen_ohne_bd)-1:
				j = 0
			else:
				j = i+1
			team2 = list(results_sorted[gruppen_ohne_bd[j]])[1]
			finalspiele.setdefault(self.finale_name(self.finale), []).append([team1, team2]) #"Sieger " + prev_finale + " " + str(spiel+1), "Sieger " + prev_finale + " " + str(spiel+2)])

			
				
		#print(finalspiele)
		"""
		worse_half = teams_finale[-finale:]

		#print(finale)

		for i in range(finale):
			j = -1
			while get_group(worse_half[j]) == get_group(teams_finale[i]):
				j-=1
			opponent = worse_half.pop(j)
			finalspiele.setdefault(finale_name(finale), []).append([teams_finale[i], opponent])
		"""

		while self.finale > 1:
			prev_finale = self.finale_name(self.finale)
			self.finale = int(self.finale/2)
			#print(self.finale)
			for spiel in range(self.finale): #finalspiele[prev_finale]:
					finalspiele.setdefault(self.finale_name(self.finale), []).append(["Sieger " + prev_finale + " " + str(spiel+1), "Sieger " + prev_finale + " " + str(spiel+2)])


		#def spielplan_finalspiele(self):
		""" Spielplan Finale """

		aktuelle_zeit = self.startzeit_finale #list(spielplan_vorrunde.keys())[-1]
		#aktuelle_zeit = str_to_time(list(spielplan_vorrunde.keys())[-1][:-3]) + self.spielzeit + self.pause
		spielplan_finalrunde = {}

		#aktuelle_zeit = finals_start
		spielplan_finalrunde_table = {}

		for final_name in finalspiele:
			for i, spiel in enumerate(finalspiele[final_name]):
				zeit = time.asctime(time.localtime(aktuelle_zeit * 60)).split(" ")[-2]
				game = [final_name]+spiel
				spielplan_finalrunde.setdefault(zeit, []).append(game)
				aktueller_platz = i % self.plaetze + 1
				spielplan_finalrunde_table.setdefault("Platz", []).append(aktueller_platz)
				if aktueller_platz == self.plaetze and i < len(finalspiele[final_name])-1:
					aktuelle_zeit += self.spielzeit + self.pause
			aktuelle_zeit += self.spielzeit + self.pause

		for zeit, spiele in spielplan_finalrunde.items():
			for spiel in spiele:
				spielplan_finalrunde_table.setdefault("Uhrzeit", []).append(zeit[:-3])
				spielplan_finalrunde_table.setdefault("Spiel", []).append(spiel[0])
				spielplan_finalrunde_table.setdefault("Heim", []).append(spiel[1])
				spielplan_finalrunde_table.setdefault("Gast", []).append(spiel[2])

		self.write_csv("spielplan_finalrunde.csv",spielplan_finalrunde_table)
		image = self.create_table(spielplan_finalrunde_table, "Spielplan Finalrunde")

		ergebnisse_finalrunde = spielplan_finalrunde_table
		ergebnisse_finalrunde["Punkte Heim"] = []
		ergebnisse_finalrunde["Punkte Gast"] = []
		self.write_csv("ergebnisse_finalrunde.csv",ergebnisse_finalrunde)
		#self.upload_images([image])

	def update_finals(self):
		""" update Finalspiele sodass die Gewinner in die nächste Runde kommen """
		
		ergebnisse_finalrunde = self.read_csv("ergebnisse_finalrunde.csv")
		diff_team1 = ergebnisse_finalrunde["Ergebnis Heim"] - ergebnisse_finalrunde["Ergebnis Gast"]
		if diff_team1 > 0:
			winner = ergebnisse_finalrunde["Heim"]
		elif diff_team1 < 0:
			winner = ergebnisse_finalrunde["Gast"]

	def load_results(self):
		""" Ergebnisse und Tabellen """
		#results_finale = {}
		finals = list(final_ergebnisse.keys())
		#print(final_ergebnisse)
		for i, finale_name in enumerate(final_ergebnisse):
			j=0
			for teams, ergebnis in final_ergebnisse[finale_name].items():
				if len(ergebnis)==2:
					#print(ergebnis)
					team1, team2 = teams.split("-")
					diff_team1 = ergebnis[0]-ergebnis[1]
					if diff_team1 > 0:
						winner = team1
					else:
						winner = team2
					
					if finals[i] == "Finale":
						print("Gewonnen hat :", winner)
					
					else:
						print(finals[i+1])
						print(finalspiele[finals[i+1]])
						finalspiele[finals[i+1]][0][j] = winner
				j += 1

		ergebnisse_finalrunde_table = {}
		ergebnisse_finalrunde_table["Ergebnis"] = []

		for zeit, spiele in spielplan_finalrunde.items():
			for spiel in spiele:
				ergebnisse_finalrunde_table.setdefault("Uhrzeit", []).append(zeit[:-3])
				ergebnisse_finalrunde_table.setdefault("Spiel", []).append(spiel[0])
				ergebnisse_finalrunde_table.setdefault("Heim", []).append(spiel[1])
				ergebnisse_finalrunde_table.setdefault("Gast", []).append(spiel[2])
				if (spiel[0]+":"+spiel[1]) in final_ergebnisse[spiel[0]].keys():
					ergebnis = final_ergebnisse[spiel[0]][spiel[1]+":"+spiel[2]] 
					if len(ergebnis)==2:
						ergebnisse_finalrunde_table["Ergebnis"].append(str(ergebnis[0])+" : "+str(ergebnis[1]))
				
		#if not ergebnisse_finalrunde_table["Ergebnis"] == []:
		#	self.upload_images(self.create_table(spielplan_finalrunde_table, "Ergebnisse Finalrunde"))


	def upload_images(self, images):    
		""" UPLOAD """

		# Below code does the authentication 
		# part of the code 
		gauth = GoogleAuth() 
		  
		# Creates local webserver and auto 
		# handles authentication. 
		gauth.LocalWebserverAuth()        
		drive = GoogleDrive(gauth) 

		file_list = drive.ListFile({'q': "'19mJyxGZkjq5YDz1382dG0EkQXOvymE5u' in parents and trashed=false"}).GetList()

		def update(file):
			for file1 in file_list:
				if file == file1['title']:
					return drive.CreateFile({'id': file1['id']})
			return drive.CreateFile({'title': x,  'parents':  [{'id': ["19mJyxGZkjq5YDz1382dG0EkQXOvymE5u"]}]}) 

		   
		# iterating thought all the files/folder 
		# of the desired directory 
		for image in images: 
			f = update(image)
			f.SetContentFile(os.path.join(self.folder, image)) 
			f.Upload()
			f = None

if __name__ == 'spielplan_vorrunde':
	spielplan = Spielplan(parameters)
	spielplan.get_teams("teams.csv")
	spielplan.get_toepfe()
	spielplan.generate_groups()
	spielplan.determine_spielplan_vorrunde()

if __name__ == '__main__':
	"""
		Generate groups and gameplan

	python3 spielplan.py parameters.yaml --spielplanvorrunde
	Update and Upload results from .csv sheet

	python3 spielplan.py parameters.yaml --vorrunde
	Generate gameplan for the finals

	python3 spielplan.py parameters.yaml --spielplanfinals
	Update and Upload results finals from .csv sheet

	python3 spielplan.py parameters.yaml --finals

	
	parser = ArgumentParser()
	parser.add_argument("config", help="yaml config defining the training pipleline", type=str)
	parser.add_argument("--spielplanvorrunde", help="Run vorrunde gameplan module",action='store_true')
	parser.add_argument("--vorrunde", help="Run vorrunde results module",action='store_true')
	parser.add_argument("--spielplanfinals", help="Run finals gameplan module",action='store_true')
	parser.add_argument("--finals", help="Run final results module", action='store_true')

	args = parser.parse_args()

	if not any([args.spielplanvorrunde, args.vorrunde, args.spielplanfinals,args.finals):
		raise ValueError("You have to specify which module to run (e.g. --finals).")

	should_generate_gameplan_vorrunde = getattr(args, 'spielplanvorrunde', False)
	should_determine_results_vorrunde = getattr(args, 'vorrunde', False)
	should_generate_gameplan_finals = getattr(args, 'spielplanfinals', False)
	should_determine_results_finals = getattr(args, 'finals', False)
	"""
	with open("parameters.yaml",encoding='utf8') as f:
		parameters = yaml.safe_load(f)

	spielplan = Spielplan(parameters)
	#spielplan.get_teams("teams.csv")
	#spielplan.get_toepfe()
	#spielplan.generate_groups()
	#spielplan.determine_spielplan_vorrunde()
	#spielplan.determine_table()
	spielplan.finalespiele()
