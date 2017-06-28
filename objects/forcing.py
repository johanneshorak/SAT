from objects.reader_csv import Reader_CSV

class Forcing:
	
	reader = None
	
	# the variables required in the forcing data
	fields_required = [
		'datetime', 
		'G', 
		'H', 
		'T_A', 
		'v_10', 
		'T_A', 
		'T_Gnd'
	]
	
	ds = None
	
	def __init__(self, csv_loc):
		self.reader = Reader_CSV(csv_loc, self.fields_required, 'forcing')
		self.ds = self.reader.load()
		

		
		

