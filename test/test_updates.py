"""This file is used to test changes, new functions, dependencies etc."""
from pprint import pprint
from pmlab_lite.pn import PetriNet, TraceNet, SynchronousProduct
from pmlab_lite.helper.io import pnml
from pmlab_lite.alignments.a_star import A_Star
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

#trace = ['As', 'Aa', 'Sso', 'Ro', 'Ao', 'Aaa', 'Aaa']
#trace = ['As', 'Aa', 'Ao', 'Aaa', 'Af']
trace = ['As', 'Aa', 'Fa', 'Do', 'Da', 'Af']
trace_net = TraceNet(trace)

sp = SynchronousProduct(running_example, trace_net)

# print(sp.transitions)
# ts = sp.transitions_by_index()
# print(ts)
# print()
# cost_vec = np.zeros(sp.num_transitions())
# print(cost_vec)
# for i in range(len(cost_vec)):
#     t = ts[i]
#     if t.endswith("synchronous"):
#         a = (t.rsplit('_', 1)[0], t.rsplit('_', 1)[0])
#         print(a, " is a synchronous move: ",  _synchronous_move(a))
#         cost_vec[i] = test_cost_func(a)
#     elif t.endswith("model"):
#         a = (t.rsplit('_', 1)[0], '>>')
#         print(a, " is a model move: ",  _model_move(a))
#         cost_vec[i] = test_cost_func(a)
#     elif t.endswith("log"):
#         a = ('>>', t.rsplit('_', 1)[0])
#         print(a, " is a log move: ",  _log_move(a))
#         cost_vec[i] = test_cost_func(a)

# print()
# print(cost_vec)

ilp_searcher1 = A_Star(sp, trace, heuristic='ilp', n_alignments=1)
ilp_searcher1.search()

print('Optimal Alignments found using the ilp heuristic:')
ilp_searcher1.print_alignments()

# for i in range(len(ilp_searcher1.alignments)):
#     print('Alignment 1 cost: ', round(ilp_searcher1.alignments[i].total_cost, 2))
# print()

# print()
# print(len(ilp_searcher1.alignments))


# trace = ['As', 'Aa', 'Fa', 'Do', 'Da', 'Af']

# assign a cost of 0.2 (instead of 1) to Aa and Fa
# compute optimal alignments with these updated costs
