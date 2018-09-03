"""
This package provides a class to build simple graph data structures,
like direct follower graphs
"""
from collections import defaultdict

# from pmlab.pn import PetriNet


class Graph:

	def __init__(self):
		self.graph = defaultdict(list)

	def __str__(self):
		return str(self.graph.items())

	def add_edge(self, o, t):
		"""
		Add edge to graph.

		:param o: origin
		:param t: target
		"""
		if t not in self.graph[o]:
			self.graph[o].append(t)
			self.graph[t]

		return self

	def remove_edge(self, o, t):
		"""

		:param o: origin
		:param t: target
		:return:
		"""
		if t in self.graph[o]:
			self.graph[o].remove(t)

		return self

	def from_seq(self, seq):
		for idx, i in enumerate(seq[:-1]):
			self.add_edge(i, seq[idx + 1])

	def from_petrinet(self, pn):
		l1 = list(filter(lambda x: not isinstance(x[0], int), pn.edges))
		for l in l1:
			for e in pn.edges:
				if l[1] == e[0]:
					self.add_edge(l[0], e[1])