from . pn import PetriNet
from . tn import TraceNet
from pmlab_lite.alignments import constants as c


class SynchronousProduct(PetriNet):
    """
    Class to represent a synchronous prodcut.
    For creation the constructor needs to get passed a PetriNet and a TraceNet.
    """

    def __init__(self, petri_net: PetriNet, trace_net: TraceNet):
        self.places = {}
        self.transitions = {}
        self.edges = []
        self.marking = []
        self.capacity = []
        self.counter = 0  # mapping
        self.transitions_as_tuples = []
        self.__synchronous_product(petri_net, trace_net)

    # TODO clunky -> more easy sync transitions with transitions_by_index()
    def __synchronous_product(self, petri_net: PetriNet, trace_net: TraceNet):
        # petri_net is model_net
        place_offset = len(petri_net.places.values())
        transition_offset = len(petri_net.transitions_by_index())

        # PLACES
        # copying the model net
        for p in petri_net.places.values():
            self.add_place(p)

            # copying the trace net
        for p in trace_net.places.values():
            self.add_place(p + place_offset)

        # TRANSITIONS
        # copying the modelnet
        model_transitions_by_index = petri_net.transitions_by_index()
        for i in range(0, len(model_transitions_by_index)):
            self.add_transition(model_transitions_by_index[i] + "_model")

        # copying the trace net
        trace_transitions_by_index = trace_net.transitions_by_index()
        for i in range(0, len(trace_transitions_by_index)):
            self.add_transition(trace_transitions_by_index[i] + "_log")

        # EDGES
        # copying the model net
        for edge in petri_net.edges:
            self.add_edge(edge[0], edge[1])

        # copying the trace net
        for edge in trace_net.edges:
            new_edge = (0, 0)
            if edge[0] > 0:
                new_edge = (edge[0]+place_offset, edge[1] - transition_offset)
            elif edge[0] < 0:
                new_edge = (edge[0] - transition_offset, edge[1]+place_offset)
            self.add_edge(new_edge[0], new_edge[1])

        # CREATE NEW SYNCHRONOUS PRODUCT TRANSITIONS AND EDGES
        self.__sp_transitions(petri_net, trace_net, place_offset)

        self.__make_tuple_transitions()

        return self

    def __sp_transitions(self, pn: PetriNet, tn: TraceNet,
                         off: int):
        """ Creates the transitions for the SynchronousProduct """
        # whenever trace_t has the same name as model_t we create a new sync_t
        # with all the in/outputs from the model_ and trace_t combined
        for keyT1 in tn.transitions.keys():
            for keyT2 in pn.transitions.keys():
                if keyT1 == keyT2:
                    for i in range(0, len(tn.transitions[keyT1])):
                        keyT3 = keyT1 + "_synchronous"
                        self.add_transition(keyT3)
                        # copy all in/outputs from the trace net transitions
                        # onto the new sync prod transitions

                        # inputs
                        for node in tn.get_inputs(tn.transitions[keyT1][i]):
                            self.add_edge(node+off, self.transitions[keyT3][i])
                        # outputs
                        for node in tn.get_outputs(tn.transitions[keyT1][i]):
                            self.add_edge(self.transitions[keyT3][i], node+off)

                        # copy all the in/outputs from the model transitions
                        # onto the new sync prod transitions
                        # inputs
                        for node in pn.get_inputs(pn.transitions[keyT2][0]):
                            self.add_edge(node, self.transitions[keyT3][i])
                        # outpus
                        for node in pn.get_outputs(pn.transitions[keyT2][0]):
                            self.add_edge(self.transitions[keyT3][i], node)

    def __make_tuple_transitions(self):
        ts = self.transitions_by_index()
        for i in range(len(ts)):
            if ts[i].endswith("synchronous"):
                a = (ts[i].rsplit('_', 1)[0], ts[i].rsplit('_', 1)[0])
            elif ts[i].endswith("model"):
                a = (ts[i].rsplit('_', 1)[0], c.BLANK)
            elif ts[i].endswith("log"):
                a = (c.BLANK, ts[i].rsplit('_', 1)[0])

            self.transitions_as_tuples.append(a)
