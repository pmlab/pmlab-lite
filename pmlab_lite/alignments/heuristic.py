"""This file contains the abstract and multiple inherited heuristic classes."""
from . import constants as c, variables as v
from abc import ABC, abstractmethod
import numpy as np
from ortools.linear_solver import pywraplp


class AbstractHeuristic(ABC):
    """Abstract class for heuristics for the A* algortihm."""

    def __init__(self):
        """Initialize depending on the heuristic."""
        pass

    @abstractmethod
    def heuristic_to_final(self, node):
        """Compute estimated cost to the final marking."""
        pass


class RemainingTraceLength(AbstractHeuristic):
    """Heurisitc based on the size of the remaining trace to align."""

    def __init__(self):
        """Do nothing."""
        pass

    def heuristic_to_final(self, node) -> float:
        """
        Compute estimated cost to the final marking.

        The default version returns the length of the remaining trace as the
        cost estimate, i.e. a cost of 1 for each move to align in the re-
        maining trace. In general the heursitic assumes for each transition in
        the trace the cheapest cost to align.

        Args:
            node (Node): node, that holds a current marking, to compute the
            cost estimate to the final marking from

        Returns:
            float: estimated cost to the final marking
        """
        return len(node.remaining_trace) * c.EPSILON
        # cost = 0
        # for act in node.remaining_trace:
        #     transition = (act, act)
        #     cost += v.cost_func(transition)
        # return cost


class ILP(AbstractHeuristic):
    """Heurisitc based on solving the marking equation."""

    def __init__(self):
        """Initialize solver and associated variables."""
        self.solver = pywraplp.Solver.CreateSolver('SCIP')
        self.INF = self.solver.infinity()
        self.data = {}
        self.x = {}

    def heuristic_to_final(self, node) -> float:
        """
        Compute estimated cost to the final marking, by solving the ilp.

        Args:
            node (Node): node, that holds a current marking, to compute the
            cost estimate to the final marking from

        Returns:
            float: estimated cost to the final marking
        """
        self.solver = pywraplp.Solver.CreateSolver('SCIP')
        self.data = {}
        self.x = {}
        C = v.incidence_matrix
        b = np.array(v.final_mark_vector) - np.array(node.marking_vector)
        cost_vec = self.cost_vector()

        self.data = self.create_ilp_model(C, b, cost_vec)
        self.x = self.init_solution()
        self.init_constraints()
        self.init_objective()
        estimated_cost_to_final = self.solve()

        return estimated_cost_to_final

    def cost_vector(self) -> np.ndarray:
        num_total_moves = v.synchronous_product.num_transitions()
        # for each activity in the trace there is a synchronous transition
        num_async_moves = num_total_moves - len(v.trace)
        cost_vector = np.append(np.ones(num_async_moves), np.zeros(
            len(v.trace)))  # cost 1 for async moves / 0 for sync moves

        # make tau transitions in cost_vec cost zero
        tau_idx = [-idx
                   - 1 for idx in v.synchronous_product.transitions['tau_model']]
        cost_vector[tau_idx] = 0.0

        return cost_vector

    def create_ilp_model(self, C: np.ndarray, b: np.ndarray, cost_vec: np.ndarray) -> dict:
        """Creates and returns a dictionary that stores the data for the problem."""
        self.data['constraint_coeffs'] = C.tolist()   # the incidence matrix defines the constraint equations of the system
        # b = mf-m defines the bounds for the constraint equations
        self.data['bounds'] = b.tolist()
        # standard cost function: cost of 1 for asynchronous move, 0 for synchronous moves, 1..d asynchronous moves, d+1..N synchronous moves
        self.data['obj_coeffs'] = cost_vec.tolist()
        # = num columns = num transitions
        self.data['num_vars'] = C.shape[1]
        self.data['num_constraints'] = C.shape[0]     # = num rows = num places
        return self.data

    def init_solution(self):
        """ Initializes the solution variable vector, i.e. each x_i can take values from 0 to inf."""
        for j in range(self.data['num_vars']):
            # set range of solution x[j] from 0 to inf
            self.x[j] = self.solver.IntVar(0, self.INF, 'x[%i]' % j)

        return self.x

    def init_constraints(self):
        """Initialize the constraints for the ilp, as described in the data object."""
        for i in range(self.data['num_constraints']):
            # set equality bounds, by lower bound = upper bound
            constraint = self.solver.RowConstraint(
                self.data['bounds'][i], self.data['bounds'][i], '')
            for j in range(self.data['num_vars']):
                constraint.SetCoefficient(
                    self.x[j], self.data['constraint_coeffs'][i][j])

    def init_objective(self):
        """Initialize the objective coefficients and make minimization problem.
        """
        objective = self.solver.Objective()
        for j in range(self.data['num_vars']):
            objective.SetCoefficient(self.x[j], self.data['obj_coeffs'][j])
            objective.SetMinimization()

    def solve(self):
        """Solve the integer linear program."""
        status = self.solver.Solve()
        if status == pywraplp.Solver.OPTIMAL:
            #for j in range(self.data['num_vars']):
            #    print(self.x[j].name(), ' = ', self.x[j].solution_value())
            return self.solver.Objective().Value()
        else:
            print('The problem does not have an optimal solution.')
