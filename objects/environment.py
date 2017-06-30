import numpy as np
from scipy import interpolate
import matplotlib as matplotlib
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import matplotlib.cm as cm

class Environment:
	
	
	horizon	= None
	dalpha	= None
	dbeta	= None

	na	= None
	nb	= None
	
	alphas	= None
	betas	= None
	ip_hor	= None	# interpolated horizon function
	
	
	map		= None	# 2D array
					# 0 ... sky
					# 1 ... building
					# 2 ... ground
					# 3 ... vegetation (not yet implemented)
			
	
	def __init__(self, horizon, dalpha, dbeta):
		self.horizon	= horizon
		self.dalpha		= dalpha
		self.dbeta		= dbeta
		
		self.alphas	= np.arange(0.0, 360.0, dalpha)
		self.betas	= np.arange(-90.0, 90.0, dbeta)
		
		self.na = len(self.alphas)
		self.nb = len(self.betas)
		
		self.map	= np.zeros(self.na*self.nb)
		self.map	= self.map.reshape(self.nb, self.na)
		
		self.horizon_fct = interpolate.interp1d(self.horizon.ds.alpha.values, self.horizon.ds.gamma.values,bounds_error=False, fill_value=0, kind='nearest')
		
		self.generate_surrounding_map()
		
	# returns the value of the horizon function at a given alpha
	def horizon_at(self, alpha):
		return self.horizon_fct(alpha)
		
	def generate_surrounding_map(self):
		self.ip_hor = self.horizon_fct(self.alphas)
		#self.ip_hor = np.interp(self.alphas, self.horizon.ds.alpha.values, self.horizon.ds.gamma.values, period=360.0)	# interpolate horzion function to map resolution
		for ia, alpha in enumerate(self.alphas):
			for ib, beta in enumerate(self.betas):
				if beta > self.ip_hor[ia] and beta > 0:
					self.map[ib, ia] = 0
				elif beta < self.ip_hor[ia] and beta > 0:
					self.map[ib, ia] = 1
				elif beta <= 0:
					self.map[ib, ia] = 2
				
		self.output_environment_map()
	
	def output_environment_map(self):
		plt.pcolormesh(self.alphas, self.betas, self.map)
		plt.savefig('./dbg/environment.png')
		
		
		
		
		
		
		
