from . pn import PetriNet


class TraceNet(PetriNet):
    """
    Class to represent a trace net.
    For creation a trace is passed to the constructor.
    """

    def __init__(self, trace: list):
        self.places = {}
        self.transitions = {}
        self.edges = []
        self.marking = []
        self.capacity = []
        self.counter = 0  # mapping
        self.__make_trace_net(trace)

    def __make_trace_net(self, trace: list):
        """
        Builds the trace net from the given trace.
        """
        # assume empty PetriNet
        num_places = len(trace)+1

        for i in range(1, num_places+1):
            self.add_place(i)

        for t in trace:
            self.add_transition(t)

        for i in range(1, num_places):
            self.add_edge(i, -i)
            self.add_edge(-i, i+1)

        return self
