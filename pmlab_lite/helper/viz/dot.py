from graphviz import Digraph

from pmlab_lite.discovery.cut import Cut
from pmlab_lite.discovery.process_tree import ProcessTree
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
	dot.attr('node', shape='circle', penwidth='1', fontsize='10',
			 fontname='Helvetica', style='unfilled')

	# draw marking
	for id, p in input_net.places.items():
		label = get_marking(input_net.marking[id])
		dot.node(str(p), label=label, xlabel=str(p))

	# draw edges
	for e in input_net.edges:
		dot.edge(str(e[0]), str(e[1]))

	render_dot(dot, 'petri_net')  # TODO: change to just return the object
	return dot


def draw_graph(graph: Graph, filename="graph", format="pdf", render=False,
			   view=True):
	dot = Digraph(name=filename, format=format)

	dot.attr(rankdir='LR', fontsize="10", nodesep="0.35",
			 ranksep="0.25 equally")

	# draw nodes
	dot.attr('node', penwidth="1", fontsize="10",
			 fontname="Helvetica")

	for node in graph.vertexes:
		dot.node(str(node))

	# draw edges
	for node in graph.vertexes:
		for target in graph.vertexes[node]:
			dot.edge(str(node), str(target))

	if render:
		render_dot(dot, filename, view)

	return dot

def draw_process_tree(tree: ProcessTree, name='process_tree', format='png',
					  render=True):
	"""
	This function transforms the given process tree
	into DOT notation renders it and returns it as a digraph object.

	:param tree: process tree object
	:param name: file name
	:param format: file format

	:return: Digraph object
	"""

	def gen_label(cut: int):
		"""
		Return node symbol, depending on cut type
		:param cut: cut code

		:return str: symbol
		"""

		if cut == Cut.SEQ:
			return '&#10140;'
		elif cut == Cut.PARA:
			return '&#43;'
		elif cut == Cut.EXCL:
			return '&#215;'
		elif cut == Cut.LOOP:
			return '&#x21BB;'

	def draw_children(parent: str, child, dot: Digraph):

		def draw_node(sub_tree, dot: Digraph):
			dot.attr('node', shape='circle', penwidth="1", fontsize="10",
					 fontname="Helvetica", height="0.3", fixedsize="false")

			node_name = ''.join([str(sub_tree.parent), str(sub_tree.id)])
			dot.node(node_name, label=gen_label(sub_tree.cut))

			for child in sub_tree.children:
				draw_children(node_name, child, dot)

		def draw_leaf(parent, leaf, dot: Digraph):
			dot.attr('node', shape='box', color='black', penwidth="1",
					 fontsize="10",
					 fontname="Helvetica", height="0.5", fixedsize="false")

			leaf_name = ''.join([parent, str(leaf)])
			if leaf == 'tau':
				dot.node(leaf_name, label=str(leaf), shape="square",
						 style='filled')
			else:
				dot.node(leaf_name, label=str(leaf))

		if isinstance(child, ProcessTree):
			draw_node(child, dot)
			child_name = ''.join([str(child.parent), str(child.id)])
		else:
			draw_leaf(parent, child, dot)
			child_name = ''.join([parent, child])

		# draw edge
		dot.edge(parent, child_name)
		return dot

	# general settings
	dot = Digraph(name, format=format)
	dot.attr(rankdir="TB", ranksep="equally")

	# draw root
	dot.attr('node', shape='circle', penwidth="1", fontsize="10",
			 fontname="Helvetica", height="0.3", fixedsize="true")

	node_name = ''.join(['root', str(tree.id)])
	dot.node(node_name, label=gen_label(tree.cut))

	for child in tree.children:
		dot = draw_children(node_name, child, dot)

	if render:
		render_dot(dot, name)

	return dot


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