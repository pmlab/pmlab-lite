import graphviz as gr
from graphviz import Digraph
from pmlab_lite.discovery.cut import Cut
from pmlab_lite.discovery.process_tree import ProcessTree
from pmlab_lite.helper.graph import Graph
from pmlab_lite.pn.abstract_pn import AbstractPetriNet
from pmlab_lite.pn.sp import SynchronousProduct
from pmlab_lite.alignments.node import Node
import numpy as np

BLANK = '>>'

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

def draw_petri_net(input_net: AbstractPetriNet, filename="petri_net", format='pdf'):

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
		if key != 'tau' and not key.endswith("_synchronous"): 
			for i, t in enumerate(values):  # i counts for multiple occurances of the same label, e.g. in a trace net
				if len(values)==1:
					dot.node(str(t), key)
				else:
					dot.node(str(t), key+str(i+1))

	# draw sync transitions
	dot.attr('node', shape='box', penwidth="1", fontsize="10",
			 fontname="Helvetica", color='green')

	for key, values in input_net.transitions.items():
		if key.endswith("_synchronous"):
			for t in values:
				dot.node(str(t), key)

	if 'tau' in input_net.transitions.keys():
		# draw tau transistions
		dot.attr('node', shape='square', style="filled",
				 color='black', penwidth="1", fontsize="10",
				 fontname="Helvetica", fontcolor='white')

		for t in input_net.transitions['tau']:
			dot.node(str(t), 'tau')

	# draw place
	dot.attr('node', shape='circle', penwidth='1', fontsize='10',
			 fontname='Helvetica', style='unfilled', color='black')

	# draw marking
	for id, p in input_net.places.items():
		label = get_marking(input_net.marking[id])
		dot.node(str(p), label=label, xlabel=str(p))

	# draw edges
	#TODO get colored edges for sync prod edges
	for e in input_net.edges:
		dot.edge(str(e[0]), str(e[1]))

	render_dot(dot, filename)  # TODO: change to just return the object
	return dot

def draw_synchronous_product(input_net: SynchronousProduct, filename="synchronous_product_net", format="pdf"):
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
	for key, values in input_net.transitions.items():
		for i, t in enumerate(values):  # i counts for multiple occurances of the same label, e.g. in a trace net
			label = __create_sp_label(key, values, i+1)
			
			if key.endswith("_model"):
				dot.node(str(t), label, shape="rect", style='unfilled', color=color[0])
		
			elif key.endswith("_log"):
				dot.node(str(t), label, shape="rect", style='filled', group='trace')
		
			elif key.endswith("_synchronous"):
				dot.node(str(t), label, shape="rect", style='filled', fillcolor=color[1])


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

def draw_alignment_path(input_net: SynchronousProduct, node: Node, filename="node_path", format="pdf"):
	color = ["purple", "yellow1", "chartreuse3", 'black', 'white']
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

	#draw transitions and color the ones that were used in the alignment
	for key, values in input_net.transitions.items():
		for i, t in enumerate(values):  # i counts for multiple occurances of the same label, e.g. in a trace net
			label = __create_sp_label(key, values, i+1)
			
			if key.endswith("_model"):
				if t in node.fired_transitions:
					if key.startswith('tau'):
						dot.node( str(t), label, shape="rect", style='filled', color=color[0], fillcolor=color[3], fontcolor=color[4])
					else:
						dot.node( str(t), label, shape="rect", style='filled', fillcolor=color[0])
				else:
					dot.node( str(t), label, shape="rect", style='unfilled')
		
			elif key.endswith("_log"):
				if t in node.fired_transitions:
					dot.node( str(t), label, shape="rect", style='filled', fillcolor=color[1], group='trace')
				else:
					dot.node( str(t), label, shape="rect", style='unfilled', group='trace')
		
			elif key.endswith("_synchronous"):
				if t in node.fired_transitions:
					dot.node( str(t), label, shape="rect", style='filled', fillcolor=color[2])
				else:
					dot.node( str(t), label, shape="rect", style='unfilled')

	#draw edges
	for e in input_net.edges:
	#the edge is coming from a transition
		if e[0] < 0:
			if transitions_by_index[-(e[0]+1)].endswith("_synchronous"):
				dot.edge( str(e[0]), str(e[1]), color=color[2] )
			else:
				dot.edge( str(e[0]), str(e[1]) )
	#the edge is going to a transition
		else:
			if transitions_by_index[-(e[1]+1)].endswith("_synchronous"):
				dot.edge( str(e[0]), str(e[1]), color=color[2] )
			else:
				dot.edge( str(e[0]), str(e[1]) )

	#f = open("./sync_product.dot", "w")
	#f.write(dot.source)

	render_dot(dot, filename)  # TODO: change to just return the object
	return dot

def __create_sp_label(label: str, transition_ids: list, repitions: int) -> str:
	
	if label.endswith("_model"):
		return __create_model_label_of_sp(label, transition_ids, repitions)
	
	elif label.endswith('_log'):
		return __create_log_label_of_sp(label, transition_ids, repitions)
	
	elif label.endswith('_synchronous'):
		return __create_sync_label_of_sp(label, transition_ids, repitions)

def __create_model_label_of_sp(label: str, transition_ids: list, repitions: int) -> str:
	if len(transition_ids)==1:
		return "(" + label.rsplit('_', 1)[0] + "," + BLANK + ")"
	else:
		return "(" + label.rsplit('_', 1)[0] + str(repitions) + "," + BLANK + ")"

def __create_log_label_of_sp(label: str, transition_ids: list, repitions: int) -> str:
	if len(transition_ids)==1:
		return "(" + BLANK + "," + label.rsplit('_', 1)[0] + ")"
	else:
		return "(" + BLANK + "," + label.rsplit('_', 1)[0] + str(repitions) + ")"

def __create_sync_label_of_sp(label: str, transition_ids: list, repitions: int) -> str:
	if len(transition_ids)==1:
		return "(" + label.rsplit('_', 1)[0] + "," + label.rsplit('_', 1)[0] + ")"
	else:
		return "(" + label.rsplit('_', 1)[0] + str(repitions) + "," + label.rsplit('_', 1)[0] + str(repitions) + ")"

def draw_a_star_search_space(astar, filename="search_space", format="pdf"):
    closed_list = astar.closed_list
    initial_mark_vector = closed_list[0].marking_vector
    final_mark_vector = astar.alignments[0].marking_vector
    colors = ["indianred2", "darkseagreen", "gray"]
    counter = 100

    dot = Digraph(name=filename, format=format)
    dot.attr(rankdir='LR', fontsize="3", nodesep="0.35",
			 ranksep="0.25 equally")

    #draw nodes
    dot.attr('node', shape='circle', penwidth='1', fontsize='12',
			 fontname='Helvetica', style='filled')
    fontcolor = 'black'
    changed_fontcolor = False
    for node in closed_list:
        #change color for darker nodes
        if not changed_fontcolor and counter < 30:
            changed_fontcolor = True
            fontcolor = 'white'
        #node is the final marking
        if ( np.array_equal(node.marking_vector, final_mark_vector) ):
            dot.node(str(node.marking_vector), label="H = " + str(round(float(node.cost_to_end),3)) + "\nG = " + str(round(float(node.cost_from_start),3)),
                color=colors[1])
        #node is the initial marking
        elif ( np.array_equal(node.marking_vector, initial_mark_vector) ):
            dot.node(str(node.marking_vector), label="H = " + str(round(float(node.cost_to_end),3)) + "\nG = " + str(round(float(node.cost_from_start),3)),
                color=colors[0])
        #any other node
        else:
            dot.node(str(node.marking_vector), label="H = " + str(round(float(node.cost_to_end),3)) + "\nG = " + str(round(float(node.cost_from_start),3)),
                color=colors[2]+str(counter), fontcolor=fontcolor)
        if counter > 0:
            counter -= 1

    #draw edges
    for node in closed_list:
        #very first nodes parent node is " '' "
        if node.predecessor:
            predecessor = node.predecessor
            dot.edge(str(predecessor.marking_vector), str(node.marking_vector), label=str(node.number))

    render_dot(dot,filename)
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

def draw_process_tree(tree: ProcessTree, name='process_tree', format='png', render=True):
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
