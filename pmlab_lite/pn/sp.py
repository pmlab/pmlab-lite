from . pn import PetriNet
import numpy as np

class SynchronousProduct(PetriNet):
	""" 
	Class to represent a synchronous prodcut.
	For creation the constructor needs to get passed a PetriNet and a TraceNet.
	"""

	def __init__(self, petri_net, trace_net):
		self.places = {}
		self.transitions = {}
		self.edges = []
		self.marking = []
		self.capacity = []
		self.counter = 0  # mapping
		self.__synchronous_product(petri_net, trace_net)

	#TODO clunky -> more easy sync transitions with transitions_by_index()
	def __synchronous_product(self, petri_net, trace_net):
		#petri_net is model_net
		place_offset = len(petri_net.places.values())
		transition_offset = len(petri_net.transitions_by_index())

		#PLACES
		#copying the model net
		for p in petri_net.places.values():
			self.add_place(p)

		#copying the trace net
		for p in trace_net.places.values():
			self.add_place(p + place_offset)
			

		#TRANSITIONS
		#copying the modelnet
		model_transitions_by_index = petri_net.transitions_by_index()
		for i in range(0, len(model_transitions_by_index)):
			self.add_transition(model_transitions_by_index[i] + "_model")
		
		#copying the trace net
		trace_transitions_by_index = trace_net.transitions_by_index()
		for i in range(0, len(trace_transitions_by_index)):
			self.add_transition(trace_transitions_by_index[i] + "_log")


		#EDGES	
		#copying the model net
		for edge in petri_net.edges:
			self.add_edge(edge[0], edge[1])
			
		# copying the trace net
		for edge in trace_net.edges:
			new_edge = (0,0)
			if edge[0] > 0:
				new_edge = (edge[0]+place_offset, edge[1] - transition_offset)
			elif edge[0] < 0:
				new_edge = (edge[0] - transition_offset, edge[1]+place_offset)
			self.add_edge(new_edge[0], new_edge[1])
		
		
		#CREATE NEW SYNCHRONOUS PRODUCT TRANSITIONS AND EDGES
		#whenever trace_t has the same name as model_t we create a new sync_t with all the in/outputs from the model_ and trace_t combined
		for keyT1 in trace_net.transitions.keys():
			for keyT2 in petri_net.transitions.keys():
				if keyT1 == keyT2:
					for i in range(0, len(trace_net.transitions[keyT1])):
						keyT3 = keyT1 + "_synchronous"
						self.add_transition(keyT3)
						#copy all the in/outputs from the trace net transitions onto the new sync prod transitions
						#inputs
						for node in trace_net.get_inputs(trace_net.transitions[keyT1][i]):
							self.add_edge(node+place_offset, self.transitions[keyT3][i] )
						#outputs
						for node in trace_net.get_outputs(trace_net.transitions[keyT1][i]):
							self.add_edge(self.transitions[keyT3][i], node+place_offset)
						
						#copy all the in/outputs from the model transitions onto the new sync prod transitions
						#inputs
						for node in petri_net.get_inputs(petri_net.transitions[keyT2][0]):
							self.add_edge(node, self.transitions[keyT3][i] )
						#outpus
						for node in petri_net.get_outputs(petri_net.transitions[keyT2][0]):
							self.add_edge(self.transitions[keyT3][i], node)
		
		return self