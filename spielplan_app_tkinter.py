import yaml
from tkinter import *
from vorrunde import SpielplanVorrunde
from finals import SpielplanFinals

class SpielplanVorFinals(Frame):
	def __init__(self, config, master=None):
		self.config = config
		Frame.__init__(self, master)
		self.pack()
		self.should_generate_spielpan_vorrunde = False
		self.should_determine_results_vorrunde=False
		self.should_generate_spielplan_finals=False
		self.should_update_finals=False
		self.createWidgets()

	def generate_spielplan_vorrunde(self):
		spielplan_vorrunde = SpielplanVorrunde(self.config)
		spielplan_vorrunde.get_teams(print=True)
		spielplan_vorrunde.get_toepfe()
		spielplan_vorrunde.generate_groups()
		spielplan_vorrunde.determine_spielplan_vorrunde()
		spielplan_vorrunde.spielplan_pause()

	def determine_results_vorrunde(self):
		spielplan_vorrunde = SpielplanVorrunde(self.config)
		spielplan_vorrunde.determine_table()

	def generate_spielplan_finals(self):
		spielplan_finals = SpielplanFinals(self.config)
		spielplan_finals.finalespiele()
	
	def update_finals(self):
		spielplan_finals = SpielplanFinals(self.config)
		spielplan_finals.update_finals()

	def createWidgets(self):
		#self.QUIT = Button(self)
		#self.QUIT["text"] = "QUIT"
		#self.QUIT["fg"]   = "red"
		#self.QUIT["command"] =  self.quit
		#self.QUIT.pack({"side": "left"})

		self.generate_vorrunde = Button(self)
		self.generate_vorrunde["text"] = "Generiere Gruppen und Spielplan",
		self.generate_vorrunde["command"] = self.generate_spielplan_vorrunde
		self.generate_vorrunde.pack({"side": "left"})

		self.vorrunde = Button(self)
		self.vorrunde["text"] = "Berechne Tabellen",
		self.vorrunde["command"] = self.determine_results_vorrunde
		self.vorrunde.pack({"side": "left"})

		self.generate_finals = Button(self)
		self.generate_finals["text"] = "Generiere Spielplan Finale",
		self.generate_finals["command"] = self.generate_spielplan_finals
		self.generate_finals.pack({"side": "left"})

		self.finals = Button(self)
		self.finals["text"] = "Update Finale",
		self.finals["command"] = self.update_finals
		self.finals.pack({"side": "left"})
	



if __name__ == '__main__':
	"""
	Generate groups and gameplan

	python3 spielplan_b4l.py parameters.yaml --options

	options are spielplanvorrunde, vorrunde, spielplanfinals and finals

	python3 spielplan.py parameters.yaml --spielplanvorrunde
	Update and Upload results from .csv sheet

	python3 spielplan.py parameters.yaml --vorrunde
	Generate gameplan for the finals

	python3 spielplan.py parameters.yaml --spielplanfinals
	Update and Upload results finals from .csv sheet

	python3 spielplan.py parameters.yaml --finals
	"""
	root = Tk()
	root.title("Spielplan Generator")
	root.geometry("2000x400")
	with open("parameters.yaml",encoding='utf8') as f:
		parameters = yaml.safe_load(f)
	spielplan = SpielplanVorFinals(parameters, master=root)
	spielplan.mainloop()
	root.destroy()

	"""
	parser = ArgumentParser()
	parser.add_argument("config", help="yaml config defining the training pipleline", type=str)
	parser.add_argument("--spielplanvorrunde", help="Run vorrunde gameplan module",action='store_true')
	parser.add_argument("--vorrunde", help="Run vorrunde results module",action='store_true')
	parser.add_argument("--spielplanfinals", help="Run finals gameplan module",action='store_true')
	parser.add_argument("--finals", help="Run final results module", action='store_true')

	args = parser.parse_args()

	if not any([args.spielplanvorrunde, args.vorrunde, args.spielplanfinals,args.finals]):
		raise ValueError("You have to specify which module to run (e.g. --finals).")

	should_generate_spielpan_vorrunde = getattr(args, 'spielplanvorrunde', False)
	should_determine_results_vorrunde = getattr(args, 'vorrunde', False)
	should_generate_spielplan_finals = getattr(args, 'spielplanfinals', False)
	should_update_finals = getattr(args, 'finals', False)
	
	with open("parameters.yaml",encoding='utf8') as f:
		parameters = yaml.safe_load(f)

	spielplan = SpielplanVorFinals(parameters)
	#spielplan.start(should_generate_spielpan_vorrunde, should_determine_results_vorrunde, should_generate_spielplan_finals, should_update_finals)
	"""