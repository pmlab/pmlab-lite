from graphviz import Digraph

from pmlab_lite.helper.graph import Graph
from pmlab_lite.pn import AbstractPetriNet


def draw_petri_net(input_net:AbstractPetriNet, filename="petri_net",
				 format="pdf"):
	"""
	This function transforms the given Petri net structure
	into DOT notation and returns it as a digraph object. Call
	the render() function to save it to file.

	Args:
		filename: string name of the file
		format: export format

	Retruns:
		Digraph object
	"""

	dot = Digraph(name=filename, format=format)
	dot.attr(rankdir='LR', fontsize="10", nodesep="0.35",
			 ranksep="0.25 equally")

	# draw transitions
	dot.attr('node', shape='box', penwidth="1", fontsize="10",
			 fontname="Helvetica")

	for key, values in input_net.transitions.items():
		if key != 'tau':
			for t in values:
				dot.node(str(t), key)

	if 'tau' in input_net.transitions.keys():
		# draw tau transistions
		dot.attr('node', shape='square', style="filled",
				 color='black', penwidth="1", fontsize="5",
				 fontname="Helvetica")

		for t in input_net.transitions['tau']:
			dot.node(str(t))

	# draw place
	dot.attr('node', shape='circle', style="filled",
			 color='lightgrey', penwidth="1", fontsize="10",
			 fontname="Helvetica")

	for p in list(input_net.places.values()):
		dot.node(str(p))

	# draw edges
	for e in input_net.edges:
		dot.edge(str(e[0]), str(e[1]))

	# dot.render()
	return dot

def draw_graph(graph: Graph, filename="graph", format="pdf"):
	dot = Digraph(name=filename, format=format)

	dot.attr(rankdir='LR', fontsize="10", nodesep="0.35",
			 ranksep="0.25 equally")

	# draw nodes
	dot.attr('node', penwidth="1", fontsize="10",
			 fontname="Helvetica")

	for node in graph.graph:
		dot.node(str(node))

	# draw edges
	for node in graph.graph:
		for target in graph.graph[node]:
			dot.edge(str(node), str(target))

	return dot