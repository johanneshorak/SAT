import numpy as np


class Physics():

	eta_ij_map = None
	environment = None
	
	kappa_table=[ [253 ,254 ,255 ,256 ,257 ,258 ,259 ,260 ,261 ,262 ,263 ,264 ,265 ,266 ,267 ,268 ,269 ,270 ,271 ,272 ,273 ,274 ,275 ,276 ,277 ,278 ,279 ,280 ,281 ,282 ,283 ,284 ,285 ,286 ,287 ,288 ,289 ,290 ,291 ,292 ,293 ,294 ,295 ,296 ,297 ,298 ,299 ,300 ,301 ,302 ,303 ,304 ,305 ,306 ,307 ,308 ,309 ,310 ,311 ,312 ,313 ],
				  [0.62 ,0.68 ,0.74 ,0.8 ,0.87 ,0.95 ,1.03 ,1.1 ,1.19 ,1.28 ,1.37 ,1.47 ,1.58 ,1.7 ,1.82 ,1.95868 ,2.08947 ,2.229 ,2.37784 ,2.53662 ,2.70601 ,2.88671 ,3.07947 ,3.28511 ,3.50447 ,3.73849 ,3.98813 ,4.25444 ,4.53854 ,4.84161 ,5.16491 ,5.5098 ,5.87773 ,6.27022 ,6.68892 ,7.13558 ,7.61207 ,8.12037 ,8.66262 ,9.24108 ,9.85816 ,10.5165 ,11.2187 ,11.9678 ,12.9 ,13.9 ,14.9 ,16.0 ,17.3 ,18.8 ,20.4 ,22.1 ,24.2 ,26.6 ,28.9 ,31.7 ,35.4 ,39.4 ,44.2 ,49.8 ,57.3]]
	
	f_tpow4_lookup = False		# flag - use t**4 lookup table?
	
	# parameters that define the t**4 lookup table
	tpow4_min_t	 = 200.0
	tpow4_max_t	 = 120.0 + 273.15
	tpow4_dt	 = 0.5
	tpow4_lookup = None						# lookup table that contains values of t and t**4

	def __init__(self, environment):
		self.environment = environment
		
		if self.tpow4_lookup is None:
			steps = int((self.tpow4_max_t-self.tpow4_min_t)/self.tpow4_dt)
			self.tpow4_lookup = np.zeros(steps+1)
			for i in range(0, steps+1):
				self.tpow4_lookup[i] = (float(i)*self.tpow4_dt+self.tpow4_min_t)**4		

	def tpow4(self, t):
		if self.f_tpow4_lookup:
			idx = int((t-self.tpow4_min_t)/self.tpow4_dt)
			return self.tpow4_lookup[idx]
		else:
			return t**4

	# standard heat conduction
	# source: Horak et al. 2016 section 2.1 
	def conduction(self, ti, tip1,  l, th):
		q = l/th*(ti-tip1)
		return q
	
	def find_nearest(self, array, value):
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
	
	# calculate the angle oalphai-alpha, betaj-beta+90.0f incidence for an oriented plain
	# angles given in degree in spherical coordinates. meaning
	# gamma and beta must be supplied as zenith angles
	def eta(self, alpha,  beta,  psi,  gamma):
		
		'''
		ax = np.sin((np.pi/180.0)*beta)*np.cos((np.pi/180.0)*alpha)
		ay = np.sin((np.pi/180.0)*beta)*np.sin((np.pi/180.0)*alpha)
		az = np.cos((np.pi/180.0)*beta)
		
		bx = np.sin((np.pi/180.0)*gamma)*np.cos((np.pi/180.0)*psi)
		by = np.sin((np.pi/180.0)*gamma)*np.sin((np.pi/180.0)*psi)
		bz = np.cos((np.pi/180.0)*gamma)
			
		sp = ax*bx+ay*by+az*bz
		
		eta_v = (180.0/np.pi) * np.arccos(sp)
		'''
		term1 = np.sin((np.pi/180.0)*gamma)*np.cos((np.pi/180.0)*beta)
		term2 = np.cos((np.pi/180.0)*gamma)*np.sin((np.pi/180.0)*beta)*np.cos((np.pi/180.0)*(alpha-psi))
		eta_v = (180.0/np.pi)*np.arccos(term1+term2)


		return eta_v
	
	def stefan_boltzmann(self, epsilon, T):
		tpow4 = self.tpow4(T+273.15)
		return epsilon*5.67*10.0E-9*tpow4

	def to_horizon_angle(self, angle_zenith):
		angle = 90-angle_zenith
		return angle
	
	def R_L_env(self, T_A, T_Gnd, alpha, beta_zenith):
		beta = self.to_horizon_angle(beta_zenith)						# beta has to be converted to a horizon angle
		
		alpha0 = (alpha-90.0-0.0*self.environment.dalpha)%360.0			# adding / substracting halve a step avoids problems
		alpha1 = (alpha+90.0+0.0*self.environment.dalpha)%360.0
		beta0 = (beta-90.0+0.0*self.environment.dbeta)
		beta1 = (beta+90.0-0.0*self.environment.dbeta)
		#print "*"
		#print "alpha0=", alpha0, " alpha1=", alpha1, " - beta0=", beta0, " beta1=", beta1

		if beta0 < 0 and beta0 != -180.0:
			beta0 = beta0%-180
		elif beta0 > 0:
			if beta0 != 180.0:
				beta0 = beta0%180
				
		if beta1 < 0 and beta1 != 180.0:
			beta1 = beta1%-180
		elif beta1 > 0:
			if beta1 != 180.0:
				beta1 = beta1%180
		
		a0 = int(alpha0/self.environment.dalpha)						#self.find_nearest(self.environment.alphas, alpha0)
		a1 = a0 + int(abs(alpha1-alpha0)/self.environment.dalpha)+1
	
		b0 = int((beta0-self.environment.betas[0])/self.environment.dbeta)
		#b0 = self.find_nearest(self.environment.betas, beta0)
		b1 = b0 + int((beta1-beta0)/self.environment.dbeta)

		#print "a0 = ", a0, " a1 = ", a1, "; b0 = ", b0, " b1 = ", b1,  " b0raw = ", (beta0-self.environment.betas[0])/self.environment.dbeta
		# now we need to generate a list of alpha and beta indizes that tell us which parts of
		# the environment map the current wall faces.

		#print "alpha = ", alpha, " beta = ", beta, " beta_zenith = ", beta_zenith
		#print "alpha0=", alpha0, " alpha1=", self.environment.alphas[a1%self.environment.na], " - beta0=", beta0, " beta1=", beta1
		
		#self.map	= np.zeros((a1-a0)*(b1-b0))
		#self.map	= self.map.reshape((b1-b0), (a1-a0))
		
		R_L_env = 0
		terms =  0
		
		# during the first execution of this routine we create a eta_ij map to save time
		# since it will always be the same.
		if self.eta_ij_map is None:
			create_eta_ij_map = True
			self.eta_ij_map = np.zeros((a1-a0)*(b1-b0))
			self.eta_ij_map = self.eta_ij_map.reshape((b1-b0), (a1-a0))
		else:
			create_eta_ij_map = False
		
		for na in range(a0, a1):
			for nb in range(b0, b1):
				a_idx = na%self.environment.na
				b_idx = nb
				Lij = 0
							
				alphai	= self.environment.alphas[a_idx]
				betaj	= self.environment.betas[b_idx]
				
				#betaj_zenith = 90-betaj
				if create_eta_ij_map:
					self.eta_ij_map[nb-b0, na-a0] = self.eta(alphai-alpha, betaj-beta+90.0, 0.0, 0.0)
					
				eta_ij = self.eta_ij_map[nb-b0, na-a0]
				
				if self.environment.map[b_idx, a_idx] == self.environment.ENV_SKY:
					esky=self.epsilon_sky(betaj, T_A)
					Lij=(1/np.pi)*self.stefan_boltzmann(esky, T_A)
				elif self.environment.map[b_idx, a_idx] == self.environment.ENV_BLD:
					Lij=(1/np.pi)*self.stefan_boltzmann(self.environment.epsilon_l_BLD, T_A)
				elif self.environment.map[b_idx, a_idx] == self.environment.ENV_GND:
					Lij=(1/np.pi)*self.stefan_boltzmann(self.environment.epsilon_l_GND, T_Gnd) # in ICOV T_Gnd was erroneously = T_A. Setting T_A here leads to ICOV behaviour
				elif self.environment.map[b_idx, a_idx] == self.environment.ENV_VEG:
					pass
								
				term_lambertslaw=np.cos((betaj-beta)*(np.pi/180.0))			# cosine law
				
				Lij_aoi = term_lambertslaw*np.cos((np.pi/180.0)*eta_ij)*Lij
				Lij_aoi_flx = ((np.pi/180.0)**2)*self.environment.dalpha*self.environment.dbeta*Lij_aoi
				#self.map[nb-b0, na-a0] = Lij_aoi_flx
				
				terms = terms + 1
				R_L_env = R_L_env + Lij_aoi_flx
		#print "terms = ",terms," R_L_env = ", R_L_env, " ", R_L_env_alt, " ", ((np.pi/180.0)**2)*self.environment.dalpha*self.environment.dbeta
		'''
		print R_L_env
		plt.clf()		
		plt.pcolormesh(self.map)
		plt.colorbar()
		#plt.xlim([alphas[0], alphas[-1]])
		#plt.ylim([betas[0], betas[-1]])
		plt.savefig('./dbg/aij_alpha-'+str(alpha)+'_beta-'+str(beta_zenith)+'.png')
		plt.close()
		sys.exit(0)
		'''
		'''
		plt.clf()		
		plt.pcolormesh(self.eta_ij_map)
		plt.colorbar()
		#plt.xlim([alphas[0], alphas[-1]])
		#plt.ylim([betas[0], betas[-1]])
		plt.savefig('./dbg/eta_ij_map.png')
		'''
		'''
		if alpha == 0 and beta_zenith==180:
			print "*"
			print R_L_env
			print " alpha = ", alpha, " beta = ",  beta,  " beta_zenith = ",  beta_zenith
			print "alpha0=", alpha0, " alpha1=", alpha1, " - beta0=", beta0, " beta1=", beta1
			print "a0=", a0, " a1=", a1, " - b0=", b0, " b1=", b1
			#print self.environment.alphas[a0], "-", self.environment.alphas[a1] , " = ", (self.environment.alphas[a1]-self.environment.alphas[a0])
			print self.environment.betas[b0], "-", self.environment.betas[b1] , " = ", (self.environment.betas[b1]- self.environment.betas[b0])
			print self.map
			for alphatest in np.arange(100.0, 250.0, 10.0):
				print alphatest, ": ", self.eta(alpha, beta_zenith, alphatest, 90.0)
			#sys.exit(0)
		'''
		
		self.last_R_L_env = R_L_env
		return R_L_env
		
	def lw_terms(self, T_A, T_Gnd, TS, TS_opp, eps_l, eps_l_opp, alpha, beta):
		# preliminary we use a really simple approximation for R_env

		R_L_S	= self.stefan_boltzmann(eps_l, TS)		# lw radiation given of by surface
		
		if eps_l_opp is None or TS_opp is None:			# considering outer surface
			R_L_opp = 0
			R_L_env = self.R_L_env(T_A, T_Gnd, alpha, beta)
		else:											# considering inner surface
			#eps_l_opp = 1.0							# assume: inside is blackbody
			R_L_opp	= self.stefan_boltzmann(eps_l_opp, TS_opp)
			R_L_env = 0

		R_L = R_L_env+R_L_opp
		return R_L,  R_L_S
	
	def convection(self, T_air, T_sfc, vw):
		K = (2.8 + 3.0*vw)*(T_air-T_sfc)
		return K
	
	def sw_terms(self, G,  Dh, H,  gamma,  psi, alpha,  beta_zenith):
		horizon = (np.pi/180.0)*self.environment.horizon_at((180.0/np.pi)*psi)	# elevation angle of horizon at psi (degree)

		eta     = self.eta(alpha, beta_zenith, (180.0/np.pi)*psi, (180.0/np.pi)*gamma)
		self.last_eta = eta
		
		# this should at some point be calculated from the environment map
		# as of now it is only correct for walls parallel or perpendicular to
		# the ground. Basically the fraction of reflected / diffuse radiation picked
		# up by a wall depends on how much of the sky/ground it sees.
		
		if beta_zenith==0.0:		# top wall doesnt pick up reflected radiation
			Ho = H
			R_S_gnd = 0
		elif beta_zenith == 90.0:
			Ho = H
			R_S_gnd = self.environment.reflectivity*G
		elif beta_zenith == 180.0:
			Ho = 0
			R_S_gnd = 0 #self.environment.reflectivity*G
			
		if gamma > horizon:		# sun is above the horizon
			if eta > 90.0:
				R_S_sky = Ho # 0
				self.last_D = 0
			else:
				R_S_sky = np.cos((np.pi/180.0)*eta)*Dh + Ho
				self.last_D = np.cos((np.pi/180.0)*eta)*Dh
		else:					# sun is below the horizon
			R_S_sky = Ho
			self.last_D = 0
			
		R_S = R_S_sky + R_S_gnd
			
		return R_S
			

	def main_loop(self, car, wall):
		pass
		
