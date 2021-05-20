from . import constants as c
from . import variables as v
import numpy as np
from ortools.linear_solver import pywraplp


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
        solver = pywraplp.Solver.CreateSolver('SCIP')
        INF = solver.infinity()

        def cost_vector() -> np.ndarray:
            num_total_moves = v.synchronous_product.num_transitions()
            num_async_moves = num_total_moves - len(v.trace)  # for each activity in the trace there is a synchronous transition
            cost_vector = np.append(np.ones(num_async_moves), np.zeros(len(v.trace)))  # cost 1 for async moves / 0 for sync moves

            # make tau transitions in cost_vec cost zero
            tau_idx = [-idx - 1 for idx in v.synchronous_product.transitions['tau_model']]
            cost_vector[tau_idx] = 0.0

            return cost_vector

        def create_ilp_model(C: np.ndarray, b: np.ndarray, cost_vec: np.ndarray) -> dict:
            """Creates and returns a dictionary that stores the data for the problem."""
            data = {}
            data['constraint_coeffs'] = C.tolist()   # the incidence matrix defines the constraint equations of the system
            data['bounds'] = b.tolist()              # b = mf-m defines the bounds for the constraint equations
            data['obj_coeffs'] = cost_vec.tolist()   # standard cost function: cost of 1 for asynchronous move, 0 for synchronous moves, 1..d asynchronous moves, d+1..N synchronous moves
            data['num_vars'] = C.shape[1]            # = num columns = num transitions
            data['num_constraints'] = C.shape[0]     # = num rows = num places
            return data

        def init_solution():
            """ Initializes the solution variable vector, i.e. each x_i can take values from 0 to inf."""
            x = {}
            for j in range(data['num_vars']):
                x[j] = solver.IntVar(0, INF, 'x[%i]' % j)  # set range of solution x[j] from 0 to inf

            return x

        def init_constraints():
            """ Initializes the constraints for the ilp, as describe in the data object."""
            for i in range(data['num_constraints']):
                constraint = solver.RowConstraint(data['bounds'][i], data['bounds'][i], '')  # set equality bounds, by lower bound = upper bound
                for j in range(data['num_vars']):
                    constraint.SetCoefficient(x[j], data['constraint_coeffs'][i][j])

        def init_objective():
            """ Initializes the objectives coefficients () and set as minimization problem."""
            objective = solver.Objective()
            for j in range(data['num_vars']):
                objective.SetCoefficient(x[j], data['obj_coeffs'][j])
                objective.SetMinimization()

        def solve():
            status = solver.Solve()
            if status == pywraplp.Solver.OPTIMAL:
                return solver.Objective().Value()
            else:
                print('The problem does not have an optimal solution.')

        C = v.incidence_matrix
        b = np.array(v.final_mark_vector) - np.array(node.marking_vector)
        cost_vec = cost_vector()

        data = create_ilp_model(C, b, cost_vec)
        x = init_solution()
        init_constraints()
        init_objective()
        estimated_cost_to_final = solve()

        return estimated_cost_to_final
