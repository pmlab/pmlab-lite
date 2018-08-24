from random import randint
from .abstract_pn import AbstractPetriNet
import pprint


class PetriNet(AbstractPetriNet):
	""" Class to represent a Petri Net."""

	def add_place(self, name, capacity=1):
		"""
		Add a place to the net and set its token capacity. The name
		has to be numeric.

		Args:
			name: integer place name
			capacity: integer number of token per place

		Raises:
			ValueError: place identifier has to be unique
			TypeError: place identifier has to be numeric
		"""
		if isinstance(name, int):
			if not self.place_exists(name):
				self.places.append((name, capacity))
			else:
				raise ValueError('place identifier has to be unique')
		else:
			raise TypeError('place identifier has to be numeric')

		return self

	def remove_place(self, name):
		"""
		Remove a place from the netself.

		Args:
			name: integer place name
		"""
		for idx, place in enumerate(self.places):
			if place[0] == name:
				self.remove_all_edges_of(name)
				del self.places[idx]
				break

		return self

	def add_transition(self, name):
		"""
		Add a transition to the net. The name has to be a string.

		Args:
			name: string name of transition

		Raises:
			ValueError: place identifier has to be unique
			TypeError: place identifier has to be a string
		"""
		if isinstance(name, str):
			if not self.transition_exists(name):
				self.transitions.append(name)
			else:
				raise ValueError('transition identifier has to be unique')
		else:
			raise TypeError('transition identifier has to be a string')

		return self

	def remove_transition(self, name):
		"""
		Remove the given transition from the net.

		Args:
			name: string of the transition
		"""
		for idx, transition in enumerate(self.transitions):
			if transition == name:
				self.remove_all_edges_of(name)
				del self.transitions[idx]
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
		if isinstance(source, int):
			# source is place
			if not self.place_exists(source):
				raise ValueError('place does not exist')
		else:
			# source is transition
			if not self.transition_exists(source):
				raise ValueError('transition does not exist')

		if isinstance(target, int):
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
				# input place has no token
				if not place[0] in self.marking:
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
		if self.place_exists(place):
			self.marking[place] = token
		else:
			raise ValueError('place does not exist.')

		return self

	def replay(self):
		"""Randomly replay the net starting from its current marking.

		Returns:
			Sequence of transitions which were fired.
		"""
		seq = []
		enabled_transitions = self.all_enabled_transitions()
		while(len(enabled_transitions) > 0):
			t = enabled_transitions[randint(0, len(enabled_transitions) - 1)]
			seq.append(t)
			self.fire_transition(t)
			enabled_transitions = self.all_enabled_transitions()

		return seq

	def transition_exists(self, name):
		"""
		Check whether the transition exists in the net or not.

		Args:
			name: string name of transition

		Returns:
			True if transition exists in petri net, False otherwise.
		"""
		return name in self.transitions

	def place_exists(self, name):
		"""
		Check whether the place exists in the net or not.

		Args:
			name: int name of place

		Returns:
			True if place exists in petri net, False otherwise.
		"""
		if len(list(filter(lambda x: x[0] == name, self.places))) > 0:
			return True
		else:
			return False

	def all_enabled_transitions(self):
		"""
		Find all transitions in the net which are enabled.

		Retruns:
			List of all enabled transitions.
		"""
		return list(filter(lambda x: self.is_enabled(x),
						   self.transitions))

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
			if i in self.marking:
				self.marking[i] -= 1

				if self.marking[i] == 0:
					self.marking.pop(i)

		# update outgoing token
		for o in outputs:
			if o in self.marking:
				self.marking[o] += 1
			else:
				self.marking[o] = 1


	# def from_ts_file(self):
	# 	"""Create a petri net from a transition system."""
	# 	pass
	#
	# def to_ts_file(self):
	# 	"""Convert the petri net into a transition system."""
	# 	pass

	def __repr__(self):
		desc = "Transitions: %s \n" \
			   "Places: %s \n" \
			   "Edges: %s" %(self.transitions, self.places, self.edges)

		return desc
