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

        
        self.data['constraint_coeffs'] = v.incidence_matrix.tolist()
       
        self.cost_vec = self.cost_vector()
        self.data['obj_coeffs'] = self.cost_vec.tolist()
        
        self.data['num_vars'] = v.incidence_matrix.shape[1]
        self.data['num_constraints'] = v.incidence_matrix.shape[0]     

        #self.cost_vec = self.cost_vector()

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
        self.x = {}
        b = np.array(v.final_mark_vector) - np.array(node.marking_vector)

        self.set_bounds(b)
        self.x = self.init_solution()
        self.init_constraints()
        self.init_objective()
        estimated_cost_to_final = self.solve()

        return estimated_cost_to_final

    def cost_vector(self) -> np.ndarray:
        """Create the cost vector from the current cost function."""
        cost_vec = np.zeros(v.synchronous_product.num_transitions())
        for i in range(len(cost_vec)):
            t = v.transitions_by_index[i]
            
            if t.endswith("synchronous"):
                a = (t.rsplit('_', 1)[0], t.rsplit('_', 1)[0])
            elif t.endswith("model"):
                a = (t.rsplit('_', 1)[0], c.BLANK)
            elif t.endswith("log"):
                a = (c.BLANK, t.rsplit('_', 1)[0])
            
            cost_vec[i] = v.cost_func(a)

        return cost_vec

    def set_bounds(self, b: np.ndarray):
        """Set the bounds for the current ilp to solve, i.e. the right hand side of the marking equation."""
        self.data['bounds'] = b.tolist()
        
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
