import xml.etree.ElementTree as xmltree
from random import randint
from graphviz import Digraph

from .abstract_pn import AbstractPetriNet


class PetriNet(AbstractPetriNet):
    """ Class to represent a Petri Net."""

    def add_place(self, name, capacity=1):
        """
        Add a place to the net and set its token capacity. The name
        has to be numeric.

        Args:
            name: integer place name
            capacity: integer number of token per place

        Raises:
            ValueError: place identifier has to be unique
            TypeError: place identifier has to be numeric
        """
        if isinstance(name, int):
            if not self.place_exists(name):
                self.places.append((name, capacity))
            else:
                raise ValueError('place identifier has to be unique')
        else:
            raise TypeError('place identifier has to be numeric')

    def remove_place(self, name):
        """
        Remove a place from the netself.

        Args:
            name: integer place name
        """
        for idx, place in enumerate(self.places):
            if place[0] == name:
                self.remove_all_edges_of(name)
                del self.places[idx]
                break

    def add_transition(self, name):
        """
        Add a transition to the net. The name has to be a string.

        Args:
            name: string name of transition

        Raises:
            ValueError: place identifier has to be unique
            TypeError: place identifier has to be a string
        """
        if isinstance(name, str):
            if not self.transition_exists(name):
                self.transitions.append(name)
            else:
                raise ValueError('transition identifier has to be unique')
        else:
            raise TypeError('transition identifier has to be a string')

    def remove_transition(self, name):
        """
        Remove the given transition from the net.

        Args:
            name: string of the transition
        """
        for idx, transition in enumerate(self.transitions):
            if transition == name:
                self.remove_all_edges_of(name)
                del self.transitions[idx]
                break

    def add_edge(self, source, target, two_way=False):
        """
        Add a new edge between two elements in the net. If two way argument
        is True, one edge per direction will be added.

        Args:
            source: name of transition/place
            target: name of transition/place
            two_way: add edge from target to source

        Raises:
            ValueError: source/target does not exists
        """
        if isinstance(source, int):
            # source is place
            if not self.place_exists(source):
                raise ValueError('place does not exist')
        else:
            # source is transition
            if not self.transition_exists(source):
                raise ValueError('transition does not exist')

        if isinstance(target, int):
            # target is place
            if not self.place_exists(target):
                raise ValueError('place does not exist')
        else:
            # target is transition
            if not self.transition_exists(target):
                raise ValueError('transition does not exist')

        if not two_way:
            self.edges.append((source, target))
        else:
            self.edges.append((source, target))
            self.edges.append((target, source))

    def remove_edge(self, source, target):
        """Remove edge.

        Args:
            source: name of transition/place
            target: name of transition/place
        """
        for idx, edge in enumerate(self.edges):
            if edge[0] == source and edge[1] == target:
                del self.edges[idx]
                break

    def remove_all_edges_of(self, name):
        """
        Remove all edge where the given element is either the source or
        the target.

        Args:
            name: name of place/transition
        """
        # where element is source
        for e in list(filter(lambda x: x[0] == name, self.edges)):
            del self.edges[self.edges.index(e)]

        # where element is target
        for e in list(filter(lambda x: x[1] == name, self.edges)):
            del self.edges[self.edges.index(e)]

    def is_enabled(self, transition):
        """
        Check whether a transition is able to fire or not.

        Args:
            transition: string name of transition

        Retruns:
            True if transition is enabled, False otherwise.
        """
        # all palces which are predecessor of the given transition
        input_places = list(filter(lambda x: x[1] == transition, self.edges))

        # do any inputs exist?
        if len(input_places) > 0:
            # check if each place contains at least one token aka. has a
            # marking
            for place in input_places:
                # input place has no token
                if not place[0] in self.marking:
                    return False
            # transition is able to fire
            return True
        else:
            # no input places
            return False

    def add_marking(self, place, token=1):
        """
        Add a new marking to the net.

        Args:
            place: int name of place
            token: int number of token to add

        Raises:
            ValueError: place does not exists
        """
        if self.place_exists(place):
            self.marking[place] = token
        else:
            raise ValueError('place does not exist.')

    def replay(self):
        """Randomly replay the net starting from its current marking.

        Returns:
            Sequence of transitions which were fired.
        """
        seq = []
        enabled_transitions = self.all_enabled_transitions()
        while(len(enabled_transitions) > 0):
            t = enabled_transitions[randint(0, len(enabled_transitions) - 1)]
            seq.append(t)
            self.fire_transition(t)
            enabled_transitions = self.all_enabled_transitions()

        return seq

    def transition_exists(self, name):
        """
        Check whether the transition exists in the net or not.

        Args:
            name: string name of transition

        Returns:
            True if transition exists in petri net, False otherwise.
        """
        return name in self.transitions

    def place_exists(self, name):
        """
        Check whether the place exists in the net or not.

        Args:
            name: int name of place

        Returns:
            True if place exists in petri net, False otherwise.
        """
        if len(list(filter(lambda x: x[0] == name, self.places))) > 0:
            return True
        else:
            return False

    def all_enabled_transitions(self):
        """
        Find all transitions in the net which are enabled.

        Retruns:
            List of all enabled transitions.
        """
        return list(filter(lambda x: self.is_enabled(x),
                           self.transitions))

    def fire_transition(self, transition):
        """
        Fire transition.

        Args:
            name: string name of transition
        """
        inputs = [item[0] for item in
                  list(filter(lambda x: x[1] == transition,
                              self.edges))]

        outputs = [item[1] for item in
                   list(filter(lambda x: x[0] == transition,
                               self.edges))]

        # update ingoing token
        for i in inputs:
            if i in self.marking:
                self.marking[i] -= 1

                if self.marking[i] == 0:
                    self.marking.pop(i)

        # update outgoing token
        for o in outputs:
            if o in self.marking:
                self.marking[o] += 1
            else:
                self.marking[o] = 1

    def draw(self, filename="petri_net", format="pdf"):
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

        for t in self.transitions:
            dot.node(t)

        # draw place
        dot.attr('node', shape='circle', style="filled",
                 color='lightgrey', penwidth="1", fontsize="10",
                 fontname="Helvetica")

        for p in self.places:
            dot.node(str(p[0]))

        # draw edges
        for e in self.edges:
            dot.edge(str(e[0]), str(e[1]))

        # dot.render()
        return dot

    def from_pnml_file(self, filename):
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
            self.add_transition(name)

        for c in net.iterfind('.//%splace' % ns):
            xml_id = c.attrib['id']
            name = get_name_or_id(c)

            p = self.add_place(int(name))
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

            self.add_edge(s, t)

    def from_ts_file(self):
        """Create a petri net from a transition system."""
        pass

    def to_ts_file(self):
        """Convert the petri net into a transition system."""
        pass

    def export_pnml_file(self, filename):
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

        for p in self.places:
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

        for t in self.transitions:
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

        for e in self.edges:
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
