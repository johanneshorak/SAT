from bunch import Bunch
import sys
import numpy as np

class Layer:
	
	options = None
	id = None
	material = None
	th = None		# thickness in m
	area = None		# area in m
	v = None		# volume in m^3
	m = None		# mass in kg
	Q0 = None		# heat capacity in J
	
	sl_th = None
	sl_n = None
	sublayers_Q = None
	
	def __init__(self, options,  id,  material, th, area):		
		# convert panda to bunch since only one row is left
		# and accessing that data is easier this way
		self.material = Bunch()
		for c in material.columns:
			self.material[c] = material[c].values[0]
		
		self.options = options
		self.id = id		
		self.th = th
		self.area = area
		self.v = area*th
		self.m = self.material.rho * self.v
		
	def to_string(self):
		s = "  L"+str(self.id)+" ("
		for i, c in enumerate(self.material):
			if i > 0:
				s = s+", "
			s = s+"{:10s}".format(str(self.material[c]))
		s = s+", {:1.3f}m".format(self.th)
		s = s+", {:1.3f}m^3".format(self.v)
		s = s+", {:3.1f}kg".format(self.m)
		s=s+")"
		return s
		
	def initialize(self, T0):
		th = 0.00001
		i = float(int(self.th / self.options.dx))
		m = self.th / self.options.dx
		if i - m > th or i == 0.0:
			print ""
			print " fatal error at "
			print "{:s}".format(self.to_string())
			print ""
			print " thickness no integer multiple of dx!"
			sys.exit(1)
		else:
			self.sl_n = int(i)
		
		self.Q0=self.m*self.material.cv*T0
	
		self.sl_th		= self.th/float(self.sl_n)
		self.sublayers_Q= np.zeros(self.sl_n)
		
		# initialize thermal energy of sublayers
		for i in range(0, self.sl_n):
			self.sublayers_Q[i] = self.Q0/float(self.sl_n)
