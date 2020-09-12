from random import shuffle
import random
import numpy as np
import time

from spielplan import Spielplan

class SpielplanVorrunde(Spielplan):
	def __init__(self, config):
		super().__init__(config)
		self.startzeit = self.str_to_time(config.get("startzeit"))
		self._preferred_groupsize = config.get("gewuenschte_gruppengroesse")
		self.spielzeit_vorrunde = config.get("spielzeit_vorrunde")
		self.pause_vorrunde = config.get("pause_vorrunde")
		self.message = False
		self.images = []


	def get_teams(self, print_=False):
		self.teams = self.read_csv("teams.csv")
		anzahl_teams = len(self.teams["Team"])
		number_groups = int(anzahl_teams / self._preferred_groupsize)
		anzahl_dritte = (self.finale-number_groups)*2
		if print_:
			self.message = f"Es gibt {anzahl_teams} Teams und {number_groups} Gruppen.\n Damit kommen die besten {anzahl_dritte} Dritten weiter."
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
		random.seed(42)
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
			for k, random_num in enumerate(randoms):
				group.append(self.toepfe[toepfe_keys[k]].pop(random_num))
			self.groups[group_name] = group
		self.write_csv("groups.csv", self.groups)	

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

		for group_name in pairings:
			shuffle(pairings[group_name])

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
				aktuelle_zeit += self.spielzeit_vorrunde + self.pause_vorrunde
					
		for zeit, spiele in spielplan_vorrunde.items():
			for spiel in spiele:
				spielplan_vorrunde_table.setdefault("Uhrzeit", []).append(zeit[:-3])
				spielplan_vorrunde_table.setdefault("Heim", []).append(spiel[0])
				spielplan_vorrunde_table.setdefault("Gast", []).append(spiel[1])
		self.images.append(self.create_table(spielplan_vorrunde_table, "Spielplan Vorrunde"))
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
		if not all([key in self.vorrunde_ergebnisse.keys() for key in ["Punkte Heim", "Punkte Gast"]]):
			return
		for i in range(len(self.vorrunde_ergebnisse["Uhrzeit"])):
			if not (self.vorrunde_ergebnisse["Punkte Heim"][i]== "" or self.vorrunde_ergebnisse["Punkte Gast"][i]==""):
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
		gruppen_ohne_bd = [self.get_group(team) for team in self.teams]
		if beste_dritte != []:
			table_dritte = {}
			for i, team in enumerate(die_dritten_sorted):   
				table_dritte.setdefault("Platz", []).append(i+1)
				table_dritte.setdefault("Team", []).append(team)
				self.images.append(self.create_table(table_dritte, "Platzierungen der Gruppendritten"))

			gruppen_ohne_bd = [group for group in self.groups if not group in gruppen_mit_bd]
		if not table=={}:
			data = []      
			for group_name in self.groups:
				if group_name in table.keys():
					images.append(self.create_table(table[group_name], "Tabelle "+group_name))
		
		self.images.append(self.create_table(self.vorrunde_ergebnisse, "Ergebnisse Vorrunde"))
		return results_sorted, gruppen_mit_bd, gruppen_ohne_bd

	def spielplan_pause(self):
		spielplan = self.read_csv("ergebnisse_vorrunde.csv")
		teams = self.read_csv("teams.csv")["Team"]
		spielzeiten = set([self.str_to_time(spielzeit) for spielzeit in spielplan["Uhrzeit"]])
		spielzeiten = [time.asctime(time.localtime(zeit * 60)).split(" ")[-2][:-3] for zeit in sorted(spielzeiten)]
		spielzeiten_pause = {}
		spielzeiten_pause["Uhrzeit"] = spielzeiten
		for team in teams:
			spielzeiten_pause[team] = [0 for zeit in spielzeiten]
		
		for i, team in enumerate(spielplan["Heim"]):
			zeit = spielplan["Uhrzeit"][i]
			j = spielzeiten.index(zeit)
			spielzeiten_pause[team][j] += 1
		for i, team in enumerate(spielplan["Gast"]):
			zeit = spielplan["Uhrzeit"][i]
			j = spielzeiten.index(zeit)
			spielzeiten_pause[team][j] += 1

		self.write_csv("spielzeiten_pause.csv", spielzeiten_pause)

		pause = {"Typ Pause": ["Minimum Pause", "Maximum Pause"]}
		for team in teams:
			min_pause = len(spielzeiten)
			max_pause = 0
			aktuelle_pause = 0
			for i, spiel in enumerate(spielzeiten):
				if spielzeiten_pause[team][i] == 0:
					aktuelle_pause += 1
				else:
					min_pause = min(min_pause, aktuelle_pause)
					if spielzeiten_pause[team][i] == 2:
						min_pause = -1
					max_pause = max(max_pause, aktuelle_pause)
					aktuelle_pause = 0
			pause[team] = [min_pause, max_pause]
			
		self.write_csv("pause_team.csv", pause)

		#for i, spiel in spielzeiten: