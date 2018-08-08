from graphviz import Digraph

from pmlab_lite.graph import Graph
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

	# draw transition
	dot.attr('node', shape='box', penwidth="1", fontsize="10",
			 fontname="Helvetica")

	for t in input_net.transitions:
		dot.node(t)

	# draw place
	dot.attr('node', shape='circle', style="filled",
			 color='lightgrey', penwidth="1", fontsize="10",
			 fontname="Helvetica")

	for p in input_net.places:
		dot.node(str(p[0]))

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