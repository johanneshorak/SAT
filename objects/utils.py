import sys as sys
import os.path
import ConfigParser
from bunch import Bunch
from optparse import OptionParser
from optparse import OptionGroup

def mwrite(string):
	sys.stdout.write(string)
	sys.stdout.flush()

def file_exists(fname):
	return(os.path.isfile(fname))

def parse_options():
	# strategy: read in command line options
	# if an options file is specified, the settings in there override
	# what is chosen on the command line. the command line parser options
	# are read to parser_options, the config file reader options to config.
	# the final options are stored in cl_options.
	parser = OptionParser()
	group_input = OptionGroup(parser, "input file specification",
						"These files are required to run the simulation. They "
						"may either be specified via the command line arguments "
						"or in an options file.")
	group_sim = OptionGroup(parser, "simulation options",
						"These options modify simulation parameters such as "
						"duration, initialisation temperature, etc.")
	parser.add_option_group(group_sim)
	parser.add_option_group(group_input)

	parser.add_option("-o", "--options",  dest="optfile", type="string", 
					  help="path and name of a file specifying input options and simulation options",  metavar=">file<")

	parser.add_option("-p", "--path", dest="outpath", type="string", default='./', 
					  help="destination path for simulation output", metavar=">path<")
	group_input.add_option("-f", "--forcing", dest="forcing_file", type="string", 
					  help="location and name of the atmospheric forcing", metavar=">file<")
	group_input.add_option("-z","--horizon", dest="horizon_file", type="string", 
					  help="location and name of the horizon function file", metavar=">file<")
	group_input.add_option("-c","--car", dest="car_file", type="string", 
					  help="location and name of the car general information file", metavar=">file<")
	group_input.add_option("-b","--body", dest="body_file", type="string", 
					  help="location and name of the car body file", metavar=">file<")

	group_sim.add_option("-d","--duration", dest="duration", type="float", default=2.0, 
					  help="duration of the simulation in hours", metavar=">duration<")
	group_sim.add_option("-T","--T0", dest="T0", type="float", default=20.0, 
					  help="initialisation temperature of all components in deg. Celsius", metavar=">T0<")
	group_sim.add_option("--date", dest="date", type="string",
					  help="begin of simulation date, format: YYYY-MM-DD", metavar=">date<")
	group_sim.add_option("--time", dest="time", type="string",
					  help="begin of simulation time, format: HH:MM", metavar=">time<")
	(parser_options, args) = parser.parse_args()

	cl_options = Bunch()

	if not parser_options.optfile is None:
		if file_exists(parser_options.optfile):	
			config = ConfigParser.ConfigParser()
			config.read(parser_options.optfile)
			
			print " * reading options from specified file"
			
			float_keys=["duration", "t0"]
			
			# copy all options to cl_options structure
			for sec in config.sections():
				for key in config.options(sec):
					if key in float_keys:
						if key == 't0':   # need to check this since keys are only lower case
							cl_options["T0"]=float(config.get(sec, key))
						else:
							cl_options[key]=float(config.get(sec, key))
					else:
						cl_options[key]=config.get(sec, key)
		else:
			print " error, submitted options file not found!"
			print " {:s}".format(cl_options.optfile)

	option_errors=""
	if cl_options.forcing_file is None:
		option_errors+="  please supply location and name of a forcing file\n"
	if cl_options.car_file is None:
		option_errors+="  please supply location and name of a car general information file\n"
	if cl_options.body_file is None:
		option_errors+="  please supply location and name of a car body_file\n"
	if not "horizon_file" in cl_options:			# a horizon file is no requirement. if not submitted
		cl_options.horizon_file = None				# it's just ground and sky.

	if option_errors != "":
		print ""
		print option_errors
		sys.exit(1)
		
	return cl_options
