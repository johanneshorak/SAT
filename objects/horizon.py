from objects.reader_csv import Reader_CSV

class Horizon:

	reader = None
	
	# the variables required in the forcing data
	fields_required = [
		'alpha', 
		'gamma'
	]
	
	ds = None
	
	def __init__(self, csv_loc):
		self.reader = Reader_CSV(csv_loc, self.fields_required, 'horizon')
		self.ds = self.reader.load()
		

		
		

