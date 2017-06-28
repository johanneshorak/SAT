# whatever the datasource is (currently only csv), reader (or classes derived from it)
# supplies the methods to check whether all required fields are available and to convert
# them into a panda dataset.

import sys

class Reader:

	req_fields = None
	loc = ''

	def __init__(self, loc, req_fields):
		pass
		
	# this function checks whether all fields are available
	# if not it prints out the missing fields and returns with false
	def fields_available(self, fields_missing):
		if fields_missing:
			print " fatal error while loading data, fields are missing!"
			sys.exit(1)
		
	# this function must return a panda dataset
	def load(self):
		pass
