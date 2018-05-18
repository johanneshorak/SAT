import sys
from bunch import Bunch
from objects.layer import Layer
from objects.wall import Wall
from objects.materials import Materials
from objects.surfaces import Surfaces
from objects.reader_csv import Reader_CSV

class Car:

	reader = None
	reader_body = None
	materials = None
	surfaces = None
	options = None
	walls = []
	
	output_file = None
	
	materials_file="./data/materials.csv"
	surfaces_file="./data/surfaces.csv"
	
	# the variables required in the forcing data
	fields_required_body = [
		'wall', 
		'part', 
		'layer', 
		'material', 
		'surface', 
		'a_eff', 
		'th'
	]
	
	fields_required_general = [
		'code', 
		'description', 
		'alpha', 
		'beta', 
		'l', 
		'w', 
		'h'
	]
	
	body = None
	
	Q_t = None
	Q_tm1 = None
	
	def __init__(self, options,  general_loc, body_loc):
		self.options = options
		
		self.reader = Reader_CSV(general_loc, self.fields_required_general, 'car-general')
		general = self.reader.load()
		
		self.general = Bunch()
		for c in general:
			self.general[c] = general[c].values[0]
		
		self.v = self.general.l*self.general.w*self.general.h
		
		self.reader_body = Reader_CSV(body_loc, self.fields_required_body, 'car-body')
		self.body = self.reader_body.load()
		
		self.materials = Materials(self.materials_file)
		self.surfaces = Surfaces(self.surfaces_file)
		
		# loop through the 6 defineable walls
		for i in range(1, 7):
			# create a panda mask that selects the current wall
			mask = self.body.wall == i

			# find out of how many parts the wall consists
			n_parts = self.body[mask].part.max()
			wall = Wall(self.options, i, n_parts)
			
			# calculate orientation of the walls
			if i == 1:
				wall.alpha = self.general.alpha
				wall.beta = self.general.beta
			elif i == 2:
				wall.alpha = self.general.alpha
				wall.beta = (self.general.beta+90.0)%360
			elif i == 3:
				wall.alpha = (self.general.alpha+90.0)%360
				wall.beta = self.general.beta
			elif i == 4:
				wall.alpha = (self.general.alpha-90.0)%360
				wall.beta = self.general.beta
			elif i == 5:
				wall.alpha = self.general.alpha
				wall.beta = (self.general.beta-90.0)%360
			elif i == 6:
				wall.alpha = (self.general.alpha-180.0)%360
				wall.beta = self.general.beta
			
			a_eff_check = 0
			for n_p in range(0, n_parts):
				# create a panda mask that selects the current part of a given wall
				mask_part = mask & (self.body.part == (n_p+1))
				
				n_layers=len(self.body[mask_part])
				a_eff = self.body[mask_part].a_eff.values[0]

				area_wall = None
				if i == 1 or i == 6:
					area_wall = self.general.w * self.general.h
				elif i == 2 or i == 5:
					area_wall = self.general.l * self.general.w
				elif i == 3 or i == 4:
					area_wall = self.general.l * self.general.h
				area_part = area_wall * a_eff
				a_eff_check = a_eff_check + a_eff

				for j in range(0, n_layers):
					material_name = self.body[mask_part].material.values[j]
					surface_name = self.body[mask_part].surface.values[j]
					
					if material_name not in self.materials.ds.name.values:
						print(" fatal error: unknown material in vehicle-configuration file!")
						print(" it is not specified in the dataset of available materials.")
						print(" material: {:s}".format(material_name))
						sys.exit(1)
				
					material_ds = self.materials.ds[self.materials.ds.name == material_name]
					surface_ds = self.surfaces.ds[self.surfaces.ds.name == surface_name]
					
					# it's possibe that no surface properties are specified - in case of layers
					# that do neither face the environment nor the interior
					if len(surface_ds) == 0:
						surface_ds = None
					
					layer = Layer(self.options, j+1, material_ds, surface_ds, self.body[mask_part].th.values[j], area_part)
					
					if j == 0:
						layer.outer=True
						
					if j == n_layers - 1:
						layer.inner=True
					
					wall.add_layer(n_p, layer)
				
			if abs(a_eff_check - 1.0) > 0.001:
				print("warning: effective area of all parts for wall {:n} does not add up to 1!".format(i))
				
			self.walls.append(wall)
					
	def initialize(self, T0):
		self.Q_tm1 = 1007.0*T0*1.16*self.v
		for wall in self.walls:
			wall.initialize(T0)
			
	def cair_temp(self):
		return self.Q_tm1/(1007.0*1.16*self.v)
		
	def output_cair(self, dtime, ts):
		if self.output_file is None:
			self.output_file = open(self.options['outpath']+'/sat_cabin_air.csv', 'w')
		out = "{:s},{:3.6f},{:3.2f}\n".format(dtime.strftime("%Y-%m-%d %H:%M:%S"), ts, self.cair_temp())
		self.output_file.write(out)
	
	def output_close(self):
		self.output_file.close()
		
	def to_string(self, print_walls=False):
		s='    name:\t\t'+self.general.code+'\n    description:\t'+self.general.description+'\n'
		s=s+'    dimensions:\t\t'+str(self.general.l)+' x '+str(self.general.w)+' x '+str(self.general.h)+'\n    oriented:\t\t'+str(self.general.alpha)+', '+str(self.general.beta)+'\n'
		if print_walls:
			for wall in self.walls:
				s=s+wall.to_string()
		return s
		

