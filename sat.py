from bunch import Bunch
from datetime import datetime,  timedelta
import sys
import time
from objects.forcing import Forcing
from objects.horizon import Horizon
from objects.physics import Physics
from objects.car import Car
from objects.environment import Environment
'''
import matplotlib as matplotlib
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import matplotlib.cm as cm
'''

# options
options                    = Bunch()
options["dx"]              = 0.001
options["model_dt"]        = 1.0
options["write_dt"]        = 60.0
options["dalpha"]          = 10.0
options["dbeta"]           = 10.0
options["write_n"]         = int(options["write_dt"]/options["model_dt"])
options["duration"]        = 3600.0*3.0
options["sim_start_dtime"] = datetime(2008, 8, 25, 11, 30)
options["lon"]             = 16.37
options["lat"]             = 48.20

# main files
forcing_file = "./input/v-w-000_forcing_25082008_1156-1700.csv"
horizon_file = "./input/horizon_fct_vu-wien.csv"
car_file     = "./input/v-w-000_general.csv"
body_file    = "./input/v-w-000_body.csv"

print " * initializing"
forcing     = Forcing(options["model_dt"], forcing_file,  options["lon"], options["lat"])
horizon     = Horizon(horizon_file)
environment = Environment(horizon, options.dalpha, options.dbeta)
physics     = Physics(environment)
car         = Car(options, car_file, body_file)

car.initialize(21.4666)

forcing.ds.to_csv('./dbg/forcing.csv')

# number of timesteps
n_ts = int(options["duration"]/options["model_dt"])+1
n_ts = 4*60*60

print ""
print " * run-info"
print "    timesteps:\t {:n}".format(n_ts)
print ""
print " * simulated vehicle"
print car.to_string()

print ""
print " * time stepping"

dt = options["model_dt"]

timer0_start = time.time()

# get everything above locally to improve efficiency
frc_G     = forcing.G
frc_H     = forcing.H
frc_Dh    = forcing.Dh
frc_T_A   = forcing.T_A
frc_T_Gnd = forcing.T_Gnd
frc_gamma = forcing.gamma
frc_psi   = forcing.psi
frc_v_1   = forcing.v_1

# loop through all timesteps
for ts in range(1, n_ts):
	t			= float(ts)*dt										# seconds passed since simulation start
	dtime_cur	= options["sim_start_dtime"]+timedelta(seconds=t)	# actual current time
	
	if ts % options["write_n"] == 0:
		timer0_end   = time.time()
		exec_text    = "time for {:n} steps: ~{:3.1f}s".format(options["write_n"], timer0_end-timer0_start)
		tleft_min    = float(n_ts-ts)*(timer0_end-timer0_start)/(60.0*options["write_dt"])
		
		if tleft_min > 60.0:
			tleft_hrs    = tleft_min%60
			tleft_min    = tleft_min-60.0*float(tleft_hrs)
			tleft_text   = "time left: ~ {:3.1f}h:{:3.1f}m.".format(tleft_hrs, tleft_min)
		else:
			tleft_hrs    = 0.0
			tleft_text   = "time left: ~ {:3.1f} min.".format(tleft_min)
			

		timer0_start = time.time()

		print "   - timestep {:6n}/{:6n}\t{:18s}\t{:26s}\t{:26s}".format(ts, n_ts, dtime_cur.strftime("%Y-%m-%d %H:%M:%S"), exec_text, tleft_text)
	
	
	out          = ""						# output string
	timer1_start = time.time()
	
	for nw,  wall in enumerate(car.walls):	# loop through all walls and layers and calculate/apply the relevant heat fluxes
		
		nw_opp 	= 7-(nw+1)-1 		# id of the opposing wall
		K_sum 	= 0 				# convective heat flux btw. walls and cabin air
		fluxes 	= Bunch()			# debug variable that will contain the environmental and interiod heat fluxes
		
		for np, part in enumerate(wall.parts):
			
			for nl,  layer in enumerate(part):
				sn = layer.sl_n
				
				for sl,  slayer in enumerate(layer.sublayers_Q_tm1):
					# depending on whether we are dealing with a layer of which one side
					# faces either the environment, the interior or both we have to consider
					# the relevant heat fluxes.
					area	= layer.area
					alpha	= wall.alpha
					beta	= wall.beta

					# at the moment only one surface can be defined for each layer
					# that means if there's a wall that constist of only one layer,
					# then the optical properties will be the same on the inside and
					# on the outside. A workaround would be to define two layers of the
					# same material.
					if layer.outer == True or layer.inner == True:
						alpha_s   = layer.surface.alpha_s
						tau_s	  = layer.surface.tau_s
						alpha_l   = layer.surface.alpha_l
						epsilon_l = layer.surface.epsilon_l
					else:
						alpha_s   = 0
						tau_s     = 0
						alpha_l   = 0
						epsilon_l = 0
					
					T_i     = layer.sl_temp(sl)	# temperature of the current sublayer at the last timestep
					T_cabin = car.cair_temp()	# cabin air temperature at the last timestep
					
					C = 0						# conductive heat flux btw. adjacent sublayers (W/m^2)
					K_env = 0					# convective heat flux btw. sublayer and environment (W/m^2)
					K_int = 0					# convective heat flux btw. sublayer and interior (W/m^2)
					R_S_env = 0					# short wave heat flux btw. sublayer and environment (W/m^2)
					R_S_int = 0					# short wave heat flux btw. sublayer and interior (W/m^2)
					R_L_env = 0					# long wave heat flux btw. sublayer and environment (W/m^2)
					R_L_int = 0					# long wave heat flux btw. sublayer and interior (W/m^2)
					R_L_S	= 0					# total long wave heat flux emitted by sublayer
					R_L_S_int = 0				# long wave heat flux emitted by sublayer towards interior
					R_L_S_env = 0				# long wave heat flux emitted by sublayer towards environment
					
					th          = layer.sl_th					# thickness of the sublayer in (m)
					l_i         = layer.material.conductivity	# thermal conductivity of the sublayers material (W/Km)
					#forcing_cur = forcing.ds.ix[ts]				# interpolated forcing at the current timestep
					
					procedure_applied = ""		# additional information - if this still has no values after
												# the if blocks below then we encountered a vehicle configuration
												# we have not considered yet and don't know which heat fluxes to apply
					
					if sl > 0 and sl<sn-1:
						# sublayer is somewhere whithin a bulk of material - consider only conduction
						procedure_applied = "m "
						T_im1 = layer.sl_temp(sl-1)
						T_ip1 = layer.sl_temp(sl+1)
						
						Cim1 = physics.conduction(T_im1, T_i, layer.material.conductivity,  th)
						Cip1 = physics.conduction(T_i, T_ip1, layer.material.conductivity,  th)
						C    = Cim1-Cip1
					else:
						if sl == 0 and layer.outer and sn > 1:
							# sublayer is the outermost and faces the environment but does not face the interior
							procedure_applied = "o1"
							
							T_ip1 = layer.sl_temp(sl+1)
							
							C		= physics.conduction(
														T_i,
														T_ip1,
														layer.material.conductivity,
														th
													)
							R_S_env	= physics.sw_terms(
														frc_G[ts],
														frc_Dh[ts],
														frc_H[ts],
														frc_gamma[ts],
														frc_psi[ts], 
														alpha,
														beta
													)
							R_L_env,  R_L_S_env = physics.lw_terms(
														frc_T_A[ts],
														frc_T_Gnd[ts],
														T_i,
														None,
														epsilon_l,
														None,
														alpha,
														beta
													)
							K_env	= physics.convection(
														frc_T_A[ts],
														T_i,
														frc_v_1[ts]
													)
													
						elif sl == 0 and layer.outer and sn == 1:
							# sole sublayer is the outermost and faces the environment but has another adjacent layer inwards
							procedure_applied = "o2"
							
							T_ip1	= part[nl+1].sl_temp(0) # temperature of next layer inwards
							l_ip1	= part[nl+1].material.conductivity

							C		= -(T_i-T_ip1)*physics.thermal_contact_conductivity(
														l_i,
														l_ip1
													)
							R_S_env = physics.sw_terms(
														frc_G[ts],
														frc_Dh[ts],
														frc_H[ts],
														frc_gamma[ts],
														frc_psi[ts], 
														alpha,
														beta
													)
							R_L_env,  R_L_S_env  = physics.lw_terms(
														frc_T_A[ts],
														frc_T_Gnd[ts],
														T_i,
														None,
														epsilon_l,
														None,
														alpha,
														beta
													)
							K_env	= physics.convection(
														frc_T_A[ts],
														T_i,
														frc_v_1[ts]
													)
													
						elif sl == 0 and not layer.outer and sn > 1:
							# sublayer is the outermost but doesn't face the environment => faces other layer outwards (thermal contact)
							# => read neccessary thermal properties of this layer and calculate conductivity due to thermal contact.
							procedure_applied = "o3"
							T_im1	= part[nl-1].sl_temp(part[nl-1].sl_n-1) # temperature of next layer outwards
							l_im1	= part[nl-1].material.conductivity
							#print " T_i=", T_i, " T_im1=",  T_im1, " l_im1=", l_im1,  " ", part[nl-1].sl_n-1, " ",  nl-1
							C = (T_im1-T_i)*physics.thermal_contact_conductivity(l_im1, l_i)
							
							
						if sl == sn-1 and layer.inner and sn > 1:			
							# sole sublayer is the innermost and faces the interior but does not face the outside
							procedure_applied = "i1"

							T_im1 = layer.sl_temp(sl-1)
							
							T_opp = car.walls[nw_opp].parts[0][-1].sl_temp(car.walls[nw_opp].parts[0][-1].sl_n-1)
							epsilon_l_opp = car.walls[nw_opp].parts[0][-1].surface.epsilon_l
							
							C		= physics.conduction(T_im1, T_i, layer.material.conductivity,  th)
							R_S_int = 0
							R_L_int,  R_L_S_int  = physics.lw_terms(
														frc_T_A[ts],
														frc_T_Gnd[ts],
														T_i,
														T_opp,
														epsilon_l,
														epsilon_l_opp,
														alpha,
														beta
													)
							K_int	= physics.convection(T_cabin, T_i, 0.0)
						elif sl == 0 and layer.inner and sn == 1:
							# sole sublayer is the innermost and faces the interior but has another ajdacent layer outward
							procedure_applied = "i2"
							
							T_im1	= part[nl-1].sl_temp(part[nl-1].sl_n-1) # temperature of next layer outward
							l_im1	= part[nl-1].material.conductivity
							
							T_opp = car.walls[nw_opp].parts[0][-1].sl_temp(car.walls[nw_opp].parts[0][-1].sl_n-1)
							epsilon_l_opp = car.walls[nw_opp].parts[0][-1].surface.epsilon_l

							C = (T_im1-T_i)*physics.thermal_contact_conductivity(l_i, l_ip1)
							R_S_int	= 0
							R_L_int,  R_L_S_int  = physics.lw_terms(
														frc_T_A[ts],
														frc_T_Gnd[ts],
														T_i,
														T_opp,
														epsilon_l,
														epsilon_l_opp,
														alpha,
														beta
													)
							K_int	= physics.convection(T_cabin, T_i, 0.0)
						elif sl == sn-1 and not layer.inner and sn > 1:
							# sublayer is the innermost but doesn't face the interior => faces other layer inwards
							# => read neccessary thermal properties of this layer and calculate conductivity due to thermal contact. 
							procedure_applied = "i3"
							T_ip1	= part[nl+1].sl_temp(0) # temperature of next layer inwards
							l_ip1	= part[nl+1].material.conductivity

							C = (T_i-T_ip1)*physics.thermal_contact_conductivity(l_i, l_ip1)
							R_S_int = 0
					
					if procedure_applied == "":
						print "fatal error! encountered a situation where no way was found to deal"
						print "with the current layer/sublayer!"
						print "wall {:2n} part {:2n} layer {:2n} sublayer {:2n}".format(nw+1, np+1,  nl+1, sl+1)
						sys.exit(0)
					
					# some adjustments:
					if nw+1 == 2:					# current wall is floor of the vehicle
						R_S_env = 0					# approximation: no environmental short wave fluxes here
					
					R_S	  = R_S_env + R_S_int
					R_L	  = R_L_env + R_L_int
					R_L_S = R_L_S_env + R_L_S_int
					K	  = K_env + K_int

					dQ = dt*area*(alpha_s*R_S+alpha_l*R_L-R_L_S+C+K)				# calculate heat gain/loss of sublayer
					layer.sublayers_Q_t[sl] = layer.sublayers_Q_tm1[sl]+dQ			# calculate heat of sublayer at current timestep
					
					if nl == len(part)-1 and sl == len(layer.sublayers_Q_tm1)-1:	# current layer is adjacent to cabin air
						K_sum = K_sum - K_int*dt*area								# keep track of heat exchange with it
						#print "\t", R_L_S, "\t", R_L_S_env, "\t", R_L_S_int
						
						fluxes["R_S_int"]	= R_S_int								# store these fluxes for output
						fluxes["R_L_int"]	= R_L_int								# store these fluxes for output
						fluxes["K_int"]		= K_int									# store these fluxes for output
						fluxes["eta"]		= physics.last_eta
						fluxes["D"]			= physics.last_D
						fluxes["R_L_S_int"] = R_L_S_int

					if nl == 0 and sl == 0:											# current layer is adjacent to environment
						#print "\t", R_L_S, "\t", R_L_S_env, "\t", R_L_S_int
						fluxes["R_S_env"]	= R_S_env								# store these fluxes for output
						fluxes["R_L_env"]	= R_L_env								# store these fluxes for output
						fluxes["R_L_hspace"]= physics.last_R_L_env
						fluxes["K_env"]		= K_env									# store these fluxes for output
						fluxes["eta"]		= physics.last_eta
						fluxes["D"]			= physics.last_D
						fluxes["R_L_S_env"] = R_L_S_env
					
					if nw != 10 and ts % options["write_n"] == 0:
						#print "wall {:2n} part {:2n} layer {:2n} sublayer {:2n} - T = {:5.3f} dQ = {:5.3f} R_S = {:5.3f} R_L = {:5.3f} K = {:5.3f}".format(nw+1, np+1,  nl+1, sl+1, T_i,  dQ, R_S, R_L, K)
						pass						

		if ts % options["write_n"] == 0 or ts == 0:
			wall.debug_to_file(dtime_cur, float(ts)*dt/3600.0, fluxes)
			pass
	timer1_end = time.time()
	#print "\twallloop: {:3.1f}".format(timer1_end-timer1_start)


	car.Q_t = car.Q_tm1 + K_sum
	car.Q_tm1 = car.Q_t
	
	if ts % options["write_n"] == 0:
		car.output_cair(dtime_cur, float(ts)*dt/3600.0)
	
	# at the end of the timestep tm-1 = t
	for nw,  wall in enumerate(car.walls):
		for np, part in enumerate(wall.parts):
			for nl,  layer in enumerate(part):
				layer.sublayers_Q_tm1 = layer.sublayers_Q_t

car.walls[0].debug_file_close()
car.walls[1].debug_file_close()
car.walls[2].debug_file_close()
car.walls[3].debug_file_close()
car.walls[4].debug_file_close()
car.walls[5].debug_file_close()
car.output_close()


#print forcing.ds
#print horizon.ds
#print materials.ds
#print surfaces.ds


'''
fig, ax = plt.subplots(1, 1)	
ax.scatter(forcing_ds.index.values, forcing_ds.G.values)
ax.set_xlim([forcing_ds.index[0], forcing_ds.index[-1]])
plt.savefig('testplot.png')
plt.close()
'''
