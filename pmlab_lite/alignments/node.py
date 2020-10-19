from . import constants as c
from . import variables as v
import numpy as np


class Node():	
	#shows a marking node

	def __init__(self, marking_vector, predecessor, number):
		self.marking_vector = marking_vector	
		self.predecessor = predecessor
		self.cost_from_start = 0
		self.cost_to_end = 100000
		self.total_cost = self.cost_from_start + self.cost_to_end

		self.alignment = []			#it's of the form [ (t1,t1), (t2,>>), (>>,t3), ... ]
		self.remaining_trace = []
		self.active_transitions = [] 

		self.number = number

	#method for comparing two objects (python 3.7)
	def __lt__(self, other):
		return self.total_cost < other.total_cost
			
	def find_active_transitions(self, incidence_matrix):
		#looping over transitions of the synchronous product, to see which are active, given the marking of that node
		for i in range(0, incidence_matrix.shape[1]):										#im.shape[1] returns #columns = #transitions
			
			if np.all( (incidence_matrix[:, i] + self.marking_vector) >= 0 ):				#im[:,i] returns i-th column as list
				#transition i is active
				if i not in self.active_transitions:
					self.active_transitions.append(i)
	
	def starting_cost(self):
		self.cost_from_start = 1 * sum( [c.EPSILON if ((x[0]!=c.BLANK and x[1]!=c.BLANK) or ('tau' in x[0])) else 1 for x in self.alignment] )

	#calcucalte the remaining cost to the final marking,based on a heuristic
	def ending_cost(self, heuristic):
		self.cost_to_end = heuristic.heuristic_to_final(self)

	def update_costs(self, heuristic):
		self.starting_cost()
		self.ending_cost(heuristic)	
		self.total_cost = self.cost_from_start + self.cost_to_end

	def get_predecessor(self):
		return self.predecessor