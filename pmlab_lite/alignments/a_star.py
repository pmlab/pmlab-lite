from pmlab_lite.pn import PetriNet
from . alignment import Alignment
from . node import Node
from . heuristic import Heuristic
from . import constants as c
from . import variables as v
import numpy as np
import heapq



class A_Star(Alignment):

	def __init__(self, synchronous_product, trace, heuristic: str='lp', alignments: int=1):
		Alignment.__init__(self)

		self.heuristic = Heuristic(heuristic)
		self.incidence_matrix     = v.incidence_matrix     = synchronous_product.incidence_matrix()
		self.transitions_by_index = v.transitions_by_index = synchronous_product.transitions_by_index()
		self.final_mark_vector    = v.final_mark_vector    = synchronous_product.get_final_marking()

		init_node = Node(synchronous_product.get_init_marking(), None, 0)
		init_node.remaining_trace = trace
		init_node.find_active_transitions(self.incidence_matrix)
		init_node.update_costs(self.heuristic)

		self.closed_list = []																	#initialise closed set
		self.open_list = [ (init_node.total_cost, init_node) ]									#initialise open set
		heapq.heapify(self.open_list)


	def search(self):
		while len(self.open_list) > 0:
			heapq.heapify(self.open_list)
			current_node = heapq.heappop(self.open_list)[1]
			self.closed_list.append(current_node)

			if ( np.array_equal(current_node.marking_vector, self.final_mark_vector)):
				self.alignments.append(current_node)
				break
			else:
				self.__investigate(current_node)


		self.calc_results()
		#return self.alignments

	def calc_results(self):
		self._fitness()
		self._alignment_moves()
		self._model_moves()
		self._log_moves()

	#this funtion calls other functions to investigate the current node
	def __investigate(self, node):
		'''
		:param incidence_matrix: matrix of the synchronous product
		:param transitions by index: reverse of the dict 'net.transitions', to access transitions names by index
		'''

		#heuristic evaluation of active transitions
		for i in node.active_transitions:
			#make child node and update it's marking, i.e. the current marking after transition i was fired
			child_node = Node(self.incidence_matrix[:, i] + node.marking_vector, node, node.number+1)
			child_node.find_active_transitions(self.incidence_matrix)

			# --Synchronous move--
			if self.transitions_by_index[i].endswith("synchronous"):

				#update it's remaining trace
				child_node.remaining_trace = node.remaining_trace[1:]
				child_node.alignment = node.alignment + [ (self.transitions_by_index[i][:-12], self.transitions_by_index[i][:-12] ) ]

			# --Model       move--
			elif self.transitions_by_index[i].endswith("model"):

				#update it's remaining trace
				child_node.remaining_trace = node.remaining_trace[:]
				child_node.alignment = node.alignment + [ ( self.transitions_by_index[i][:-6], c.BLANK ) ]

			# --Log         move--
			elif self.transitions_by_index[i].endswith("log"):

				#update it's remaining trace
				child_node.remaining_trace = node.remaining_trace[1:]
				child_node.alignment = node.alignment + [ (c.BLANK, self.transitions_by_index[i][:-4] ) ]

			#update the child nodes costs
			child_node.update_costs(self.heuristic)

			#check whether it's in the closed list or it's a cheaper version of same marking
			self.__add_node(child_node)

	#deciding on whether or not to add a node to the open list
	def __add_node(self,node):

		#checking whether it is in the closed list
		ind = [k for k in range( len(self.closed_list) ) if np.array_equal(node.marking_vector, self.closed_list[k].marking_vector) ] #ind is a list like [12,34,10]
		if len(ind) > 0:
			pass

		#checking whether it is in the open list, update if we found it
		else:
			ind = [k for k in range(len(self.open_list)) if np.array_equal(node.marking_vector, self.open_list[k][1].marking_vector)]

			#at least once in open list
			if ind:
				for k in ind:
					if self.open_list[k][1].cost_from_start > node.cost_from_start:
						self.open_list[k] = [node.total_cost, node]
					else:
						continue
			#not in open list yet
			else:
				self.open_list.append([node.total_cost, node])
