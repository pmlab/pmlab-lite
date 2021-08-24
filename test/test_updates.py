"""This file is used to test changes, new functions, dependencies etc."""
from pprint import pprint
from pmlab_lite.pn import PetriNet, TraceNet, SynchronousProduct
from pmlab_lite.helper.io import pnml
from pmlab_lite.alignments.a_star import A_Star
from pmlab_lite.helper.viz import dot
import numpy as np


BLANK = '>>'
EPSILON = 0.01

def _synchronous_move(transition: tuple) -> bool:
    return (transition[0] == transition[1]) or ('tau' in transition[0])  # (xx, xx) is a synchronous move

def _model_move(transition: tuple) -> bool:
    return transition[1] == BLANK  # (xx, >>) is a model move

def _log_move(transition: tuple) -> bool:
    return transition[0] == BLANK  # (>>, yy) is a log move

def test_cost_func(transition: tuple) -> float:
    if transition == ('Aa', '>>') or transition == ('Fa', '>>'):
        return 0.2 + EPSILON  # cheaper cost for Aa and Fa
    elif _synchronous_move(transition):
        return EPSILON
    elif _model_move(transition) or _log_move(transition):
        return 1.0 + EPSILON


running_example = PetriNet()
pnml.load(running_example, '../conf_tutorial/running_example.pnml')

trace = ['As', 'Aa', 'Sso', 'Ro', 'Ao', 'Aaa', 'Aaa']
trace_net = TraceNet(trace)

sp = SynchronousProduct(running_example, trace_net)

ilp_searcher1 = A_Star(sp, trace, heuristic='ilp', n_alignments=3)
ilp_searcher1.search()
print('Optimal Alignments found using the ilp heuristic:')
ilp_searcher1.print_alignments()
#dot.draw_synchronous_product(sp)