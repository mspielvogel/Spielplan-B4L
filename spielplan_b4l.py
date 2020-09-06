import numpy as np
import time
import plotly.graph_objects as go
import pandas
import plotly.express as px
import os
from random import shuffle
from pydrive.drive import GoogleDrive 
from pydrive.auth import GoogleAuth 

class spielplan():
	__init__(self, config):

	self.startzeit = self.str_to_time(startzeit, datum)


	def str_to_time(self, startzeit, datum):
    startzeit = datum + " " + startzeit
    startzeit = time.mktime(time.strptime(startzeit,"%d/%m/%Y %H:%M"))
    startzeit /= 60
    return startzeit


    def get_teams(self, csv_file_teams):
    	self.teams = {}
    	anzahl_teams = len(teams)
		print("Es gibt ", anzahl_teams, " Teams.")
		anzahl_dritte = anzahl_teams % anzahl_toepfe
		print("Damit kommen die besten",anzahl_dritte,"Dritten weiter.")

	def get_toepfe(self):
		""" Lostoepfe - es gibt so viele Toepfe wie die max_i(len(group_i)); 
		der erste Topf darf höchstens ein Element mehr haben als jeder andere und nicht weniger """

		self.toepfe = {}
		for team, topf in teams.items():
		    topf_name = 'Topf ' + str(topf)
		    toepfe.setdefault(topf_name, []).append(team)

		#print(toepfe)
		for topf in toepfe:
		    print(topf, len(toepfe[topf]))

	def generate_groups(self):
		""" Erstelle die Gruppen """

		groups = {}
		i = 0
		np.random.seed(42)
		toepfe_keys = list(toepfe.keys())

		while len(toepfe[toepfe_keys[0]])>0:
		    i += 1
		    group_name = 'Gruppe ' + str(i)
		    
		    size_randoms = 0
		    for key in toepfe_keys:
		        if len(toepfe[key]) > 0:
		            size_randoms += 1
		    
		    randoms = [np.random.randint(len(toepfe[toepfe_keys[j]])) for j in range(size_randoms)]
		    group = []
		    for k, random in enumerate(randoms):
		        group.append(toepfe[toepfe_keys[k]].pop(random))
		    groups[group_name] = group

		def get_group(team):
		    if ". " in team: 
		        return team.split(". ")[1]
		    for group_name, group in groups.items():
		        if team in group:
		            return group_name
		    
		print(groups)

	def load_results(self):
		self.results = #read csv with results and translate it into a dict


	def determine_table(self):
		""" Ergebnisse und Tabellen """
		results = {}
		for teams, ergebnis in vorrunde_ergebnisse.items():
		    if len(ergebnis)==2:
		        team1, team2 = teams.split(":")
		        diff_team1 = ergebnis[0]-ergebnis[1]
		        if diff_team1 == 0:
		            pts_team1 = 1
		        else:
		            pts_team1 = (diff_team1>0)*2
		        for group_name, group in groups.items():
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
		    group_results_sorted = {key: value for key, value in reversed(sorted(group_results.items(), key=lambda item: (item[1]["Differenz"], item[1]["Punkte"])))}
		    results_sorted[group_name] = group_results_sorted
		    i = 0
		    for team, team_results in group_results_sorted.items():
		        i+=1
		        table[group_name].setdefault("rank", []).append(i)
		        table[group_name].setdefault("teams", []).append(team)
		        table[group_name].setdefault("pts", []).append(team_results["Punkte"])
		        table[group_name].setdefault("diff", []).append(team_results["Differenz"])


		die_dritten = {}
		for group_name in results_sorted:
		    if len(results_sorted[group_name]) >= 3:
		        die_dritten[list(results_sorted[group_name])[2]] = results_sorted[group_name][list(results_sorted[group_name])[2]] #(list( #list(group_results_sorted[group_name]))#[3])

		die_dritten_sorted = {key: value for key, value in reversed(sorted(die_dritten.items(), key=lambda item: (item[1]["Punkte"], item[1]["Differenz"])))}
		beste_dritte = list(die_dritten_sorted)[:anzahl_dritte]

		gruppen_mit_bd = [get_group(team) for team in beste_dritte]
		table_dritte = {}
		for i, team in enumerate(die_dritten_sorted):   
		    table_dritte.setdefault("rank", []).append(i+1)
		    table_dritte.setdefault("teams", []).append(team)


		data = [go.Table(header=dict(values=["Platz" ,"Team"]), cells=dict(values=[table_dritte["rank"], table_dritte["teams"]]))]
		fig = go.Figure(data = data)
		fig.update_layout(title="Platzierungen der Dritten")
		fig.write_image(os.path.join(folder,"Dritte.jpeg"))
		#fig.show()

		gruppen_ohne_bd = [group for group in groups if not group in gruppen_mit_bd]

		if not table=={}:
		    data = []        
		    for group_name in groups:
		        data = [go.Table(header=dict(values=["Platz" ,"Team", "Punkte", "Differenz"]), cells=dict(values=[table[group_name]["rank"], table[group_name]["teams"],table[group_name]["pts"],table[group_name]["diff"]]))] 
		        fig = go.Figure(data = data)
		        fig.update_layout(title=group_name)
		        fig.write_image(os.path.join(folder,str(group_name)+"_Ergebnis.jpeg"))

		    
		ergebnisse_vorrunde_table = {}
		ergebnisse_vorrunde_table["ergebnis"] = []

		for zeit, spiele in spielplan_vorrunde.items():
		    for spiel in spiele:
		        ergebnisse_vorrunde_table.setdefault("zeit", []).append(zeit[:-3])
		        ergebnisse_vorrunde_table.setdefault("team1", []).append(spiel[0])
		        ergebnisse_vorrunde_table.setdefault("team2", []).append(spiel[1])
		        if (spiel[0]+":"+spiel[1]) in vorrunde_ergebnisse.keys():
		            ergebnis = vorrunde_ergebnisse[spiel[0]+":"+spiel[1]]
		            if len(ergebnis)==2:
		                ergebnisse_vorrunde_table["ergebnis"].append(str(ergebnis[0])+" : "+str(ergebnis[1]))
		                
		                
		if not ergebnisse_vorrunde_table["ergebnis"] == []:        
		    data = [go.Table(header=dict(values=["Uhrzeit" ,"Heim", "Gast", "Ergebnis"]), 
		                     cells=dict(values=[ergebnisse_vorrunde_table["zeit"], 
		                                        ergebnisse_vorrunde_table["team1"], ergebnisse_vorrunde_table["team2"],
		                                        ergebnisse_vorrunde_table["ergebnis"]]))]   
		    fig = go.Figure(data = data)
		    fig.update_layout(title="Ergebnisse Vorrunde", height = 1000)
		    fig.write_image(os.path.join(folder,"ergebnis_vorrunde.jpeg"))


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

	def finalespiele(self):
		""" Finalspiele 

		es ist wichtig, dass hier nicht die ersten gegen die ersten spielen werden 
		und die Teams dürfen nicht aus der gleichen Gruppe sein
		"""
		#print(results)
		if results == {}:
		    for group_name, group in groups.items():
		        results[group_name] = {}
		        i = 0
		        for team in group:
		            i+=1
		            results[group_name][str(i)+". "+group_name] = {}
		            
		results_sorted = results

		print(results_sorted)
		            
		teams_finale = []
		i = 0
		j = 0
		group_names = list(results_sorted.keys())
		print(finale)
		print(teams_finale)
		while finale*2 > len(teams_finale):
		    teams_finale.append(list(results_sorted[group_names[i]].keys())[j])
		    i = (i+1)%len(results_sorted)
		    if i == 0 and len(teams_finale) != 0:
		        j += 1


		finalspiele = {}

		for i in range(int(len(gruppen_mit_bd)/2)):
		    gruppe1 = gruppen_mit_bd[2*i]
		    print(list(results_sorted[gruppe1]))
		    gruppe2 = gruppen_mit_bd[2*i+1]
		    print(list(results_sorted[gruppe2]))
		    for j in range(3):
		        team1 = list(results_sorted[gruppe1])[j]
		        team2 = list(results_sorted[gruppe2])[3-j-1]
		        finalspiele.setdefault(finale_name(finale), []).append([team1, team2]) #"Sieger " + prev_finale + " " + str(spiel+1), "Sieger " + prev_finale + " " + str(spiel+2)])

		        
		for i,_ in enumerate(gruppen_ohne_bd):
		    team1 = list(results_sorted[gruppen_ohne_bd[i]])[0]
		    if i == len(gruppen_ohne_bd)-1:
		        j = 0
		    else:
		        j = i+1
		    team2 = list(results_sorted[gruppen_ohne_bd[j]])[1]
		    finalspiele.setdefault(finale_name(finale), []).append([team1, team2]) #"Sieger " + prev_finale + " " + str(spiel+1), "Sieger " + prev_finale + " " + str(spiel+2)])

		    
		        
		print(finalspiele)
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

		while finale > 1:
		    prev_finale = finale_name(finale)
		    finale /= 2
		    for spiel in range(int(finale)): #finalspiele[prev_finale]:
		            finalspiele.setdefault(finale_name(finale), []).append(["Sieger " + prev_finale + " " + str(spiel+1), "Sieger " + prev_finale + " " + str(spiel+2)])


	def spielplan_finalspiele(self):
		""" Spielplan Finale """

		aktuelle_zeit = list(spielplan_vorrunde.keys())[-1]
		aktuelle_zeit = str_to_time(list(spielplan_vorrunde.keys())[-1][:-3]) + spielzeit + pause
		spielplan_finalrunde = {}

		aktuelle_zeit = finals_start
		spielplan_finalrunde_table = {}

		for final_name in finalspiele:
		    for i, spiel in enumerate(finalspiele[final_name]):
		        zeit = time.asctime(time.localtime(aktuelle_zeit * 60)).split(" ")[-2]
		        game = [final_name]+spiel
		        spielplan_finalrunde.setdefault(zeit, []).append(game)
		        aktueller_platz = i % plaetze + 1
		        spielplan_finalrunde_table.setdefault("platz", []).append(aktueller_platz)
		        if aktueller_platz == plaetze and i < len(finalspiele[final_name])-1:
		            aktuelle_zeit += spielzeit + pause
		    aktuelle_zeit += spielzeit + pause

		"""
		for i,  game in enumerate(finalspiele.items()):
		    print(game)
		    zeit = time.asctime(time.localtime(aktuelle_zeit * 60)).split(" ")[-2]
		    spielplan_finalrunde.setdefault(zeit, []).append(game)
		    if i%plaetze == plaetze-1:
		        aktuelle_zeit += spielzeit + pause
		"""


		for zeit, spiele in spielplan_finalrunde.items():
		    for spiel in spiele:
		        spielplan_finalrunde_table.setdefault("zeit", []).append(zeit[:-3])
		        spielplan_finalrunde_table.setdefault("spiel", []).append(spiel[0])
		        spielplan_finalrunde_table.setdefault("team1", []).append(spiel[1])
		        spielplan_finalrunde_table.setdefault("team2", []).append(spiel[2])
		        
		data = [go.Table(header=dict(values=["Uhrzeit", "Spiel" ,"Heim", "Gast", "Platz"]), 
		                 cells=dict(values=[spielplan_finalrunde_table["zeit"], spielplan_finalrunde_table["spiel"], 
		                                    spielplan_finalrunde_table["team1"], spielplan_finalrunde_table["team2"],
		                                   spielplan_finalrunde_table["platz"]]))]   
		fig = go.Figure(data = data)
		fig.update_layout(title="Spielplan Finalspiele", height = 1000, width = 1000)
		fig.write_image(os.path.join(folder,"spielplan_finals.jpeg"))
		fig.show()

	def load_results(self):
		""" Ergebnisse und Tabellen """
		#results_finale = {}
		finals = list(final_ergebnisse.keys())
		#print(final_ergebnisse)
		for i, finale in enumerate(final_ergebnisse):
		    j=0
		    for teams, ergebnis in final_ergebnisse[finale].items():
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
		spielplan_finalrunde_table["ergebnis"] = []

		for zeit, spiele in spielplan_finalrunde.items():
		    for spiel in spiele:
		        ergebnisse_finalrunde_table.setdefault("zeit", []).append(zeit[:-3])
		        ergebnisse_finalrunde_table.setdefault("spiel", []).append(spiel[0])
		        ergebnisse_finalrunde_table.setdefault("team1", []).append(spiel[1])
		        ergebnisse_finalrunde_table.setdefault("team2", []).append(spiel[2])
		        if (spiel[0]+":"+spiel[1]) in final_ergebnisse[spiel[0]].keys():
		            ergebnis = final_ergebnisse[spiel[0]][spiel[1]+":"+spiel[2]] 
		            if len(ergebnis)==2:
		                spielplan_finalrunde_table["ergebnis"].append(str(ergebnis[0])+" : "+str(ergebnis[1]))
		        
		if not spielplan_finalrunde_table["ergebnis"] == []:        
		    data = [go.Table(header=dict(values=["Uhrzeit", "Spiel" ,"Heim", "Gast", "Ergebnis"]), 
		                     cells=dict(values=[ergebnisse_finalrunde_table["zeit"], ergebnisse_finalrunde_table["spiel"], 
		                                        ergebnisse_finalrunde_table["team1"], ergebnisse_finalrunde_table["team2"],
		                                       ergebnisse_finalrunde_table["ergebnis"]]))]   
		    fig = go.Figure(data = data)
		    fig.update_layout(title="Ergebnisse Finalspiele")
		    fig.write_image(os.path.join(folder,"ergebnis_finals.jpeg"))
		    fig.show()


	def upload_images(self):	
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
		for x in os.listdir(folder): 
		    f = update(x)
		    f.SetContentFile(os.path.join(folder, x)) 
		    f.Upload()
		    f = None