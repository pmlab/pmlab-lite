"""The A* class."""
from . alignment import Alignment
from . node import Node
from . heuristic import RemainingTraceLength, ILP
from . import constants as c, variables as v
import numpy as np
import heapq


class A_Star(Alignment):
    """Represents an Alignment for which the A*-algortihm can be used."""

    def __init__(self, synchronous_product, trace, heuristic: str = 'ilp',
                 n_alignments: int = 1, cost_func=None):
        """
        Initialize the alignment and it's characteristics.

        Heurstic = 'ilp' for integer linear programming and = 'rtl' for remain-
        ing trace length heursitic. Necessary class variables are defined and
        computed, such as the incidence matrix, the open and closed list and
        intial node.

        Args:
            synchronous_product (SynchronousProduct): The synchronous product,
            that shall be the perfect transition order be found for.

            trace (list): contains the sequence of activities

            heuristic (str): specifies the heuristic to use

            n_alignments (int): specifies for how many optimal alignments to
            searched for
        """
        Alignment.__init__(self)
        self.n_alignments = n_alignments
        v.synchronous_product = synchronous_product
        v.trace = trace

        self.incidence_matrix = v.incidence_matrix = synchronous_product.incidence_matrix()
        self.transitions_by_index = v.transitions_by_index = synchronous_product.transitions_by_index()
        self.final_mark_vector = v.final_mark_vector = synchronous_product.get_final_marking()

        if cost_func:
            v.cost_func = cost_func
        else:
            v.cost_func = c.default_cost_func

        if heuristic == 'ilp':
            self.heuristic = ILP()
        elif heuristic == 'rtl':
            self.heuristic = RemainingTraceLength()

        init_node = Node(synchronous_product.get_init_marking(), None, 0)
        init_node.remaining_trace = trace
        init_node.find_active_transitions(self.incidence_matrix)
        init_node.update_costs(self.heuristic)

        self.closed_list = []
        self.open_list = [(init_node.total_cost, init_node)]
        heapq.heapify(self.open_list)

    def search(self):
        """Find an optimal alignment using the A*-algorithm."""
        while len(self.open_list) > 0:
            heapq.heapify(self.open_list)
            current_node = heapq.heappop(self.open_list)[1]
            self.closed_list.append(current_node)

            if (np.array_equal(current_node.marking_vector,
                               self.final_mark_vector)):
                self.alignments.append(current_node)

                if len(self.alignments) == self.n_alignments:
                    break

            self.__investigate(current_node)

        self.__calc_results()
        # return self.alignments

    def __calc_results(self):
        self._fitness()
        self._alignment_moves()
        self._model_moves()
        self._log_moves()

    def __investigate(self, node):
        # this funtion calls other functions to investigate the current node
        # heuristic evaluation of active transitions
        for i in node.active_transitions:
            # make child node and update it's marking,
            # i.e. the current marking after transition i was fired
            child_node = Node(
                self.incidence_matrix[:, i] + node.marking_vector, node, node.number+1)
            child_node.fired_transitions = node.fired_transitions + [-(i+1)]
            child_node.find_active_transitions(self.incidence_matrix)

            # --Synchronous move--
            if self.transitions_by_index[i].endswith("synchronous"):

                # update it's remaining trace
                child_node.remaining_trace = node.remaining_trace[1:]
                child_node.alignment = node.alignment + \
                    [(self.transitions_by_index[i].rsplit('_', 1)[0],
                      self.transitions_by_index[i].rsplit('_', 1)[0])]

            # --Model       move--
            elif self.transitions_by_index[i].endswith("model"):

                # update it's remaining trace
                child_node.remaining_trace = node.remaining_trace[:]
                child_node.alignment = node.alignment + \
                    [(self.transitions_by_index[i].rsplit('_', 1)[0], c.BLANK)]

            # --Log         move--
            elif self.transitions_by_index[i].endswith("log"):

                # update it's remaining trace
                child_node.remaining_trace = node.remaining_trace[1:]
                child_node.alignment = node.alignment + \
                    [(c.BLANK, self.transitions_by_index[i].rsplit('_', 1)[0])]

            # update the child nodes costs
            child_node.update_costs(self.heuristic)

            # check if it's in the closed list or
            # if it's a cheaper version of same marking
            self.__add_node(child_node)

    def __add_node(self, node):
        # deciding on whether or not to add a node to the open list
        # checking whether it is in the closed list
        # ind is a list like [12,34,10]
        
        idx = [k for k in range(len(self.closed_list)) if node == self.closed_list[k]]
        if len(idx) > 0:
            pass

        # checking whether it is in the open list, update if we found it
        else:
            idx = [k for k in range(len(self.open_list)) if node == self.open_list[k][1]]

            # at least once in open list
            if idx:
                for k in idx:
                    if (self.open_list[k][1].cost_from_start > node.cost_from_start):
                        self.open_list[k] = [node.total_cost, node]
                    else:
                        continue
            # not in open list yet
            else:
                self.open_list.append([node.total_cost, node])
