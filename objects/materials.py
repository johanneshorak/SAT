from objects.reader_csv import Reader_CSV

class Materials:

	reader = None
	
	# the variables required in the forcing data
	fields_required = [
		'name', 
		'cv', 
		'conductivity', 
		'rho'
	]
	
	ds = None
	
	def __init__(self, csv_loc):
		self.reader = Reader_CSV(csv_loc, self.fields_required, 'materials')
		self.ds = self.reader.load()
		

		
		

