class Wall:
	
	options = None
	id = None
	parts = None
	layers = None
	area = None
	
	dbg_file = None
	
	alpha = None
	beta = None
	
	def __init__(self,options,  id,  n_parts):
		self.options = None
		self.id = id
		
		self.parts=[]
		for i in range(0, n_parts):
			self.parts.append(None)
			
	def add_layer(self, part, layer):
		if self.parts[part] is None:
			self.parts[part] = []
			
		self.parts[part].append(layer)
		#print "appended to ", part,  " ", len(self.parts[part])
		
	def to_string(self):
		s=""
		for np,  part in enumerate(self.parts):
			s=s+"\n    W{:2n} P{:2n}".format(self.id, np+1)
			s=s+" ({:2.1f}, {:2.1f})".format(self.alpha, self.beta)
			for layer in part:
				s=s+"\n"+layer.to_string()
		return s
		
	# this function outputs the layer temperatures and additional information, such as heat fluxes
	# to a file. If a wall consists of multiple parts each part is saved to a separate file.
	def debug_to_file(self, dtime, fluxes):
		
		if self.dbg_file is None:
			self.dbg_file = []
			for np, part in enumerate(self.parts):
				header = "time,"					# generate file header for output csv
				for nl, layer in enumerate(part):
					for sl, slayer in enumerate(layer.sublayers_Q_t):
						header = header+"l{:n}sl{:n},".format(nl+1, sl+1)
						
				header = header + "R_S_env,R_L_env,K_env,R_S_int,R_L_int,K_int,\n"
				
				self.dbg_file.append(open('./dbg/wall-'+str(self.id).zfill(2)+'-'+str(np+1).zfill(2)+'.csv', 'w'))
				self.dbg_file[-1].write(header)
				
		for np, part in enumerate(self.parts):
			out = "{:s},".format(dtime.strftime("%Y-%m-%d %H:%M:%S"))
			for nl, layer in enumerate(part):
				for sl, slayer in enumerate(layer.sublayers_Q_t):
					out = out + "{:2.2f},".format(layer.sl_temp(sl))
			out = out + "{:3.2f},".format(fluxes["R_S_env"])
			out = out + "{:3.2f},".format(fluxes["R_L_env"])
			out = out + "{:3.2f},".format(fluxes["K_env"])
			out = out + "{:3.2f},".format(fluxes["R_S_int"])
			out = out + "{:3.2f},".format(fluxes["R_L_int"])
			out = out + "{:3.2f},".format(fluxes["K_int"])
			out = out + "\n"
			self.dbg_file[np].write(out)
	
	def debug_file_close(self):
		if self.dbg_file is not None:
			for file in self.dbg_file:
				file.close()
		
	def initialize(self, T0):
		for part in self.parts:
			#print part
			for layer in part:
				layer.initialize(T0)
