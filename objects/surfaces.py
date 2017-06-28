import pandas as pa
from objects.reader_csv import Reader_CSV

class Surfaces:

	reader = None
	
	# the variables required in the forcing data
	fields_required = [
		'name', 
		'alpha_s', 
		'tau_s', 
		'alpha_l', 
		'epsilon_l'
	]
	
	ds = None
	
	def __init__(self, csv_loc):
		self.reader = Reader_CSV(csv_loc, self.fields_required, 'surfaces')
		self.ds = self.reader.load()
		

		
		

