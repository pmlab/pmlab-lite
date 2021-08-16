"""This file is used to test changes, new functions, dependencies etc."""
from pprint import pprint
from pmlab_lite.pn import PetriNet, TraceNet, SynchronousProduct
from pmlab_lite.helper.io import pnml
from pmlab_lite.alignments.a_star import A_Star
from pmlab_lite.helper.viz import dot
import numpy as np

import graphviz as gr
from graphviz import Digraph


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

def get_marking(marking: int):
	"""viz import
	Create label for a place with its corresponding number of tokens.

	:param marking: number of token
	:return: label
	"""

	if marking < 4:
		token = '&#11044;'
		if marking == 0:
			return ''
		elif marking == 1:
			return '<<B>%s</B>>' % token
		elif marking == 2:
			return '<<B>%s %s</B>>' % (token, token)
		else:
			return '<<B>%s<BR/>%s %s</B>>' % (token, token, token)
	else:
		return '4'

def render_dot(dot: Digraph, name: str, cleanup=True, view=True):
	"""
	Render the given DOT object to file. After rendering, the image can be
	shown and artifacts can be removed.

	:param dot: DOT object
	:param name: file name
	:param cleanup: remove dot artifacts after rendering
	:param view: open file after rendering
	"""

	dot.render(filename=name, view=view, cleanup=cleanup)

def draw_alignment_path(input_net: SynchronousProduct, alignment, filename="synchronous_product_net", format="pdf"):
	color = ["black", "chartreuse3", "yellow1"]
	transitions_by_index = input_net.transitions_by_index()

	dot = gr.Digraph(name=filename, format=format)
	dot.attr(rankdir='LR', fontsize="10", nodesep="0.35", ranksep="0.25 equally" )

	#draw places
	for id, p in input_net.places.items():
		label = get_marking(input_net.marking[id])
		if id >= input_net.get_index_init_places()[1]:  # the second index is the trace net input place, and all indexes up from there relate to places from the trace net
			dot.node(str(p), label=label, xlabel=str(p), shape="circle", group='trace')
		else:
			dot.node(str(p), label=label, xlabel=str(p), shape="circle")

	#draw transitions
	for i in range(0,len(transitions_by_index)):
		if transitions_by_index[i].endswith("_model"):
			dot.node( str(-(i+1)), "(" + transitions_by_index[i].rsplit('_', 1)[0] + "," + BLANK + ")",shape="rect", style='unfilled', color=color[0])
		elif transitions_by_index[i].endswith("_log"):
			dot.node( str(-(i+1)), "(" + BLANK + "," + transitions_by_index[i].rsplit('_', 1)[0] + ")", shape="rect", style='filled', group='trace')
		elif transitions_by_index[i].endswith("_synchronous"):
			dot.node( str(-(i+1)), "(" + transitions_by_index[i].rsplit('_', 1)[0] + "," + transitions_by_index[i][:-12] + ")", shape="rect", style='filled', fillcolor=color[1])


	#draw edges
	for e in input_net.edges:
	#the edge is coming from a transition
		if e[0] < 0:
			if transitions_by_index[-(e[0]+1)].endswith("_synchronous"):
				dot.edge( str(e[0]), str(e[1]), color=color[1] )
			else:
				dot.edge( str(e[0]), str(e[1]) )
	#the edge is going to a transition
		else:
			if transitions_by_index[-(e[1]+1)].endswith("_synchronous"):
				 dot.edge( str(e[0]), str(e[1]), color=color[1] )
			else:
				dot.edge( str(e[0]), str(e[1]) )

	#f = open("./sync_product.dot", "w")
	#f.write(dot.source)

	render_dot(dot, filename)  # TODO: change to just return the object
	return dot


running_example = PetriNet()
pnml.load(running_example, '../conf_tutorial/running_example.pnml')

#trace = ['As', 'Aa', 'Sso', 'Ro', 'Ao', 'Aaa', 'Aaa']
#trace = ['As', 'Aa', 'Ao', 'Aaa', 'Af']
trace = ['As', 'Aa', 'Fa', 'Do', 'Da', 'Af']
trace_net = TraceNet(trace)

sp = SynchronousProduct(running_example, trace_net)

print(sp.places)
print(sp.get_index_init_places())
print()
print(sp.transitions_as_tuples)

#draw_alignment_path(sp, "sp_net")


ilp_searcher1 = A_Star(sp, trace, heuristic='ilp', n_alignments=1)
ilp_searcher1.search()

print('Optimal Alignments found using the ilp heuristic:')
ilp_searcher1.print_alignments()
print()
print(ilp_searcher1.fitness)
print(ilp_searcher1.alignment_moves[0])
print(ilp_searcher1.model_moves)
print(ilp_searcher1.log_moves)

# for i in range(len(ilp_searcher1.alignments)):
#     print('Alignment 1 cost: ', round(ilp_searcher1.alignments[i].total_cost, 2))
# print()

# print()
# print(len(ilp_searcher1.alignments))


# trace = ['As', 'Aa', 'Fa', 'Do', 'Da', 'Af']

# assign a cost of 0.2 (instead of 1) to Aa and Fa
# compute optimal alignments with these updated costs
