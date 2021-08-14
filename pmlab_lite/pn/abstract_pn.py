from abc import ABC, abstractmethod


class AbstractPetriNet(ABC):
    """Abstract class for petri net object, eg. petri net, trace net."""

    def __init__(self):
        self.places = {}
        self.transitions = {}
        self.edges = []
        self.marking = []
        self.capacity = []
        self.counter = 0  # mapping
        self.exceeded_places = []  # indexes of places

    @abstractmethod
    def add_place(self, name, capacity=1):
        pass

    @abstractmethod
    def remove_place(self, name):
        pass

    @abstractmethod
    def add_transition(self, name):
        pass

    @abstractmethod
    def remove_transition(self, name):
        pass

    @abstractmethod
    def add_edge(self, place, transition, two_way=False):
        pass

    @abstractmethod
    def remove_edge(self, place, transitions):
        pass

    @abstractmethod
    def is_enabled(self, transition):
        pass

    @abstractmethod
    def add_marking(self, place, token=1):
        pass

    @abstractmethod
    def replay(self):
        pass
