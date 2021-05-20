from pmlab_lite.pn.abstract_pn import AbstractPetriNet
import xml.etree.ElementTree as xmltree



def export(input_net: AbstractPetriNet, filename, export_marking=True):
	"""
	Save Petri net in PNML format.

	:param input_net: Petri net object
	:param filename: file or filename of the outout file
	:param export_marking: whether the current marking should be exported or not
	"""

	baseURL = '{http://www.pnml.org/version-2009/grammar/pnml}'

	if ".pnml" not in filename:
		filename = ".".join([filename, "pnml"])

	def add_text(element, text):
		xmltree.SubElement(
			element, ''.join([baseURL, 'text'])).text = text

	def add_name(element, text):
		add_text(xmltree.SubElement(
			element, ''.join([baseURL, 'name'])), text)

	xmltree.register_namespace("pnml",
							   "http://www.pnml.org/version-2009/grammar/pnml")

	root = xmltree.Element(''.join([baseURL, 'pnml']))
	net = xmltree.SubElement(root, ''.join([baseURL, 'net']), {
		''.join([baseURL, 'id']): 'pmlabNet1',
		''.join([baseURL, 'type']): 'http://www.pnml.org/version-2009/grammar'
									'/pnmlcoremodel'
		})

	add_name(net, filename)
	page = xmltree.SubElement(net, ''.join([baseURL, 'page']), {
		''.join([baseURL, 'id']): 'n0'
		})

	node_num = 1
	id_map = {}

	for k, p in input_net.places.items():
		name = str(p)

		xml_id = "p%d" % node_num
		node = xmltree.SubElement(page, ''.join([baseURL, 'place']),
								  {''.join([baseURL, 'id']): xml_id})
		add_name(node, name)

		if export_marking:
			tokens = input_net.marking[k]
			if tokens >= 1:
				marking = xmltree.SubElement(node, ''.join([baseURL,
															'initialMarking']))
				add_text(marking, str(tokens))

		id_map[p] = xml_id
		node_num += 1

	for name, ids in input_net.transitions.items():
		for id in ids:
			assert id not in id_map

			xml_id = "t%d" % (id * -1)
			node = xmltree.SubElement(page, ''.join([baseURL, 'transition']),
									  {''.join([baseURL, 'id']): xml_id})
			add_name(node, name)

			id_map[id] = xml_id
			node_num += 1

	for e in input_net.edges:
		xml_id = "arc%d" % node_num
		node = xmltree.SubElement(page, ''.join([baseURL, 'arc']), {
			''.join([baseURL, 'id']): xml_id,
			''.join([baseURL, 'source']): id_map[e[0]],
			''.join([baseURL, 'target']): id_map[e[1]]
			})
		add_name(node, "%d" % 1)

		node_num += 1

	tree = xmltree.ElementTree(root)
	tree.write(filename, encoding='UTF-8', xml_declaration=True,
			   default_namespace='http://www.pnml.org/version-2009/grammar'
								 '/pnml')


def load(input_net: AbstractPetriNet, filename):
	"""
	Overwrite petri net structure by reading in a PNML file and
	generate a new petri net structure.

	Args:
		filename: path to PNML file

	Raises:
		ValueError: invalid PNML format
	"""
	transition_counter = 0
	place_counter = 0

	tree = xmltree.parse(filename)
	ns = '{http://www.pnml.org/version-2009/grammar/pnml}'
	root = tree.getroot()
	net = root.find('%snet' % ns)

	if net is None:
		# Try non namespaced version
		# "Be conservative in what you send, be liberal in what you accept"
		net = root.find('net')
		if net is None:
			# Nothing to do
			raise ValueError('invalid PNML format')
		# Otherwise assume entire file is non-namespaced
		ns = ''

	id_map = {}

	def has_name(element):
		node = element.find('%sname/%stext' % (ns, ns))
		return node is not None

	def get_name_or_id(element):
		node = element.find('%sname/%stext' % (ns, ns))
		if node is not None:
			return node.text
		else:
			return element.attrib['id']

	def remove_suffix(s, suffix):
		if s.endswith(suffix):
			return s[:-len(suffix)]
		else:
			return s

	# Recursively enumerate all nodes with tag = transition
	# They might be distributed in several <page> child tags

	for c in net.iterfind('.//%stransition' % ns):
		transition_counter -= 1
		xml_id = c.attrib['id']
		name = remove_suffix(get_name_or_id(c), '+complete')

		if 'tau' in name:
			name = ''
		# If it has no name, it's probably a dummy transition
		# dummy = not has_name(c)

		id_map[xml_id] = transition_counter
		input_net.add_transition(name, transition_counter)

	for c in net.iterfind('.//%splace' % ns):
		place_counter += 1
		init_marking = c.find('%sinitialMarking/text' % ns)

		if 'id' in c.attrib.keys():  # else marking
			xml_id = c.attrib['id']
			name = get_name_or_id(c)

			p = input_net.add_place(place_counter)
			id_map[xml_id] = place_counter

		if init_marking is not None:
			input_net.add_marking(place_counter, int(init_marking.text))

	for c in net.iterfind('.//%sarc' % ns):
		s = id_map[c.attrib['source']]
		t = id_map[c.attrib['target']]

		input_net.add_edge(int(s), int(t))
