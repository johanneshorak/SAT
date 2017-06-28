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
	
	materials_file="./data/materials.csv"
	surfaces_file="./data/surfaces.csv"
	
	# the variables required in the forcing data
	fields_required_body = [
		'wall', 
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
	
	def __init__(self, options,  general_loc, body_loc):
		self.options = options
		
		self.reader = Reader_CSV(general_loc, self.fields_required_general, 'car-general')
		general = self.reader.load()
		
		self.general = Bunch()
		for c in general:
			self.general[c] = general[c].values[0]
		
		self.reader_body = Reader_CSV(body_loc, self.fields_required_body, 'car-body')
		self.body = self.reader_body.load()
		
		self.materials = Materials(self.materials_file)
		self.surfaces = Surfaces(self.surfaces_file)
		
		# loop through the 6 defineable walls
		for i in range(1, 7):
			wall = Wall(self.options, i)
			mask = self.body.wall==i
			
			area = None
			if i == 1 or i == 6:
				area = self.general.w * self.general.h
			elif i == 2 or i == 5:
				area = self.general.l * self.general.w
			elif i == 3 or i == 4:
				area = self.general.l * self.general.h

			for j in range(0, len(self.body[mask])):
				material_name = self.body[mask].material.values[j]
				material_ds = self.materials.ds[self.materials.ds.material == material_name]
				layer = Layer(self.options, j+1, material_ds, self.body[mask].th.values[j], area)
				wall.add_layer(layer)
			self.walls.append(wall)
			
		print self.to_string()
		
	def initialize(self, T0):
		for wall in self.walls:
			wall.initialize(T0)
		
	def to_string(self):
		s='name:\t\t'+self.general.code+'\ndescription:\t'+self.general.description+'\n'
		s=s+'dimensions:\t'+str(self.general.l)+' x '+str(self.general.w)+' x '+str(self.general.h)+'\noriented:\t'+str(self.general.alpha)+', '+str(self.general.beta)+'\n'
		for wall in self.walls:
			s=s+wall.to_string()
		return s
		

