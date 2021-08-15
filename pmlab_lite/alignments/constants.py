"""Constants that multiple *.py-files in this module need access to."""
BLANK = '>>'
EPSILON = 0.000001


# constants for printing alignments
CHARS_PER_ROW = 110
ROW1 = '| log trace          |'
ROW2 = '| execution sequence |'
INDENT = '                     '


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
    if _synchronous_move(transition):
        return EPSILON
    elif _model_move(transition) or _log_move(transition):
        return 1.0 + EPSILON


def _synchronous_move(transition: tuple) -> bool:
    return (transition[0] == transition[1]) or ('tau' in transition[0])


def _model_move(transition: tuple) -> bool:
    return transition[1] == BLANK


def _log_move(transition: tuple) -> bool:
    return transition[0] == BLANK
