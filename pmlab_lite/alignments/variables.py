"""Variables that multiple *.py-files in this module need access to."""
from typing import Callable

open_list = []
closed_list = []
solutions = []

# Storing the specification of SP net
incidence_matrix = []
init_mark_vector = []
final_mark_vector = []
transitions_by_index = dict()

# variables for the ilp heuristic_to_final
synchronous_product = None
trace = None

# cost function related variables
cost_func = Callable 
