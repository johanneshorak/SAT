from objects.reader_csv import Reader_CSV
from objects.sun import Sun
from datetime import datetime
import pandas as pa
import numpy as np

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
	sun = None
	
	def __init__(self, model_dt, csv_loc,  lon,  lat):
		self.reader = Reader_CSV(csv_loc, self.fields_required, 'forcing')
		self.ds = self.reader.load()
		
		# interpolate the forcing data to the model timestep
		new_dt = int(1000.0*model_dt)
		new_range = pa.date_range(self.ds.index.values[0], self.ds.index.values[-1], freq=str(new_dt)+'ms')
		self.ds = self.ds.reindex(new_range)
		self.ds = self.ds.interpolate(method='linear')
		
		# calculate other quantities at forcing timestep
		n = len(self.ds.index)
		self.sun = Sun(lon, lat)
		gammas = np.zeros(n)
		psis = np.zeros(n)
		Dh	= np.zeros(n)
		for i in range(0, len(self.ds.index.values)):
			dtime = datetime.utcfromtimestamp((self.ds.ix[i].name - np.datetime64('1970-01-01T00:00:00Z')) / np.timedelta64(1, 's'))
			self.sun.set_datetime(dtime)
			gammas[i]	= self.sun.gamma
			psis[i]		= self.sun.psi
			Dh[i]		= self.ds.ix[i].G-self.ds.ix[i].H
			
		self.ds['gamma'] = gammas
		self.ds['psi'] = psis
		self.ds['Dh'] = Dh

	# interpolates forcing to current timestep
	def values_at(self,  dtime):
		left= self.ds.asof(dtime)
		t = pa.Timedelta(dtime-left.datetime).seconds
		
		if t > 0:		
			i   = self.ds.index.get_loc(left.datetime)
			ip1 = i+1
	
			if ip1 > len(self.ds.index):
				return left
			else:	
				right = self.ds.iloc[ip1]
				
				timestep = pa.Timedelta(right.datetime-left.datetime).seconds	# current timestep of forcing
				slope = (right-left)/timestep
				
				result = left + slope*t
				return result
		else:
			return left
	
	
		

