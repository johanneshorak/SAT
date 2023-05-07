import numpy as np
from scipy import interpolate
import matplotlib as matplotlib
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import matplotlib.cm as cm
from shapely.geometry import Point
from shapely.geometry.polygon import Polygon



class Environment:
	
	horizon	= None
	
	dalpha	= None
	dbeta	= None

	epsilon_l_BLD = 0.94	# long wave emissivity of buildings
	epsilon_l_GND = 0.94	# long wave emissivity of the ground
	
	z0			  = 0.6		# surface roughness
	
	reflectivity = 0.2		# albedo of the environment

	na	= None
	nb	= None
	
	alphas	= None
	betas	= None
	ip_hor	= None	# interpolated horizon function
        
        # patches of grass should be defined with the following list. Each
        # patch of grass is another entry in the list:
        # [ [lower left corner, upper left corner, lower right corner, upper right corner ] ]
	grass = [ 
			[ [100,-75],[50,-25],[250,-85],[300,-45] ]
		]
	trees   = None
        
	grass_polygons = []
	
	ENV_SKY = 0
	ENV_BLD = 1
	ENV_GND = 2
	ENV_VEG = 3
	ENV_GRAS = 4
	
	map		= None	# 2D array
					# 0 ... sky
					# 1 ... building
					# 2 ... ground
					# 3 ... vegetation (not yet implemented)
			
	
	def __init__(self, horizon, dalpha, dbeta):
		self.horizon	= horizon
		self.dalpha		= dalpha
		self.dbeta		= dbeta
		
		self.alphas	= np.arange(0.0, 360.0+0.1*dalpha, dalpha)	# make sure that upper bound is 360 by adding a fraction of dalpha
		self.betas	= np.arange(-90.0, 90.0+0.1*dbeta, dbeta)	# make sure that upper bound is 90 by adding a fraction of dbeta
		
                # generate polygon list with grass patches
		for n in range(len(self.grass)):
			c_ll = self.grass[n][0]
			c_ul = self.grass[n][1]
			c_lr = self.grass[n][2]
			c_ur = self.grass[n][3]
			self.grass_polygons.append(Polygon([c_ll,c_lr,c_ur,c_ul]))

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
		print(self.horizon.ds.gamma.values)
		print(self.horizon.ds.alpha.values)
		#self.ip_hor = np.interp(self.alphas, self.horizon.ds.alpha.values, self.horizon.ds.gamma.values, period=360.0)	# interpolate horzion function to map resolution
		for ia, alpha in enumerate(self.alphas):
			for ib, beta in enumerate(self.betas):
				if beta > self.ip_hor[ia] and beta > 0:
					self.map[ib, ia] = self.ENV_SKY
				elif beta < self.ip_hor[ia] and beta > 0:
					self.map[ib, ia] = self.ENV_BLD
				elif beta <= 0:
					self.map[ib, ia] = self.ENV_GND
				for ig, grass_patch in enumerate(self.grass_polygons):
					if grass_patch.contains(Point(alpha,beta)):
						self.map[ib, ia] = self.ENV_GRAS
                
		# now repeat the part from 0-90 reverse at 90-180 and the part from -90 to 90 from -90 to -180
		beta_idx_m90 = int((-90.0-self.betas[0])/self.dbeta)
		beta_idx_p90 = int((90-self.betas[0])/self.dbeta)
		for ia, alpha in enumerate(self.alphas):
			for ib in range(beta_idx_m90, 0, -1):
				self.map[ib, ia] = self.map[beta_idx_m90+(beta_idx_m90-ib), ia]
			for ib in range(beta_idx_p90, self.nb, 1):
				self.map[ib, ia] = self.map[beta_idx_p90-(ib-beta_idx_p90), ia]
		self.output_environment_map()
		
	
	def output_environment_map(self):
		
		f, ax = plt.subplots(1, 1, dpi=200)
		pcm = ax.pcolormesh(self.alphas, self.betas, self.map)
		ax.set_xlim(0, 360)
		ax.set_ylim(-180, 180)
		f.colorbar(pcm)
		plt.savefig('./dbg/environment.png')
		
		pass
		
		
		
		
		
		
		
