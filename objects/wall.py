class Wall:
	
	options = None
	id = None
	layers = None
	area = None
	
	def __init__(self,options,  id):
		self.options = None
		self.id = id
		
	def add_layer(self, layer):
		if self.layers is None:
			self.layers = []
			
		self.layers.append(layer)
		
	def to_string(self):
		s=""
		s="\nW"+str(self.id)
		for layer in self.layers:
			s=s+"\n"+layer.to_string()
		return s
		
	def initialize(self, T0):
		for layer in self.layers:
			layer.initialize(T0)
