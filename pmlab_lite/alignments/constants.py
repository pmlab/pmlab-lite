"""Constants that multiple *.py-files in this module need access to."""
from . import variables as v

BLANK = '>>'
EPSILON = 0.000001


# constants for printing alignments
CHARS_PER_ROW = 110
ROW1 = '| log trace          |'
ROW2 = '| execution sequence |'
INDENT = '                     '


# cost function related constants

def default_cost_func(transition: tuple) -> float:
    """
    Return the default cost for a transition.

    A synchronous or tau move has no cost. For stability a minimum cost
    epsilon is returned. Log and model moves have a default cost of 1.

    Args:
        transition (tuple): transition (model, log) of an alignment

    Returns:
        float: the cost for that transition
    """
    if _synchronous_move(transition) or _tau_move(transition):
        return EPSILON
    elif _model_move(transition) or _log_move(transition):
        return 1.0 + EPSILON


def _alignment_based_cost(alignment: list) -> float:
    '''Compute alignment-based fitness (Conformance Checking book p. 169).'''
    # idea: Use ilp solve to maximize the cost function and determine the worst case cost.

    #optimal cost = cost(alignment) = sum([v.cost_func(move) for move in self.alignment])

    #worst_case_cost = solution_of_ilp_solver

    #return 1 - optimal_cost / worst_case_cost
    pass


def _move_model_fitness(alignment: list) -> float:
    """Compute move-model fitness (Conformance Checking book p. 170)."""
    model_move_cost = 0 
    cost_of_sync_moves_interpreted_as_model_moves = 0
    for move in alignment:
        if _model_move(move) or _tau_move(move):
            model_move_cost += v.cost_func(move)
        elif _synchronous_move(move):
            cost_of_sync_moves_interpreted_as_model_moves += v.cost_func((move[0], BLANK))  # interpret as model move

    return 1 - model_move_cost / (model_move_cost + cost_of_sync_moves_interpreted_as_model_moves)


def _move_log_fitness(alignment: list) -> float:
    """Compute move-log fitness (Conformance Checking book p. 170)."""
    log_move_cost = 0 
    cost_of_sync_moves_interpreted_as_log_moves = 0
    for move in alignment:
        if _log_move(move):
            log_move_cost += v.cost_func(move)
        elif _synchronous_move(move):
            cost_of_sync_moves_interpreted_as_log_moves += v.cost_func((BLANK, move[0]))  # interpret as log move

    return 1 - log_move_cost / (log_move_cost + cost_of_sync_moves_interpreted_as_log_moves)


def _synchronous_move(transition: tuple) -> bool:
    return (transition[0] == transition[1]) or ('tau' in transition[0])


def _model_move(transition: tuple) -> bool:
    return transition[1] == BLANK


def _tau_move(transition: tuple) -> bool:
    return ('tau' in transition[0])


def _log_move(transition: tuple) -> bool:
    return transition[0] == BLANK
