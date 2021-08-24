"""The Node class."""
from . import variables as v
import numpy as np


class Node():
    """Represents a node in the A*-algorithm search space."""

    def __init__(self, marking_vector, predecessor, number):
        """
        Initialize the node and it's characteristics.

        The characteristics of the nodes are set. The alignment is a list
        containing the transitions aligned so far, of the form: [(t1,t1),
        (t2,>>), ...].

        Args:
            marking_vector (np.ndarray): vector describing the current marking
                                         of the synchronous product
            predecessor (Node): the predeceding node / marking
            number (int): the number at which this node / marking has been in-
                          vestigated
        """
        self.marking_vector = marking_vector
        self.predecessor = predecessor
        self.cost_from_start = 0
        self.cost_to_end = 100000
        self.total_cost = self.cost_from_start + self.cost_to_end
        self.alignment = []
        self.remaining_trace = []
        self.active_transitions = []
        self.fired_transitions = []  # sequence of transitions fired to reach this nodes marking
        self.number = number

    def __lt__(self, other_node):
        """Compare the total cost of this and another node."""
        return self.total_cost < other_node.total_cost

    def __eq__(self, other_node):
        """Check if marking and fired transitions of two nodes are equal."""
        return (np.array_equal(self.marking_vector, other_node.marking_vector)) and (self.fired_transitions == other_node.fired_transitions)

    def find_active_transitions(self, incidence_matrix):
        """
        Add all activated transitions to the set of activated transitions.

        Given the nodes marking and the incidence matrix of the synchronous
        product net, all activated transitions are found and added to the
        nodes list of active transitions.

        Args:
            incidence_matrix (np.ndarray): matrix for the synchronous product
        """
        # looping over all transitions of the synchronous product,
        # to see which are active, given the marking of that node
        # im.shape[1] returns #columns = #transitions
        for i in range(0, incidence_matrix.shape[1]):

            if np.all((incidence_matrix[:, i] + self.marking_vector) >= 0):
                # im[:,i] returns i-th column as list
                # transition i is active
                if i not in self.active_transitions:
                    self.active_transitions.append(i)

    def starting_cost(self):
        """Compute the cost of the alignment so far for the node."""
        # self.cost_from_start = 1 * sum([c.EPSILON if
        # ((x[0] != c.BLANK and x[1] != c.BLANK) or ('tau' in x[0]))
        # else 1 for x in self.alignment] )
        self.cost_from_start = sum([v.cost_func(t) for t in self.alignment])

    def ending_cost(self, heuristic):
        """
        Estimate the cost to the final marking for the node, using a heuristic.

        Args:
            heuristic (Heuristic): the heuristic to estimate the final cost
        """
        self.cost_to_end = heuristic.heuristic_to_final(self)

    def update_costs(self, heuristic):
        """
        Calculate the new costs for a node in the search space.

        Calls starting_cost() and ending_cost() to update the cost so far, the
        estimated cost to final respectively for the given node. Then computes
        the nodes total_cost as the sum of the two costs.

        Args:
            heuristic (Heuristic): the heuristic to estimate the final cost
        """
        self.starting_cost()
        self.ending_cost(heuristic)
        self.total_cost = self.cost_from_start + self.cost_to_end

    def get_predecessor(self):
        """Return the beforegoing node."""
        return self.predecessor
