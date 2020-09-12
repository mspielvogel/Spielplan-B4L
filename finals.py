import time

from spielplan import Spielplan
from vorrunde import SpielplanVorrunde

class SpielplanFinals(Spielplan):
	def __init__(self, config):
		super().__init__(config)
		self.startzeit_finale = self.str_to_time(config.get("finals_start"))
		self.spielzeit_finalrunde = config.get("spielzeit_finalrunde")
		self.pause_finalrunde = config.get("pause_finalrunde")
		self.images = []
		#self.message = False

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
	
	def finale_number(self, finale_name):
		""" """
		if finale_name == "Achtelfinale":
			return 8
		elif finale_name == "Viertelfinale":
			return 4
		elif finale_name == "Halbfinale":
			return 2
		elif finale_name in ["Finale", "Spiel um Platz 3"]:
			return 1
	
	def game_idx(self, i, j, final_num):
		k = i
		#if k-(final_num*2) > 0:
		#	idx = final_num * 2
		#else:
		idx = 0
		#print(k-final_num*2,";",idx)
		final_number = final_num
		#print(i, j, "Final_NUM",final_num)
		while k >= 0:
			final_number *= 2
			k -= final_number
			#if k >= 0:
			idx += final_number
		idx += int(j/2)
		return idx
			
	def finalespiele(self):
		""" Finalspiele 

		es ist wichtig, dass hier nicht die ersten gegen die ersten spielen werden 
		und die Teams dürfen nicht aus der gleichen Gruppe sein
		"""
		self.load_groups()
		vorrunde = SpielplanVorrunde(self.config)
		vorrunde_results = vorrunde.determine_table()
		if vorrunde_results:
			results_sorted, gruppen_mit_bd, gruppen_ohne_bd = vorrunde_results
		else:
			return "Es wurde kein Finalspielplan erstellt, da es keine Vorrundenergebnisse gibt."
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
					finalspiele.setdefault(self.finale_name(self.finale), []).append(["Sieger " + prev_finale + " " + str(2*spiel+1), "Sieger " + prev_finale + " " + str(2*spiel+2)])
					if self.finale_name(self.finale) == "Finale":
						finalspiele.setdefault("Spiel um Platz 3", []).append(["Verlierer " + prev_finale + " " + str(2*spiel+1), "Verlierer " + prev_finale + " " + str(2*spiel+2)])


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
				if final_name == "Finale":
					final_platz = aktueller_platz
				if final_name == "Spiel um Platz 3":
					aktueller_platz = final_platz + 1
				spielplan_finalrunde_table.setdefault("Platz", []).append(aktueller_platz)
				if aktueller_platz == self.plaetze and i < len(finalspiele[final_name])-1:
					aktuelle_zeit += self.spielzeit_finalrunde + self.pause_finalrunde
			if not final_name == "Finale":
				aktuelle_zeit += self.spielzeit_finalrunde + self.pause_finalrunde

		for zeit, spiele in spielplan_finalrunde.items():
			for spiel in spiele:
				spielplan_finalrunde_table.setdefault("Uhrzeit", []).append(zeit[:-3])
				spielplan_finalrunde_table.setdefault("Spiel", []).append(spiel[0])
				spielplan_finalrunde_table.setdefault("Heim", []).append(spiel[1])
				spielplan_finalrunde_table.setdefault("Gast", []).append(spiel[2])

		#self.write_csv("spielplan_finalrunde.csv",spielplan_finalrunde_table)
		self.images.append(self.create_table(spielplan_finalrunde_table, "Spielplan Finalrunde"))
		ergebnisse_finalrunde = spielplan_finalrunde_table
		ergebnisse_finalrunde["Punkte Heim"] = []
		ergebnisse_finalrunde["Punkte Gast"] = []
		self.write_csv("ergebnisse_finalrunde.csv",ergebnisse_finalrunde)
		#self.upload_images([image])
		return "Ein Finalspielplan wurde erstellt."
		#return True

	def update_finals(self):
		""" update Finalspiele sodass die Gewinner in die nächste Runde kommen 
		
		ergebnisse_finalrunde = self.read_csv("ergebnisse_finalrunde.csv")
		diff_team1 = ergebnisse_finalrunde["Ergebnis Heim"] - ergebnisse_finalrunde["Ergebnis Gast"]
		if diff_team1 > 0:
			winner = ergebnisse_finalrunde["Heim"]
		elif diff_team1 < 0:
			winner = ergebnisse_finalrunde["Gast"]
		"""
		output = ""
		#def load_results(self):
		""" Ergebnisse und Tabellen """
		final_ergebnisse = self.read_csv("ergebnisse_finalrunde.csv")
		#finals = list(final_ergebnisse.keys())
		#for i, finale_name in enumerate(final_ergebnisse):
		if not all([key in final_ergebnisse.keys() for key in ["Punkte Heim", "Punkte Gast"]]):
			return
		for i in range(len(final_ergebnisse["Uhrzeit"])):
			#import pdb; pdb.set_trace()
			if i > 0:
				if final_ergebnisse["Spiel"][i] != final_ergebnisse["Spiel"][i-1] and not final_ergebnisse["Spiel"][i-1] == "Finale":
					j = 0
			else:
				j = 0
			#print(j)
			if not (final_ergebnisse["Punkte Heim"][i]== "" or final_ergebnisse["Punkte Gast"][i]==""):
				#print("GAME", i)
				diff_team1 = int(final_ergebnisse["Punkte Heim"][i]) - int(final_ergebnisse["Punkte Gast"][i])
				if diff_team1 > 0:
					winner = final_ergebnisse["Heim"][i]
					loser = final_ergebnisse["Gast"][i]
				elif diff_team1 < 0:
					winner = final_ergebnisse["Gast"][i]
					loser = final_ergebnisse["Heim"][i]
				
				if final_ergebnisse["Spiel"][i] == "Finale":
					output += f"Gewonnen hat {winner}, Zweiter wurde {loser}"
				elif final_ergebnisse["Spiel"][i] == "Spiel um Platz 3":
					output += f"und Dritter wurde {winner}."
				else:
					final_num = int(self.finale_number(final_ergebnisse["Spiel"][i]) / 2)
					final_name = self.finale_name(final_num)
					#print(final_name)
					#if final_name == "Spiel um Platz 3":
					#	final_ergebnisse["Spiel"][self.game_idx(i,j,final_num)+1] = final_name
					#else:
					#	final_ergebnisse["Spiel"][self.game_idx(i,j,final_num)] = final_name
					#print(final_name)
					#print(self.game_idx(i,j,final_num))
					if j%2 == 0:
						side = "Heim"
					else:
						side = "Gast"
					final_ergebnisse[side][self.game_idx(i,j,final_num)] = winner
					if final_name == "Finale":
						final_ergebnisse[side][self.game_idx(i,j,final_num)+1] = loser
						#print(self.game_idx(i,j,final_num))

			j+=1
		self.write_csv("ergebnisse_finalrunde.csv", final_ergebnisse)
		self.images.append(self.create_table(final_ergebnisse, "Ergebnisse Finalrunde"))
		return output
		"""
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
		"""
		#if not ergebnisse_finalrunde_table["Ergebnis"] == []:
		#	self.upload_images(self.create_table(spielplan_finalrunde_table, "Ergebnisse Finalrunde"))
