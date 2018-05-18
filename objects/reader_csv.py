from .reader import Reader
import pandas as pa

class Reader_CSV(Reader):
	fields_required = None
	
	type = ''		# indicates what file we are reading, e.g. forcing, horizon or ...
	
	options = None
	
	loc = ''		# location of the csv file
	sep = ','		# field separator
	dec_mark = '.'	# decimal mark
	

	def __init__(self, loc, fields_required, type = '', sep=None):
		self.type = type
		self.loc = loc
		self.fields_required = fields_required
		
		
		if sep is not None:
			self.sep=sep
		
		self.fields_available()

		
	def fields_available(self):
		with open(self.loc, 'r') as f:
			first_line = f.readline()
		
		fields_found = first_line.replace('\n', '').split(self.sep)
		
		
		
		fields_missing = False
		fields_missing_list = []
		for field in self.fields_required:
			if field not in fields_found:
				fields_missing_list.append(field)
				fields_missing = True

		if fields_missing:
			print(" missing fields while loading {:s} from {:s}".format(self.type, self.loc))
			print("  list of missing fields: ", fields_missing_list)
		Reader.fields_available(self, fields_missing)

		
	def load(self):
		print("    loading "+self.type)
		ds = pa.read_csv(self.loc, sep=self.sep, decimal=self.dec_mark)
		if 'datetime' in ds.columns and self.type=='forcing':
			ds.index = pa.to_datetime(ds.datetime)
			ds.datetime = pa.to_datetime(ds.datetime)
		elif 'alpha' in ds.columns and self.type=='horizon':
			ds.index = ds.alpha
		elif 'material' in ds.columns and self.type=='materials':
			ds.index = ds.material
		elif 'name' in ds.columns and self.type=='surfaces':
			ds.index = ds.name
		return ds
		
		
