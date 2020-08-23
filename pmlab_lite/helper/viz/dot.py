import graphviz as gr
from graphviz import Digraph
from pmlab_lite.discovery.cut import Cut
from pmlab_lite.discovery.process_tree import ProcessTree
from pmlab_lite.helper.graph import Graph
from pmlab_lite.pn import AbstractPetriNet
from pmlab_lite.pn import PetriNet
from pmlab_lite.pn import SynchronousProduct
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
	
	dot = Digraph(name=filename, format=format)
	dot.attr(rankdir='LR', fontsize="10", nodesep="0.35",
			 ranksep="0.25 equally")

	# draw transitions
	dot.attr('node', shape='box', penwidth="1", fontsize="10",
			 fontname="Helvetica")

	for key, values in input_net.transitions.items():
		if key != 'tau' and not key.endswith("_synchronous"):
			for t in values:
				dot.node(str(t), key)
					
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
				 color='black', penwidth="1", fontsize="5",
				 fontname="Helvetica")

		for t in input_net.transitions['tau']:
			dot.node(str(t))

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
		dot.node(str(p), label=label, xlabel=str(p), shape="circle")

	#draw transitions	
	for i in range(0,len(transitions_by_index)):
		if transitions_by_index[i].endswith("_model"):
			dot.node( str(-(i+1)), "(" + transitions_by_index[i][:-6] + "," + BLANK + ")",shape="rect", style='unfilled', color=color[0])
		elif transitions_by_index[i].endswith("_log"):
			dot.node( str(-(i+1)), "(" + BLANK + "," + transitions_by_index[i][:-4] + ")", shape="rect", style='filled')
		elif transitions_by_index[i].endswith("_synchronous"):
			dot.node( str(-(i+1)), "(" + transitions_by_index[i][:-12] + "," + transitions_by_index[i][:-12] + ")", shape="rect", style='filled', color=color[1])


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

def draw_a_star_search_space(alignment, filename="search_space", format="pdf"):
    closed_list = alignment.closed_list_end
    initial_mark_vector = closed_list[0][1].marking_vector
    final_mark_vector = alignment.solutions[0].marking_vector
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
    for e in closed_list:
        #change color for darker nodes
        if not changed_fontcolor and counter < 30:
            changed_fontcolor = True
            fontcolor = 'white'
        #node is the final marking
        if ( np.array_equal(e[1].marking_vector, final_mark_vector) ):
            dot.node(str(e[1].marking_vector), label="H = " + str(round(float(e[1].cost_to_final_marking),3)) + "\nG = " + str(round(float(e[1].cost_from_init_marking),3)), 
                color=colors[1])
        #node is the initial marking
        elif ( np.array_equal(e[1].marking_vector, initial_mark_vector) ):
            dot.node(str(e[1].marking_vector), label="H = " + str(round(float(e[1].cost_to_final_marking),3)) + "\nG = " + str(round(float(e[1].cost_from_init_marking),3)),
                color=colors[0])
        #any other node
        else:
            dot.node(str(e[1].marking_vector), label="H = " + str(round(float(e[1].cost_to_final_marking),3)) + "\nG = " + str(round(float(e[1].cost_from_init_marking),3)), 
                color=colors[2]+str(counter), fontcolor=fontcolor)
        if counter > 0:
            counter -= 1

    #draw edges
    for node in closed_list:
        #very first nodes parent node is " '' "
        if node[1].parent_node != '':
            parent_node = node[1].parent_node
            dot.edge(str(parent_node.marking_vector), str(node[1].marking_vector), label=str(node[1].number))

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
