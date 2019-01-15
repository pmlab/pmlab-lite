from random import randint
from .abstract_pn import AbstractPetriNet
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

	def get_mapping(self):
		return self.transitions

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

	def add_edge(self, source, target, two_way=False):
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

	def is_enabled(self, transition):
		"""
		Check whether a transition is able to fire or not.

		Args:
			transition: string name of transition

		Retruns:
			True if transition is enabled, False otherwise.
		"""

		# all palces which are predecessor of the given transition
		input_places = list(filter(lambda x: x[1] == transition, self.edges))
		# do any inputs exist?
		if len(input_places) > 0:
			# check if each place contains at least one token aka. has a
			# marking
			for place in input_places:
				idx = self.index_of_place(place[0])
				# input place has no token
				if self.marking[idx] == 0:
					return False
			# transition is able to fire
			return True
		else:
			# no input places
			return False

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
		inputs = [item[0] for item in
				  list(filter(lambda x: x[1] == transition,
							  self.edges))]

		outputs = [item[1] for item in
				   list(filter(lambda x: x[0] == transition,
							   self.edges))]

		# update ingoing token
		for i in inputs:
			idx = self.index_of_place(i)
			self.marking[idx] -= 1

		# update outgoing token
		for o in outputs:
			idx = self.index_of_place(o)
			self.marking[idx] += 1

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
