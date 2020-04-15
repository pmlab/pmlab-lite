from random import randint
from .abstract_pn import AbstractPetriNet
import numpy
import pprint


class PetriNet(AbstractPetriNet):
	""" Class to represent a Petri Net."""

	def add_place(self, name, capacity=1):
		"""
		Add a place to the net and set its token capacity. The name
		has to be numeric. Further, the keys are indices of the corresponding
		marking vector and capacity vector.

		Args:
			name: integer place name
			capacity: integer number of token per place

		Raises:
			ValueError: place identifier has to be unique
			TypeError: place identifier has to be numeric
		"""
		if isinstance(name, int) and name > 0:
			if not self.place_exists(name):
				idx = len(self.places)
				self.places[idx] = name
				self.marking.append(0)
				self.capacity.append(capacity)
			else:
				raise ValueError('place identifier has to be unique')
		else:
			raise TypeError('place identifier has to be numeric and > 0')

		return self

	def remove_place(self, name):
		"""
		Remove a place from the net.

		Args:
			name: integer place name
		"""
		index = 0

		for idx, place in self.places.items():
			if place == name:
				index = idx
				break

		# shift places with larger index to the left
		if index + 1 == len(self.places):  # last index
			self.places.pop(index)
		else:
			for idx in range(index, len(self.places) - 1):
				self.places[idx] = self.places[idx + 1]

			self.places.pop(len(self.places) - 1)

		del self.marking[index]
		del self.capacity[index]

		return self

	def num_places(self):
		return len( self.places.keys() )

	def get_mapping(self):
		return self.transitions

	def get_marking(self):
		return self.marking

	def add_transition(self, name, id=None):
		"""
		Add a transition to the net. The name has to be a string.

		Args:
			name: string name of transition

		Raises:
			ValueError: place identifier has to be unique
			TypeError: place identifier has to be a string
		"""

		self.counter -= 1

		if len(name) == 0:
			name = 'tau'

		if id is None:
			id = self.counter
		else:
			if id >= 0:
				raise ValueError('transition identifier has to be < 0')

		if name in self.transitions.keys():
			self.transitions[name].append(id)
		else:
			self.transitions[name] = [id]

		return self

	def remove_transition(self, name):
		"""
		Remove the given transition from the net.

		Args:
			name: string of the transition
		"""

		for key, values in self.transitions.items():
			if name in values:
				values.remove(name)
				if len(values) == 0:
					self.transitions.pop(key, None)
				break

		return self
		
	def num_transitions(self):
		return sum( [len(v) for v in self.transitions.values()] )

	def add_edge(self, source, target, two_way=False):
		#could also get one touple as an argument...
		"""
		Add a new edge between two elements in the net. If two way argument
		is True, one edge per direction will be added.

		Args:
			source: name of transition/place
			target: name of transition/place
			two_way: add edge from target to source

		Raises:
			ValueError: source/target does not exists
		"""
		if source > 0 and target > 0 or source < 0 and target < 0:
			raise ValueError('edges can only be added between places and '
							 'transition and vice versa')

		if source > 0:
			# source is place
			if not self.place_exists(source):
				raise ValueError('place does not exist')
		else:
			# source is transition
			if not self.transition_exists(source):
				raise ValueError('transition does not exist')

		if target > 0:
			# target is place
			if not self.place_exists(target):
				raise ValueError('place does not exist')
		else:
			# target is transition
			if not self.transition_exists(target):
				raise ValueError('transition does not exist')

		if not two_way:
			self.edges.append((source, target))
		else:
			self.edges.append((source, target))
			self.edges.append((target, source))

		return self

	def remove_edge(self, source, target):
		"""Remove edge.

		Args:
			source: name of transition/place
			target: name of transition/place
		"""
		for idx, edge in enumerate(self.edges):
			if edge[0] == source and edge[1] == target:
				del self.edges[idx]
				break

		return self

	def remove_all_edges_of(self, name):
		"""
		Remove all edge where the given element is either the source or
		the target.

		Args:
			name: name of place/transition
		"""
		# where element is source
		for e in list(filter(lambda x: x[0] == name, self.edges)):
			del self.edges[self.edges.index(e)]

		# where element is target
		for e in list(filter(lambda x: x[1] == name, self.edges)):
			del self.edges[self.edges.index(e)]

		return self

	def index_of_place(self, place):
		for idx, p in self.places.items():
			if p == place:
				return idx

	def transitions_by_index(self):
		transitions_by_index = dict()

		for key, value in self.transitions.items():
				for val in value:
					transitions_by_index[-(val+1)] = key

		return transitions_by_index

	def is_enabled(self, transition):
		"""
		Check whether a transition is able to fire or not.

		Args:
			transition: value (negative number) of transition

		Retruns:
			True if transition is enabled, False otherwise.
			Special case: returning true, when a transition has no input places
		"""

		# all palces which are predecessor of the given transition
		inputs = self.get_inputs(transition)
		# do any inputs exist?
		if len(inputs) > 0:
			# check if each place contains at least one token aka. has a
			# marking
			for i in inputs:
				idx = self.index_of_place(i)
				# input place has no token
				if self.marking[idx] == 0:
					return False
			# transition is able to fire
			return True
		else:
			# no input places
			return True

	def get_inputs(self, node):
		"""
		args: node, positive number for place, negative number for transition

		returns: list of numbers, positives when node is a transition and negatives when node is a place
		"""
		inputs = []
		for edge in self.edges:
			if edge[1] == node:
				inputs.append(edge[0])
		return inputs

	def get_outputs(self, node):
		"""
		args: node, positive number for place, negative number for transition

		returns: list of numbers, positives when node is a transition and negatives when node is a place
		"""
		outputs = []
		for edge in self.edges:
			if edge[0] == node:
				outputs.append(edge[1])
		return outputs

	def add_marking(self, place, token=1):
		"""
		Add a new marking to the net.

		Args:
			place: int name of place
			token: int number of token to add

		Raises:
			ValueError: place does not exists
		"""
		index = None
		if self.place_exists(place):
			for idx, p in self.places.items():
				if p == place:
					index = idx
					break

			self.marking[index] = token
		else:
			raise ValueError('place does not exist.')

		return self

	def null_marking(self):
		for i in range(0, len(self.marking)):
			self.marking[i] = 0

	def replay(self, max_length):
		"""Randomly replay the net starting from its current marking.

		Returns:
			Sequence of transitions which were fired.
		"""
		seq = []
		enabled_transitions = self.all_enabled_transitions()
		while (len(enabled_transitions) > 0 and len(seq) < max_length):
			t = enabled_transitions[randint(0, len(enabled_transitions) - 1)]
			seq.append(t)
			self.fire_transition(t)
			enabled_transitions = self.all_enabled_transitions()

		if len(seq) == max_length:
			seq.append('BREAK')

		return seq

	def transition_exists(self, name):
		"""
		Check whether the transition exists in the net or not.

		Args:
			name: string name of transition

		Returns:
			True if transition exists in petri net, False otherwise.
		"""

		# flatten list
		transition_mapping = [item for sublist in self.transitions.values() for
							  item
							  in sublist]
		return name in transition_mapping

	def place_exists(self, name):
		"""
		Check whether the place exists in the net or not.

		Args:
			name: int name of place

		Returns:
			True if place exists in petri net, False otherwise.
		"""

		return name in list(self.places.values())

	def all_enabled_transitions(self):
		"""
		Find all transitions in the net which are enabled.

		Retruns:
			List of all enabled transitions.
		"""
		transitions = [item for sublist in self.transitions.values() for item
					   in sublist]

		return list(filter(lambda x: self.is_enabled(x), transitions))

	def fire_transition(self, transition):
		"""
		Fire transition.

		Args:
			name: string name of transition
		"""
		if self.is_enabled(transition):
			inputs = self.get_inputs(transition)

			outputs = self.get_outputs(transition)

			# update ingoing token
			for i in inputs:
				idx = self.index_of_place(i)
				self.marking[idx] -= 1

			# update outgoing token
			for o in outputs:
				idx = self.index_of_place(o)
				self.marking[idx] += 1
		else:
			print("Transition is not enabled!")

	def __repr__(self):
		"""
		Change class representation.

		:return: string
		"""
		desc = "Transitions: %s \n" \
			   "Places: %s \n" \
			   "Capacities: %s \n" \
			   "Marking: %s \n" \
			   "Edges: %s" % (self.transitions, self.places, self.capacity,
							  self.marking, self.edges)

		return desc

	def get_index_initial_places(self):
		index_places_start = []
		for key in self.places.keys():
			if len(self.get_inputs(self.places[key])) == 0:
				index_places_start.append(key)
		return index_places_start

	def get_index_final_places(self):
		index_places_end = []
		for key in self.places.keys():
			if len(self.get_outputs(self.places[key])) == 0:
				index_places_end.append(key)
		return index_places_end
	
	def get_spnets_initial_marking(self):
		#only works for nets with 2 start places so far (assuming sp-nets)
		index_start_places = self.get_index_initial_places()
		index_place_start = index_start_places[0]
		index_place_start_log = index_start_places[1]
		init_mark_vector = list (numpy.repeat(0, len(self.places)))
		init_mark_vector[index_place_start] = 1
		init_mark_vector[index_place_start_log] = 1
		return init_mark_vector
	
	def get_spnets_final_marking(self):
		#only works for nets with 2 end places so far (assuming sp-nets)
		index_final_places = self.get_index_final_places() 
		index_place_end = index_final_places[0]
		index_place_end_log = index_final_places[1]	
		final_mark_vector = list (numpy.repeat(0, len(self.places)))
		final_mark_vector[index_place_end] = 1
		final_mark_vector[index_place_end_log] = 1
		return final_mark_vector

	def incidence_matrix(self):
		# Creating an empty matrix							  	
		incidence_matrix = numpy.zeros( ( self.num_places(), self.num_transitions() ), dtype=int)
        
		transitions_by_index = self.transitions_by_index()

		for t in transitions_by_index:
			for key in self.places.keys():
				t_val = -(t+1)					#reverse the index, to be the transtions value again
				col_index = t
				row_index = key
				p = self.places[key]
				#edge goes from P to T and vice versaa
				if ( (t_val, p) in self. edges) and ( (p, t_val) in self. edges): 
					incidence_matrix[row_index][col_index] = 0
				#edge goes from T to P
				elif (t_val, p) in self.edges:
					incidence_matrix[row_index][col_index] = 1
				#edge goes from P to T
				elif (p, t_val) in self.edges:
					incidence_matrix[row_index][col_index] = -1

		return incidence_matrix

	#TODO clunky -> more easy sync transitions with transitions_by_index()
	def synchronous_product(self, trace_net):
		#self is model_net
		sp_net = PetriNet()
		place_offset = len(self.places.values())
		transition_offset = len(self.transitions_by_index())

		#PLACES
		#copying the model net
		for p in self.places.values():
			sp_net.add_place(p)

		#copying the trace net
		for p in trace_net.places.values():
			sp_net.add_place(p + place_offset)
			

		#TRANSITIONS
		#copying the modelnet
		model_transitions_by_index = self.transitions_by_index()
		for i in range(0, len(model_transitions_by_index)):
			sp_net.add_transition(model_transitions_by_index[i] + "_model")
		
		#copying the trace net
		trace_transitions_by_index = trace_net.transitions_by_index()
		for i in range(0, len(trace_transitions_by_index)):
			sp_net.add_transition(trace_transitions_by_index[i] + "_log")


		#EDGES	
		#copying the model net
		for edge in self.edges:
			sp_net.add_edge(edge[0], edge[1])
			
		# copying the trace net
		for edge in trace_net.edges:
			new_edge = (0,0)
			if edge[0] > 0:
				new_edge = (edge[0]+place_offset, edge[1] - transition_offset)
			elif edge[0] < 0:
				new_edge = (edge[0] - transition_offset, edge[1]+place_offset)
			sp_net.add_edge(new_edge[0], new_edge[1])
		
		
		#CREATE NEW SYNCHRONOUS PRODUCT TRANSITIONS AND EDGES
		#whenever trace_t has the same name as model_t we create a new sync_t with all the in/outputs from the model_ and trace_t combined
		for keyT1 in trace_net.transitions.keys():
			for keyT2 in self.transitions.keys():
				if keyT1 == keyT2:
					for i in range(0, len(trace_net.transitions[keyT1])):
						keyT3 = keyT1 + "_synchronous"
						sp_net.add_transition(keyT3)
						#copy all the in/outputs from the trace net transitions onto the new sync prod transitions
						#inputs
						for node in trace_net.get_inputs(trace_net.transitions[keyT1][i]):
							sp_net.add_edge(node+place_offset, sp_net.transitions[keyT3][i] )
						#outputs
						for node in trace_net.get_outputs(trace_net.transitions[keyT1][i]):
							sp_net.add_edge(sp_net.transitions[keyT3][i], node+place_offset)
						
						#copy all the in/outputs from the model transitions onto the new sync prod transitions
						#inputs
						for node in self.get_inputs(self.transitions[keyT2][0]):
							sp_net.add_edge(node, sp_net.transitions[keyT3][i] )
						#outpus
						for node in self.get_outputs(self.transitions[keyT2][0]):
							sp_net.add_edge(sp_net.transitions[keyT3][i], node)
		
		return sp_net

### make trace net an own class, derived form abstract pn?
	def make_trace_net(self, trace):
		#assume empty PetriNet
		num_places = len(trace)+1

		for i in range(1, num_places+1):
			self.add_place(i)

		for t in trace:
			self.add_transition(t)
 
		for i in range(1, num_places):
			self.add_edge(i, -i)
			self.add_edge(-i, i+1)
