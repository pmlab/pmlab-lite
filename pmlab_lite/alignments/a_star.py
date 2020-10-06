from pmlab_lite.pn import PetriNet
from .alignment import Alignment
from . import variables as v
import numpy as np
import heapq

BLANK = '>>' 
EPSILON = 0.00001


def store_variables(incidence_matrix, init_mark_vector, final_mark_vector, transitions_by_index):
	v.incidence_matrix = incidence_matrix
	v.init_mark_vector = init_mark_vector
	v.final_mark_vector = final_mark_vector
	v.transitions_by_index = transitions_by_index
	v.solutions = []


class A_star(Alignment):
	
	def __init__(self):
		Alignment.__init__(self)
		self.solutions = []
		
	#a star algorithm
	def A_star_exe(self, petri_net, trace, heuristic_variant="lp", no_of_solutions=1):
		v.open_list = open_list = []
		v.closed_list = closed_list = []

		heuristic = Heuristic(heuristic_variant)
		incidence_matrix = petri_net.incidence_matrix()
		transitions_by_index = petri_net.transitions_by_index()
		init_mark_vector = petri_net.get_init_marking() 
		final_mark_vector = petri_net.get_final_marking()
			
		store_variables(incidence_matrix, init_mark_vector, final_mark_vector, transitions_by_index)
			
		#creating the initial node in the search space
		current_node = Node()
		current_node.Make_initial_node(trace, heuristic)
		open_list.append( [current_node.total_cost, current_node] )
		
		#number for drawing the search space in order
		count = 0
		#iterating until open_list has no elements
		while len(open_list) > 0:
			# build min heap from open list
			heapq.heapify(open_list)					

			current_node = heapq.heappop(v.open_list)	#pop cheapest node from open list as (total cost, node)
			closed_list.append(current_node)		#append it to closed list as (total cost, node)
			current_node = current_node[1]			#make the current node just the node of the tuple
			current_node.number = count
			
			#checking whether the node is a solution. else: investigate
			if( np.array_equal( current_node.marking_vector, final_mark_vector) ):
				self.solutions.append(current_node)
				v.solutions.append(self.alignment_move)
					
				if len(self.solutions) >= no_of_solutions:
					break
			else:
				current_node.Investigate(incidence_matrix, transitions_by_index, heuristic)
				count += 1
		
		self.closed_list_end = closed_list
		self.__Fitness()
		self.__Move_alignment()
		self.__Move_in_model()
		self.__Move_in_log()
		return v.solutions
	
	def __Fitness(self):
		for sol in self.solutions:
			u = sol.alignment_up_to
			self.fitness.append( round ( len( [e for e in u if ((e[0]!=BLANK and e[1]!=BLANK) or ('tau' in e[0])) ]) / len(u), 3) )
		
	def __Move_alignment(self):
		for sol in self.solutions:
			u = sol.alignment_up_to
			self.alignment_move.append( [e for e in u if ('tau' not in e[0])] )
		
	def __Move_in_model(self):
		for sol in self.solutions:
			u = sol.alignment_up_to
			self.move_in_model.append( [e[0] for e in u if (e[0]!=BLANK and ('tau' not in e[0]))] )  
		
	def __Move_in_log(self):
		for sol in self.solutions:
			u = sol.alignment_up_to
			self.move_in_log.append( [e[1] for e in u if e[1] != BLANK])								


class Node():	
	def __init__(self):
		#shows a marking node
		self.number = 0
		self.marking_vector = []
		self.active_transitions = []
		self.parent_node = ''
		self.observed_trace_remain = []
		self.alignment_up_to = []			#it's of the form [ (t1,t1), (t2,-), (-,t3), ... ]
		
		self.cost_from_init_marking = 1 * sum( [EPSILON if ((x[0]!=BLANK and x[1]!=BLANK) or ('tau' in x[0])) else 1 for x in self.alignment_up_to] )
		self.cost_to_final_marking = 1000
		self.total_cost = self.cost_from_init_marking + self.cost_to_final_marking
	
	#method for comparing two objects (python 3.7)
	def __lt__(self, other):
		return self.total_cost < other.total_cost
		
	#this funtion calls other functions to investigate the current node
	def Investigate(self, incidence_matrix, transitions_by_index, heuristic):
		'''
		:param incidence_matrix: matrix of the synchronous product
		:param transitions by index: reverse of the dict 'net.transitions', to access transitions names by index
		'''

		self.Find_active_transitions(incidence_matrix)

		#heuristic evaluation of active transitions
		for i in self.active_transitions:
			#make child node and update it's marking, i.e. the current marking after transition i was fired
			child_node = Node()
			child_node.marking_vector = incidence_matrix[:, i] + self.marking_vector
			child_node.parent_node = self

			# --Synchronous move--
			if transitions_by_index[i].endswith("synchronous"):
				
				#update it's remaining trace
				child_node.observed_trace_remain = self.observed_trace_remain[1:]
				child_node.alignment_up_to = self.alignment_up_to + [ (transitions_by_index[i][:-12], transitions_by_index[i][:-12] ) ]
				
			# --Model       move--
			elif transitions_by_index[i].endswith("model"):
				
				#update it's remaining trace
				child_node.observed_trace_remain = self.observed_trace_remain[:]
				child_node.alignment_up_to = self.alignment_up_to + [ ( transitions_by_index[i][:-6], BLANK ) ]
					
			# --Log         move--
			elif transitions_by_index[i].endswith("log"):

				#update it's remaining trace
				child_node.observed_trace_remain = self.observed_trace_remain[1:]
				child_node.alignment_up_to = self.alignment_up_to + [ (BLANK, transitions_by_index[i][:-4] ) ]

			#update the child nodes costs
			child_node.Update_costs(heuristic)
	
			#check whether it's in the closed list or it's a cheaper version of same marking
			child_node.Add_node(v.open_list, v.closed_list)
			
	def Find_active_transitions(self, incidence_matrix):
		#looping over transitions of the synchronous product, to see which are active, given the marking of that node
		for i in range(0, incidence_matrix.shape[1]):											#im.shape[1] returns #columns = #transitions
			
			if np.all( (incidence_matrix[:, i] + self.marking_vector) >= 0 ):				#im[:,i] returns i-th column as list
				#transition i is active
				if i not in self.active_transitions:
					self.active_transitions.append(i)
					
	#deciding on whether or not to add a node to the open list
	def Add_node(self, open_list, closed_list):
		#checking whether it is in the closed list
		#ind is a list like [12,34,10]
		ind = [k for k in range( len(closed_list) ) if np.array_equal(self.marking_vector, closed_list[k][1].marking_vector) ]
		
		if len(ind) > 0:
			pass
		#checking whether it is in the open list, update if we found it
		else:
			ind = [k for k in range(len(open_list)) if np.array_equal(self.marking_vector, open_list[k][1].marking_vector)]
			
			#at least once in open list
			if ind:
				for k in ind:
					if open_list[k][1].cost_from_init_marking > self.cost_from_init_marking:	
						open_list[k] = [self.total_cost, self]
					else: 
						continue
			#not in open list yet
			else:
				open_list.append( [self.total_cost, self] )

	def Cost_from_init(self):
		#base_cost = 1 + EPSILON
		#add base cost into initial cost calculation
		self.cost_from_init_marking = 1 * sum( [EPSILON if ((x[0]!=BLANK and x[1]!=BLANK) or ('tau' in x[0])) else 1 for x in self.alignment_up_to] )

	#calcucalte the remaining cost to the final marking,based on a heuristic
	def Cost_to_final(self, heuristic):
		heuristic.heuristic_to_final(self)

	def Update_costs(self, heuristic):
		self.Cost_from_init()
		self.Cost_to_final(heuristic)	
		self.total_cost = self.cost_from_init_marking + self.cost_to_final_marking
		
	def Make_initial_node(self, trace, heuristic):
		self.marking_vector = v.init_mark_vector
		self.observed_trace_remain = trace    
		self.Cost_to_final(heuristic)
		return self


class Heuristic():

	def __init__(self, variant):
		self.variant = variant

	def heuristic_to_final(self, node):
		if self.variant == "tl":
			self.remaining_trace_length_heursitic(node)
		elif self.variant == "lp":
			self.linear_programming_heursitic(node)
	
	def remaining_trace_length_heursitic(self, node):
		node.cost_to_final_marking = len(node.observed_trace_remain) * EPSILON

	def linear_programming_heursitic(self, node):
		#Heuristic.heurisitic_to_final()
		b = np.array(v.final_mark_vector) - np.array(node.marking_vector) 
		x = np.linalg.lstsq(v.incidence_matrix, b, rcond=None)[0]
		
		# important note: with rcond=None, the the results in costs calculated my vary on different machines
		# on three machines tested the unrounded sum of each x was mostly equal, differences occured in +-10 digits after comma
		# after rounding up or down though, differences where bigger on each machine (e.g. machine1 rounds -0.000001 to 0
		# 			and machine2 rounds 0.00000001 to 1 -> making the sums differ in multiples of 1
		#with rcond=-1 the same results have been calculated on each machine
		
		#rounding up or down, 
		x[x > 0] = 1
		x[x <= 0] = 0
		
		for key in v.transitions_by_index:
			if v.transitions_by_index[key].startswith('tau'):
				x[key] = 0
		
		node.cost_to_final_marking = np.sum(x)
