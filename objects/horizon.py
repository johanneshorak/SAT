from objects.reader_csv import Reader_CSV
import pandas as pd

class Horizon:

	reader = None
	
	# the variables required in the forcing data
	fields_required = [
		'alpha', 
		'gamma'
	]
	
	ds = None
	
	def __init__(self, csv_loc):
		if not(csv_loc is None):
			self.reader = Reader_CSV(csv_loc, self.fields_required, 'horizon')
			self.ds = self.reader.load()
		else:
			self.ds = pd.DataFrame(columns=['alpha', 'gamma'], data=[[0, 0], [180, 0], [270, 0]])
		

		
		

