from . abstract_pn import AbstractPetriNet
from random import randint
import numpy as np


class PetriNet(AbstractPetriNet):
    """Class to represent a Petri Net."""

    def add_place(self, place_name: int, capacity: int = 1):
        """
        Add a place to the net and set its token capacity. The name
        has to be numeric. Further, the keys are indices of the corresponding
        marking vector and capacity vector.

        Args:
            name: integer place name
            capacity: integer number of token per place

        Raises:
            ValueError: place identifier has to be unique
            TypeError: place identifier has to be numeric
        """
        if isinstance(place_name, int) and place_name > 0:
            if not self.place_exists(place_name):
                idx = len(self.places)
                self.places[idx] = place_name
                self.marking.append(0)
                self.capacity.append(capacity)
            else:
                raise ValueError('place identifier has to be unique')
        else:
            raise TypeError('place identifier has to be numeric and > 0')

        return self

    def remove_place(self, place_name: int):
        """
        Remove a place from the net.

        Args:
            name: integer place name
        """
        index = 0
        # !!!if name not in places -> index stays 0 and 1st place gets removed

        for idx, place in self.places.items():
            if place == place_name:
                index = idx
                break

        # shift places with larger index to the left
        if index + 1 == len(self.places):  # last index
            self.places.pop(index)
        else:
            for idx in range(index, len(self.places) - 1):
                self.places[idx] = self.places[idx + 1]

            self.places.pop(len(self.places) - 1)

        del self.marking[index]
        del self.capacity[index]

        return self

    def num_places(self) -> int:
        return len(self.places.keys())

    def get_mapping(self) -> dict:
        return self.transitions

    def get_marking(self) -> list:
        return self.marking

    def add_transition(self, name: str, transition_id: int = None):
        """
        Add a transition to the net. The name has to be a string.
        Adding the same name multiple times will append to the list,
        which the name(key) points to.

        Args:
            name: string name of transition, key
            id: negative integer, value of transition at the key(name)
        """

        self.counter -= 1

        if len(name) == 0:
            name = 'tau'

        if transition_id is None:
            transition_id = self.counter
        else:
            if transition_id >= 0:
                raise ValueError('transition identifier has to be < 0')

        if name in self.transitions.keys():
            self.transitions[name].append(transition_id)
        else:
            self.transitions[name] = [transition_id]

        return self

    def remove_transition(self, id: int):
        """
        Remove the given transition from the net.

        Args:
            id: value of the transition at key=name
        """

        for key, values in self.transitions.items():
            if id in values:
                values.remove(id)
                if len(values) == 0:
                    self.transitions.pop(key, None)
                break

        return self

    def num_transitions(self) -> int:
        return sum([len(v) for v in self.transitions.values()])

    def add_edge(self, source, target, two_way: bool = False):
        """Add a new edge between two elements in the net. If two way argument
        is True, one edge per direction will be added.

        Args:
            source: id of transition/name of place
            target: id of transition/name of place
            two_way: add edge from target to source

        Raises:
            ValueError: source/target does not exists """

        if source > 0 and target > 0 or source < 0 and target < 0:
            raise ValueError('edges can only be added between places and '
                             'transition and vice versa')

        if source > 0:
            # source is place
            if not self.place_exists(source):
                raise ValueError('place does not exist')
        else:
            # source is transition
            if not self.transition_exists(source):
                raise ValueError('transition does not exist')

        if target > 0:
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

        return self

    def remove_edge(self, source, target):
        """Remove edge.

        Args:
            source: id of transition/name of place
            target: id of transition/name of place
        """
        for idx, edge in enumerate(self.edges):
            if edge[0] == source and edge[1] == target:
                del self.edges[idx]
                break

        return self

    def remove_all_edges_of(self, name):
        """
        Remove all edge where the given element is either the source or
        the target.

        Args:
            name: id of transition/name of place
        """
        # where element is source
        for e in list(filter(lambda x: x[0] == name, self.edges)):
            del self.edges[self.edges.index(e)]

        # where element is target
        for e in list(filter(lambda x: x[1] == name, self.edges)):
            del self.edges[self.edges.index(e)]

        return self

    def index_of_place(self, place_name: int) -> int:
        for idx, p in self.places.items():
            if p == place_name:
                return idx

    def rev_mapping(self) -> dict:
        rev_mapping = {}
        for k, v in self.get_mapping().items():
            for k2 in v:
                rev_mapping[k2] = k
        return rev_mapping

    def transitions_by_index(self) -> dict:
        """
        Returns the reverse of data structure of the transitions,
        i.e. a dict where the id of the transitions are the keys and the
        values are the transtions names (strings)
        """
        transitions_by_index = dict()

        for key, value in self.transitions.items():
            for val in value:
                transitions_by_index[-(val+1)] = key

        return transitions_by_index

    def is_enabled(self, transition_id: int) -> bool:
        """
        Check whether a transition is able to fire or not.

        Args:
            transition: id of transition

        Retruns:
            True if transition is enabled, False otherwise.
            Special case: returning true, when a transition has no input places
        """

        # all palces which are predecessor of the given transition
        inputs = self.get_inputs(transition_id)
        # do any inputs exist?
        if len(inputs) > 0:
            # check if each place contains at least one token aka. has a
            # marking
            for i in inputs:
                idx = self.index_of_place(i)
                # input place has no token
                if self.marking[idx] == 0:
                    return False
            # transition is able to fire
            return True
        else:
            # no input places
            return True

    def get_inputs(self, node: int) -> list:
        """
        args: node; name of place or id of transition

        returns: list of numbers, positives when node is a transition
        and negatives when node is a place
        """
        inputs = []
        for edge in self.edges:
            if edge[1] == node:
                inputs.append(edge[0])
        return inputs

    def get_outputs(self, node: int) -> list:
        """
        args: node; name of place or id of transition

        returns: list of numbers, positives when node is a transition
        and negatives when node is a place
        """
        outputs = []
        for edge in self.edges:
            if edge[0] == node:
                outputs.append(edge[1])
        return outputs

    def add_marking(self, place_name: int, num_token: int = 1):
        """
        Add a new marking to the net.

        Args:
            place: name of place
            num_token: number of token to add

        Raises:
            ValueError: place does not exists
        """
        index = None
        if self.place_exists(place_name):
            for idx, p in self.places.items():
                if p == place_name:
                    index = idx
                    break

            self.marking[index] = num_token
        else:
            raise ValueError('place does not exist.')

        return self

    def init_marking(self):
        """Resets the net to the init marking,
        i.e. all input places contain one token."""

        self.null_marking()
        for i in self.get_index_init_places():
            self.marking[i] = 1

    def null_marking(self):
        """Resets the net to the null marking,
        i.e. all places contain no token."""

        for i in range(0, len(self.marking)):
            self.marking[i] = 0

    def replay(self, max_length: int) -> list:
        """Randomly replay the net starting from its current marking.

        Returns:
            Sequence of transitions which were fired.
        """
        seq = []
        enabled_transitions = self.all_enabled_transitions()
        while (len(enabled_transitions) > 0 and len(seq) < max_length):
            t = enabled_transitions[randint(0, len(enabled_transitions) - 1)]
            seq.append(t)
            self.fire_transition(t)
            enabled_transitions = self.all_enabled_transitions()

        if len(seq) == max_length:
            seq.append('BREAK')

        return seq

    def transition_exists(self, transition_id: int) -> bool:
        """
        Check whether the transition exists in the net or not.

        Args:
            name: id of transition

        Returns:
            True if transition exists in petri net, False otherwise.
        """

        # flatten list
        transition_mapping = [item for sublist in self.transitions.values() for
                              item
                              in sublist]
        return transition_id in transition_mapping

    def place_exists(self, place_name: int) -> bool:
        """
        Check whether the place exists in the net or not.

        Args:
            name: name of place

        Returns:
            True if place exists in petri net, False otherwise.
        """

        return place_name in list(self.places.values())

    def all_enabled_transitions(self) -> list:
        """
        Find all transitions in the net which are enabled.

        Returns:
            List of all enabled transitions.
        """
        transitions = [item for sublist in self.transitions.values() for item
                       in sublist]

        return list(filter(lambda x: self.is_enabled(x), transitions))

    def fire_transition(self, transition_id: int,
                        ignore_warnings: bool = False):
        """
        Fire transition. If capacities of places would be exceeded
        a warning is printed, which can be turned off.

        Args:
            transition_id (int): negative id of transition to fire
            ignore_exceedings (bool, optional): If true warnings for exceeded
            capacity of places are not shown. Defaults to False.
        """
        if self.is_enabled(transition_id):
            inputs = self.get_inputs(transition_id)

            outputs = self.get_outputs(transition_id)

            # update ingoing token
            for i in inputs:
                idx = self.index_of_place(i)

                # check if places before t is already exceeded
                # and would be at allowed capacity after firing t,
                # i.e. with one token less
                marking = self.marking[idx]
                capacity = self.capacity[idx]
                if (idx in self.exc_idx and marking == capacity+1):
                    self.exc_idx.remove(idx)

                self.marking[idx] -= 1

            # update outgoing token
            for o in outputs:
                idx = self.index_of_place(o)

                # check if the max marking of the target place will be exceeded
                if self.marking[idx] >= self.capacity[idx]:
                    if not ignore_warnings:
                        print('Caution: Capacity (', self.capacity[idx],
                              ') of place', o, 'will be exceeded by',
                              self.marking[idx]-self.capacity[idx]+1)
                    self.exc_idx.append(idx)

                self.marking[idx] += 1
        else:
            print("Transition is not enabled!")

    def get_exceeded_places(self):
        return [self.places[idx] for idx in self.exc_idx]

    def __repr__(self):
        """
        Change class representation.

        :return: string
        """
        desc = "Transitions: %s \n" \
               "Places: %s \n" \
               "Capacities: %s \n" \
               "Marking: %s \n" \
               "Edges: %s" % (self.transitions, self.places,
                              self.capacity, self.marking, self.edges)

        return desc

    def get_index_init_places(self) -> list:
        """
        Returns a list of the indices of the initial places,
        i.e. the keys to the values(names) of the place names for all places,
        who do not have any input transitions.
        """
        index_places_start = []
        for key in self.places.keys():
            if len(self.get_inputs(self.places[key])) == 0:
                index_places_start.append(key)
        return index_places_start

    def get_index_final_places(self) -> list:
        """
        Returns a list of the indices of the final places,
        i.e. the keys to the values(names) of the place names for all places,
        who do not have any output transitions.
        """
        index_places_end = []
        for key in self.places.keys():
            if len(self.get_outputs(self.places[key])) == 0:
                index_places_end.append(key)
        return index_places_end

    def get_init_marking(self) -> np.ndarray:
        init_mark_vector = np.repeat(0, len(self.places))
        for index in self.get_index_init_places():
            init_mark_vector[index] = 1
        return init_mark_vector

    def get_final_marking(self) -> np.ndarray:
        final_mark_vector = np.repeat(0, len(self.places))
        for index in self.get_index_final_places():
            final_mark_vector[index] = 1
        return final_mark_vector

    def incidence_matrix(self) -> np.ndarray:
        # Creating an empty matrix
        incidence_matrix = np.zeros((self.num_places(),
                                     self.num_transitions()), dtype=int)

        transitions_by_index = self.transitions_by_index()

        for t in transitions_by_index:
            for key in self.places.keys():
                col_index = t
                row_index = key

                t_val = -(t+1)  # reverse the idx, to be the transtions value
                p = self.places[key]

                # edge goes from T to P
                if (t_val, p) in self.edges:
                    incidence_matrix[row_index][col_index] += 1
                # edge goes from P to T
                if (p, t_val) in self.edges:
                    incidence_matrix[row_index][col_index] -= 1

        return incidence_matrix
