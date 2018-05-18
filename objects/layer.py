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
	
	sl_th = None		# thickness of sublayers
	sl_n = None			# number of sublayers
	sublayers_Q_tm1 = None	# array containing the thermal energy of the sublayers of the previous timestep
	sublayers_Q_t = None	# array containing the thermal energy of the sublayers of the current timestep
	
	outer=False
	inner=False
	
	def __init__(self, options,  id,  material, surface,  th, area):		
		# convert panda to bunch since only one row is left
		# and accessing that data is easier this way
		self.material = Bunch()
		for c in material.columns:
			self.material[c] = material[c].values[0]
		
		if surface is not None:
			self.surface = Bunch()
			for c in surface.columns:
				self.surface[c] = surface[c].values[0]
		else:
			self.surface = None

		self.options = options
		self.id = id		
		self.th = th
		self.area = area
		self.v = area*th
		self.m = self.material.rho * self.v
		
	def to_string(self):
		s = "      L"+str(self.id)
		if self.inner == True and self.outer==True:
			s = s + " inout"
		elif self.inner == True:
			s = s + " inner"
		elif self.outer == True:
			s = s + " outer"
		
		s = s + " ("
		if self.surface is not None:
			s = s + self.surface.name+"\t"
		else:
			s = s + "nosfc\t"
			
		for i, c in enumerate(self.material):
			if i > 0:
				s = s+", "
			s = s+"{:10s}".format(str(self.material[c]))
		s = s+", {:1.3f}m".format(self.th)
		s = s+", {:1.3f}m^2".format(self.area)
		s = s+", {:1.3f}m^3".format(self.v)
		s = s+", {:3.1f}kg".format(self.m)
		s=s+")"
		return s
		
	# returns the temperature of sublayer n
	def sl_temp(self, n):
		return (float(self.sl_n)*self.sublayers_Q_tm1[n])/(self.m*self.material.cv)
		
	def initialize(self, T0):
		th = 0.00001
		i = float(int(self.th / self.options.dx))
		m = self.th / self.options.dx
		if i - m > th or i == 0.0:
			print("")
			print(" fatal error at ")
			print("{:s}".format(self.to_string()))
			print("")
			print(" thickness no integer multiple of dx!")
			sys.exit(1)
		else:
			self.sl_n = int(i)
		
		self.Q0=self.m*self.material.cv*T0
	
		self.sl_th			 = self.th/float(self.sl_n)
		self.sublayers_Q_tm1 = np.zeros(self.sl_n)
		self.sublayers_Q_t	 = np.zeros(self.sl_n)
		
		# initialize thermal energy of sublayers
		for i in range(0, self.sl_n):
			self.sublayers_Q_tm1[i] = self.Q0/float(self.sl_n)
			
		if np.sum(self.sublayers_Q_tm1) / self.Q0 - 1.0 > th:
			print(" fatal error at")
			print("{:s}".format(self.to_string()))
			print("")
			print(" sum of sublayer thermal energy does not equal expected energy of a layer!")
			print(" sum of sublayer thermal energies: {:f}".format(np.sum(self.sublayers_Q_tm1)))
			print(" expected total energy of layer  : {:f}".format(self.Q0))
			sys.exit(1)
