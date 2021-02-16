from . node import Node
from . import constants as c
from . import variables as v
import numpy as np
from scipy.linalg import lstsq

class Heuristic():

	def __init__(self, variant):
		self.variant = variant

	def heuristic_to_final(self, node):
		if self.variant == "tl":
			return self.remaining_trace_length_heursitic(node)
		elif self.variant == "lp":
			return self.linear_programming_heursitic(node)

	def remaining_trace_length_heursitic(self, node):
		return len(node.remaining_trace) * c.EPSILON

	def linear_programming_heursitic(self, node):
		#Heuristic.heurisitic_to_final()
		b = np.array(v.final_mark_vector) - np.array(node.marking_vector)
		x = np.linalg.lstsq(v.incidence_matrix, b, rcond=None)[0]
		#x2 = lstsq(v.incidence_matrix, b, cond=None)[0]
		# important note: with rcond=None, the the results in costs calculated my vary on different machines
		# on three machines tested the unrounded sum of each x was mostly equal, differences occured in +-10 digits after comma
		# after rounding up or down though, differences where bigger on each machine (e.g. machine1 rounds -0.000001 to 0
		# 			and machine2 rounds 0.00000001 to 1 -> making the sums differ in multiples of 1
		#with rcond=-1 the same results have been calculated on each machine
		#
		# also linalg.lstsq does not return the x fulfilling min c(x)

		#rounding up or down, NOTE: but not roundin makes the solution closer to "real" / integer solutions cost. But it can still be overestimating, see test_lp.py
		#x[x > 0] = 1
		#x[x <= 0] = 0

		for key in v.transitions_by_index:
			if v.transitions_by_index[key].startswith('tau') or v.transitions_by_index[key].endswith('synchronous'):
				x[key] = 0

		return np.sum(x)
