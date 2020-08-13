from . pn import PetriNet



class TraceNet(PetriNet):
	""" 
	Class to represent a synchronous prodcut.
	For creation the constructor needs to get passed a trace.
	"""

	def __init__(self, trace: list):
		self.places = {}
		self.transitions = {}
		self.edges = []
		self.marking = []
		self.capacity = []
		self.counter = 0  # mapping
		self.make_trace_net(trace)

	def make_trace_net(self, trace: list):
		"""
		Takes a trace, as a list of strings(=events) and makes a traces net from it, 
		i.e. a sequential connection of the events as places with transitions in between.
		"""
		#assume empty PetriNet
		num_places = len(trace)+1

		for i in range(1, num_places+1):
			self.add_place(i)

		for t in trace:
			self.add_transition(t)
 
		for i in range(1, num_places):
			self.add_edge(i, -i)
			self.add_edge(-i, i+1)

		return self