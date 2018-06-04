from pmlab_lite.pn import AbstractPetriNet
import xml.etree.ElementTree as xmltree

def export(input_net: AbstractPetriNet, filename):
	"""
	Save the petri net in PNML format.

	Args:
		filename: file or filename in which the PN has to be written

	"""

	if ".pnml" not in filename:
		filename = ".".join([filename, "pnml"])

	def add_text(element, text):
		xmltree.SubElement(
			element, '{http://www.pnml.org/version-2009/grammar/pnml}text').text = text

	def add_name(element, text):
		add_text(xmltree.SubElement(
			element, '{http://www.pnml.org/version-2009/grammar/pnml}name'), text)

	xmltree.register_namespace("pnml", "http://www.pnml.org/version-2009/grammar/pnml")

	root = xmltree.Element('{http://www.pnml.org/version-2009/grammar/pnml}pnml')
	net = xmltree.SubElement(root, '{http://www.pnml.org/version-2009/grammar/pnml}net', {
		'{http://www.pnml.org/version-2009/grammar/pnml}id': 'pmlabNet1',
		'{http://www.pnml.org/version-2009/grammar/pnml}type': 'http://www.pnml.org/version-2009/grammar/pnmlcoremodel'
	})

	add_name(net, filename)
	page = xmltree.SubElement(net, '{http://www.pnml.org/version-2009/grammar/pnml}page', {
		'{http://www.pnml.org/version-2009/grammar/pnml}id': 'n0'
	})

	node_num = 1
	id_map = {}

	for p in input_net.places:
		name = str(p[0])

		xml_id = "p%d" % node_num
		node = xmltree.SubElement(page, '{http://www.pnml.org/version-2009/grammar/pnml}place',
								  {'{http://www.pnml.org/version-2009/grammar/pnml}id': xml_id})
		add_name(node, name)

		# tokens = self.vp_place_initial_marking[p]
		# if tokens >= 1:
		#     marking = xmltree.SubElement(node, '{http://www.pnml.org/version-2009/grammar/pnml}initialMarking')
		#     add_text(marking, str(tokens))

		id_map[p[0]] = xml_id
		node_num += 1

	for t in input_net.transitions:
		assert t not in id_map
		name = t
		# if self.vp_transition_dummy[t]:
		#     name = '' # empty label for dummies
		xml_id = "t%d" % node_num
		node = xmltree.SubElement(page, '{http://www.pnml.org/version-2009/grammar/pnml}transition',
								  {'{http://www.pnml.org/version-2009/grammar/pnml}id': xml_id})
		add_name(node, name)

		id_map[t] = xml_id
		node_num += 1

	for e in input_net.edges:
		xml_id = "arc%d" % node_num
		node = xmltree.SubElement(page, '{http://www.pnml.org/version-2009/grammar/pnml}arc', {
			'{http://www.pnml.org/version-2009/grammar/pnml}id': xml_id,
			'{http://www.pnml.org/version-2009/grammar/pnml}source': id_map[e[0]],
			'{http://www.pnml.org/version-2009/grammar/pnml}target': id_map[e[1]]
		})
		add_name(node, "%d" % 1)

		node_num += 1

	tree = xmltree.ElementTree(root)
	tree.write(filename, encoding='UTF-8', xml_declaration=True,
			   default_namespace='http://www.pnml.org/version-2009/grammar/pnml')


def load(input_net: AbstractPetriNet, filename):
	"""
	Overwrite petri net structure by reading in a PNML file and
	generate a new petri net structure.

	Args:
		filename: path to PNML file

	Raises:
		ValueError: invalid PNML format
	"""
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
		xml_id = c.attrib['id']
		name = remove_suffix(get_name_or_id(c), '+complete')

		# If it has no name, it's probably a dummy transition
		dummy = not has_name(c)

		id_map[xml_id] = name
		input_net.add_transition(name)

	for c in net.iterfind('.//%splace' % ns):
		xml_id = c.attrib['id']
		name = get_name_or_id(c)

		p = input_net.add_place(int(name))
		id_map[xml_id] = name
	"""
		marking = c.find('%sinitialMarking/%stext' % (ns, ns))
		if marking is not None:
			pn.set_initial_marking(p,int(marking.text))
	"""

	for c in net.iterfind('.//%sarc' % ns):
		s = id_map[c.attrib['source']]
		t = id_map[c.attrib['target']]

		if str.isnumeric(s):
			s = int(s)

		if str.isnumeric(t):
			t = int(t)

		input_net.add_edge(s, t)