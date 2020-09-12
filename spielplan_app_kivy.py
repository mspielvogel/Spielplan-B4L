import yaml
import os
import time

from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.modalview import ModalView

from spielplan import Spielplan
from vorrunde import SpielplanVorrunde
from finals import SpielplanFinals

class SpielplanVorFinals():
	def __init__(self):
		with open("parameters.yaml",encoding='utf8') as f:
			parameters = yaml.safe_load(f)
		self.config = parameters
		self.images = []

	def generate_spielplan_vorrunde(self):
		spielplan_vorrunde = SpielplanVorrunde(self.config)
		spielplan_vorrunde.get_teams(print_=True)
		spielplan_vorrunde.get_toepfe()
		spielplan_vorrunde.generate_groups()
		spielplan_vorrunde.determine_spielplan_vorrunde()
		spielplan_vorrunde.spielplan_pause()
		self.images = spielplan_vorrunde.images
		return spielplan_vorrunde.message

	def determine_results_vorrunde(self):
		spielplan_vorrunde = SpielplanVorrunde(self.config)
		self.images = spielplan_vorrunde.images
		return spielplan_vorrunde.determine_table()

	def generate_spielplan_finals(self):
		spielplan_finals = SpielplanFinals(self.config)
		self.images = spielplan_finals.images
		return spielplan_finals.finalespiele()	
	
	def update_finals(self):
		spielplan_finals = SpielplanFinals(self.config)
		self.images = spielplan_finals.images
		return spielplan_finals.update_finals()

	def upload(self, images=None):
		spielplan = Spielplan(self.config)
		if not images:
			images = os.listdir(self.config["folder_upload"])
		spielplan.upload_images(images)

class ViewGridDecision(GridLayout):
	def __init__(self, message):
		super(ViewGridDecision, self).__init__()
		self.rows = 3
		label = Label(text=message, font_size=30)
		self.add_widget(label)

		self.yes_btn = Button(text='Ja', font_size=30)
		self.yes_btn.bind(on_press=self.yes)
		self.add_widget(self.yes_btn)
	
		self.no_btn = Button(text='Nein', font_size=30)
		self.no_btn.bind(on_press=self.no)
		self.add_widget(self.no_btn)

	def yes(self, obj):
		self.feedback = True

	def no(self, obj):
		self.feedback = False

class ViewGridMessage(GridLayout):
	def __init__(self, message):
		super(ViewGridMessage, self).__init__()
		self.rows = 3
		label = Label(text=message, font_size=30)
		self.add_widget(label)

		self.close_btn = Button(text='Schließen', font_size=30)
		#self.close_btn.bind(on_press=self.yes)
		self.add_widget(self.close_btn)
	

	#def close(self, obj):
	#	self.feedback = True


class SpielplanGrid(GridLayout):
	def __init__(self, **kwargs):
		super(SpielplanGrid, self).__init__(**kwargs)
		self.rows = 5
		groups_vorrunde_btn = Button(text='Generiere Gruppen und Spielplan', font_size=30)
		groups_vorrunde_btn.bind(on_release=self.generate_spielplan_vorrunde)
		self.add_widget(groups_vorrunde_btn)

		spielplan_vorrunde_btn = Button(text='Verarbeite Ergebnisse Vorrunde', font_size=30)
		spielplan_vorrunde_btn.bind(on_release=self.determine_results_vorrunde)
		self.add_widget(spielplan_vorrunde_btn)

		spielplan_finals_btn = Button(text='Erstelle Spielplan Finale', font_size=30)
		spielplan_finals_btn.bind(on_release=self.generate_spielplan_finals)
		self.add_widget(spielplan_finals_btn)

		update_finals_btn = Button(text='Verarbeite Ergebnisse Finals', font_size=30)
		update_finals_btn.bind(on_release=self.update_finals)
		self.add_widget(update_finals_btn)

		upload_btn = Button(text='Alles Hochladen', font_size = 30)
		upload_btn.bind(on_release=self.upload)
		self.add_widget(upload_btn)

	def message_(self, message):
		grid = ViewGridMessage(message)
		view = ModalView(auto_dismiss=False)
		view.add_widget(grid)
		grid.close_btn.bind(on_release=view.dismiss)
		view.open()

	def decision(self, message_decision, method):
		grid = ViewGridDecision(message_decision)
		view = ModalView(auto_dismiss=False)
		view.add_widget(grid)
		grid.yes_btn.bind(on_release=view.dismiss)
		grid.no_btn.bind(on_release=view.dismiss)
		view.open()
		spielplangrid = self
		def do(self):
			if grid.feedback:
				message = method()
				spielplangrid.message_(message)
		view.bind(on_dismiss=do)

	def generate_spielplan_vorrunde(self, obj):
		spielplan_ = SpielplanVorFinals()
		if os.path.exists(os.path.join(spielplan_.config["folder_tables"], "groups.csv")) and os.path.exists(os.path.join(spielplan_.config["folder_tables"], "ergebnisse_vorrunde.csv")):
			message = self.decision("Es wurden bereits Gruppen generiert\n und ein Vorrundenspielplan erstellt.\nMöchtest Du dies trotzdem nochmal tun?\nErgebnisse könnten überschrieben werden.", spielplan_.generate_spielplan_vorrunde)
		else:
			message = spielplan_.generate_spielplan_vorrunde()
		#self.decision("Möchtest Du den Spielplan hochladen?", spielplan_.upload(spielplan_.images))

	def determine_results_vorrunde(self, obj):
		spielplan_ = SpielplanVorFinals()
		results_vorrunde = spielplan_.determine_results_vorrunde()
		if results_vorrunde:
			message = "Die Tabellen der Vorrunde wurden aktualisiert."
		else:
			message = "Es wurden keine Ergebnisse eingetragen"
		self.message_(message)
		#self.decision("Möchtest Du die Tabellen und Ergebnisse hochladen?", spielplan_.upload(spielplan_.images))
	
	def generate_spielplan_finals(self, obj):
		spielplan_ = SpielplanVorFinals()
		if os.path.exists(os.path.join(spielplan_().config["folder_tables"], "ergebnisse_finalrunde.csv")):
			message = self.decision("Es wurde bereitsein Finalrundenspielplan erstellt.\nMöchtest Du dies trotzdem nochmal tun?\nErgebnisse könnten überschrieben werden.", SpielplanVorFinals().generate_spielplan_finals)
		else:
			message = spielplan_.generate_spielplan_finals()
			if message:
				self.message_("Der Finalspielplan wurde erstellt.")
		#self.decision("Möchtest Du den Spielplan hochladen?", spielplan_.upload(spielplan_.images))

	def update_finals(self, obj):
		spielplan_ = SpielplanVorFinals()
		message = spielplan_.update_finals()
		if not message:
			message = "Es wurden keine Ergebnisse eingetragen"
		self.message_(message)
		#self.decision("Möchtest Du die Ergebnisse hochladen?", spielplan_.upload(spielplan_.images))

	def upload(self, obj):
		SpielplanVorFinals().upload()



class SpielplanApp(App):

	def build(self):
		return SpielplanGrid()


if __name__ == '__main__':
	SpielplanApp().run()