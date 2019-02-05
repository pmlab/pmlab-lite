from graphviz import Digraph

from pmlab_lite.helper.graph import Graph
from pmlab_lite.pn import AbstractPetriNet


def draw_petri_net(input_net: AbstractPetriNet, filename="petri_net",
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
	dot.attr('node', shape='circle', penwidth="1", fontsize="10",
			 fontname="Helvetica")

	# draw marking
	for id, p in input_net.places.items():
		label = get_marking(input_net.marking[id])
		dot.node(str(p), label=label, xlabel=str(p))

	# draw edges
	for e in input_net.edges:
		dot.edge(str(e[0]), str(e[1]))

	# dot.render()
	return dot


def draw_graph(graph: Graph, filename="graph", format="pdf", render=False,
			   view=True):
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

	if render:
		render_dot(dot, filename, view)

	return dot

def render_dot(dot: Digraph, name: str, cleanup=True, view=True):
	dot.render(filename = name, view = view, cleanup = cleanup)