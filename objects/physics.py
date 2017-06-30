import numpy as np
import sys
class Physics():

	
	environment = None
	
	kappa_table=[ [253 ,254 ,255 ,256 ,257 ,258 ,259 ,260 ,261 ,262 ,263 ,264 ,265 ,266 ,267 ,268 ,269 ,270 ,271 ,272 ,273 ,274 ,275 ,276 ,277 ,278 ,279 ,280 ,281 ,282 ,283 ,284 ,285 ,286 ,287 ,288 ,289 ,290 ,291 ,292 ,293 ,294 ,295 ,296 ,297 ,298 ,299 ,300 ,301 ,302 ,303 ,304 ,305 ,306 ,307 ,308 ,309 ,310 ,311 ,312 ,313 ],
				  [0.62 ,0.68 ,0.74 ,0.8 ,0.87 ,0.95 ,1.03 ,1.1 ,1.19 ,1.28 ,1.37 ,1.47 ,1.58 ,1.7 ,1.82 ,1.95868 ,2.08947 ,2.229 ,2.37784 ,2.53662 ,2.70601 ,2.88671 ,3.07947 ,3.28511 ,3.50447 ,3.73849 ,3.98813 ,4.25444 ,4.53854 ,4.84161 ,5.16491 ,5.5098 ,5.87773 ,6.27022 ,6.68892 ,7.13558 ,7.61207 ,8.12037 ,8.66262 ,9.24108 ,9.85816 ,10.5165 ,11.2187 ,11.9678 ,12.9 ,13.9 ,14.9 ,16.0 ,17.3 ,18.8 ,20.4 ,22.1 ,24.2 ,26.6 ,28.9 ,31.7 ,35.4 ,39.4 ,44.2 ,49.8 ,57.3]]
	
	def __init__(self, environment):
		self.environment = environment

	# standard heat conduction
	# source: Horak et al. 2016 section 2.1 
	def conduction(self, ti, tip1,  l, th):
		q = l/th*(ti-tip1)
		return q
	
	def find_nearest(self, array,value):
		idx = (np.abs(array-value)).argmin()
		return idx
	
	def kappa(self, TA):
		idx=self.find_nearest(self.kappa_table[0], TA+273.15)
		return self.kappa_table[1][idx]
	
	def epsilon_sky(self, beta, TA):
		theta = (np.pi/180.0)*abs(beta-90.0)	# angle measured from horizon (beta) to zenith angle (theta)
		kappa = self.kappa(TA)
		
		esky = 1-0.5*np.exp(-0.3*(kappa/np.cos(theta))**0.5)
		
		return esky
	
	# thermal conductivity alpha_c
	# source: Horak et al. 2016 section 2.1
	def thermal_contact_conductivity(self, l1, l2):
		dC = 0.0001	# average spacing btw. layers
		AC = 0.5	# relative area of direct contact
		lc = 0.026	# heat conductivity of air
		
		term1=AC*(l1*l2)/(l1+l2)
		term2=(1.0-AC)*lc
		alpha_c = (1.0/dC)*(term1+term2)
		
		return alpha_c
				
	def H(self):
		pass
	
	# calculate the angle of incidence for an oriented plain
	def eta(self, alpha,  beta,  psi,  gamma):
		vector_1x = np.sin((np.pi/180.0)*beta)*np.cos((np.pi/180.0)*alpha)
		vector_1y = np.sin((np.pi/180.0)*beta)*np.sin((np.pi/180.0)*alpha)
		vector_1z = np.cos((np.pi/180.0)*beta)
		vector_2x = np.sin((np.pi/180.0)*gamma)*np.cos((np.pi/180.0)*psi)
		vector_2y = np.sin((np.pi/180.0)*gamma)*np.sin((np.pi/180.0)*psi)
		vector_2z = np.cos((np.pi/180.0)*gamma)
		
		sp = vector_1x*vector_2x+vector_1y*vector_2y+vector_1z*vector_2z
		
		eta = (180.0/np.pi) * np.arccos(sp)
		
		return eta
	
	def stefan_boltzmann(self, epsilon, T):
		return epsilon*5.67*10.0E-8*(T+273.15)**4
		
	def lw_terms(self, forcing, TS, TS_opp, eps_l, eps_l_opp, alpha, beta):
		# preliminary we use a really simple approximation for R_env

		R_L_S	= self.stefan_boltzmann(eps_l, TS)
		
		if eps_l_opp is None or TS_opp is None:
			R_L_opp = 0
			R_gnd	= self.stefan_boltzmann(0.9, forcing.T_Gnd)
			R_sky	= self.stefan_boltzmann(0.7, forcing.T_A)
			R_L_env = 0.75*R_gnd+0.25*R_sky
		else:
			R_L_opp	= self.stefan_boltzmann(eps_l_opp, TS_opp)
			R_L_env = 0

		esky=self.epsilon_sky(beta, forcing.T_A)
		print esky
		sys.exit()
		
		R_L = R_L_env+R_L_opp-R_L_S
		return R_L
	
	def convection(self, T_air, T_sfc, vw):
		K = (2.8 + 3.0*vw)*(T_air-T_sfc)
		return K
	
	def sw_terms(self, forcing, alpha,  beta):
		G = forcing.G
		Dh = forcing.Dh
		H = forcing.H							
		gamma = forcing.gamma										# elevation angle of the sun (rad)
		psi	  = forcing.psi											# azimuth angle of the sun (rad)
		horizon = self.environment.horizon_at((180.0/np.pi)*psi)	# elevation angle of horizon at psi (degree)

		eta = self.eta(alpha, beta, psi, gamma)
		
		if gamma > horizon:		# sun is above the horizon
			R_S_sky = np.cos((np.pi/180.0)*eta)*Dh + H
		else:					# sun is below the horizon
			R_S_sky = H
	
		R_S_gnd = 0.2*G
		R_S = R_S_sky + R_S_gnd
		
		return R_S
			
		
