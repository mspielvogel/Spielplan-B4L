import time
import plotly.graph_objects as go
import pandas
import plotly.express as px
import os
import csv
#from pydrive.drive import GoogleDrive 
#from pydrive.auth import GoogleAuth 

class Spielplan():
	def __init__(self, config):
		self.config = config
		self.datum = config.get("datum")		
		self.plaetze = config.get("plaetze")
		self.finale = config.get("finale")
		self.folder_upload = config.get("folder_upload")
		self.folder_tables = config.get("folder_tables")

	def str_to_time(self, startzeit):
		startzeit = self.datum + " " + startzeit
		startzeit = time.mktime(time.strptime(startzeit, "%d.%m.%Y %H:%M"))
		startzeit /= 60
		return startzeit

	def write_csv(self, file_name, values):
		headers = list(values.keys())
		with open(os.path.join(self.folder_tables, file_name), 'w') as csv_file:
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
		with open(os.path.join(self.folder_tables, file_name), 'r') as csv_file:
			reader = csv.reader(csv_file, dialect='excel')
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
		cell_values = [table[key] for key in headers]
		width = len(headers) * 250
		if len(table[headers[0]]) < 6:
			height = 300
		else:
			height = len(table[headers[0]]) * 50
		fig = go.Figure(data = [go.Table(header=dict(values=headers), cells=dict(values=cell_values))])
		fig.update_layout(title=title, height=height, width = width)
		image_name = "_".join(title.lower().split(" "))+".jpeg"
		path = os.path.join(self.folder_upload, image_name)
		fig.write_image(path)
		return image_name

	def get_group(self, team):
		if ". " in team: 
			return team.split(". ")[1]
		for group_name, group in self.groups.items():
			if team in group:
				return group_name
		
	def load_results(self):
		pass

	def load_groups(self):
		self.groups = self.read_csv("groups.csv") 

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
			f.SetContentFile(os.path.join(self.folder_upload, image)) 
			f.Upload()
			f = None