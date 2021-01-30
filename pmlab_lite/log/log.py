from pmlab_lite.manipulable import Manipulable
from datetime import datetime

class Event(dict):
    """An event is the minimum observable unit of information. It actually is a dictionary with, at least, three attributes: 'case_id', 'activity_name' and 'timestamp'."""

    def __init__(self, case_id):
        self["case:id"] = case_id

    def get_activity_name(self):
        return self.get_value("concept:name")

    def get_case_id(self):
        return self.get_value("case:id")

    def get_timestamp(self):
        return self['time:timestamp'] #self.get_value("time:timestamp")

    def get_value(self, attr):
        if attr == 'time:timestamp':
            return self[attr].strftime("%m/%d/%Y %H:%M:%S.%f")
        else:
            return self[attr]

    def get_attributes(self):
        return [attribute for attribute in self.keys()]


class EventCollection(Manipulable):
    """An event collection is an abstract iterable collection of events. This is the smallest collection of events."""

    def __iter__(self):
        return self

    def __next__(self) -> Event:
        raise NotImplemented


class EventLog(EventCollection):
    """
    An event log is a collection of events with a fixed size. It can also extend the 'Manipulable' (or whatever we call
    it) class. With this implementation, it is not possible to have trace attributes, but only events attributes.
    Direct access to single traces is also possible
    """

    def __init__(self):
        self.events = list() # events are still stored as list of events
        self.traces = dict() # traces have attributes and store events as under trace['events'] -> list of events
        self.A = set()
        self.classifiers = dict() # stores the classifiers, i.e. an identity for events
        self.globals = dict() # stores the globally defined attributes, i.e attributes every trace/event must contain
        self.extensions = dict() # stores log extensions
        self.attributes = dict() # stores log attributes

    def add_event(self, event: Event):
        self.events.append(event)
        case_id = event.get_case_id()
        self.traces[case_id] = self.traces.get(case_id, {})
        self.traces[case_id]['events'] = self.traces[case_id].get('events', []) + [event]
        return self

    def add_trace(self, case_id):
        self.traces[case_id] = {}
        return self

    def get_traces(self):
        """ Returns the list of events associated to the traces. """
        traces_only = []
        for key in self.traces:
            traces_only.append(self.traces[key]['events'])
        return traces_only

    def get_trace(self, case_id):
        return self.traces[case_id]

    def __iter__(self):
        return self.events.__iter__()

    def __next__(self):
        return self.events.__iter__().__next__()

    def activity_set(self):
        """Creates the set of unique activities for the log."""

        for event in self.events:
            self.A.add(event['concept:name'])

    def equal_by_classifier(self, event1: Event, event2: Event, classifier: str) -> bool:
        """ Return true if the given events are equal according to the classifier, false otherwise."""

        attrib1 = self.classifiers[classifier][0]
        attrib2 = self.classifiers[classifier][1]
        return event1[attrib1] == event2[attrib1] and event1[attrib2] == event2[attrib2]

    def filter_by_classifier(self, event, classifier: str) -> list:
        """Return a list of all events of the log that are equal to the given event by the given classifier.

        Args:
            event (Event): [The Event to compare all the other events of the log to.]
            classifier (str): [A classifier, i.e. a list of attributes the events must have the same values for, to be considered equal.]
        """
        equal_events = [event]
        for event2 in self.events:
            if self.equal_by_classifier(event, event2, classifier) and event is not event2:
                equal_events.append(event2)

        return equal_events

    def __check_standard_globals(self) -> bool:
        """ Checks if the standatd attributes are present in the global property for events in the log."""
        
        if {'concept:name', 'time:timestamp', 'lifecycle:transition'} <= set(self.globals['event']):
            return True
        else:
            return False

    def print_traces(self, start: int=0, num: int=1, attributes: list=None):
        """
            Prints specified number of traces from the log given the start index.
            For instance to print 3 traces starting from the 4th trace: log.print_traces(4, 3)

            Args:
                start (int, optional): The index of the start trace to print. Defaults to 0.
                num (int, optional): The number of the traces to print from start. Defaults to 1.

            Raises:
                Index out of bounds Error: Num > len(log) - 1
        """

        if attributes is not None: # try to print provided attributes
            if len(attributes) > 3:
                raise ValueError('maximum number of attributes to provide is 3')
            elif len(attributes) == 3:
                self.__print_three_attributes(attributes, start, num)
            elif len(attributes) == 2:
                self.__print_two_attributes(attributes, start, num)
            elif len(attributes) == 1:
                self.__print_one_attribute(attributes, start, num)

        elif self.__check_standard_globals():        # try to print the most common attributes of events in traces
            self.__print_standard_event_attributes(start, num)

        elif len(self.globals['event'] >= 3):
            self.__print_three_attributes(list(self.globals['event'].keys())[:3], start, num)

        elif len(self.globals['event'] == 2):
            self.__print_three_attributes(list(self.globals['event'].keys())[:2], start, num)

        elif len(self.globals['event'] == 1):
            self.__print_three_attributes(list(self.globals['event'].keys())[:1], start, num)

        else:
            print("The given log neither does not have any global attributes. Please provide the attributes to print as 'attributes' in the function call.")

    def __print_standard_event_attributes(self, start: int=0, num: int=1):
        self.__print_three_attributes(['concept:name', 'lifecycle:transition', 'time:timestamp'], start, num)

    def __print_one_attribute(self, attributes, start: int=0, num: int=1):

        traces_in_range = [self.traces[case_id]['events'] for case_id in self.traces][start:start+num]

        for i in range(len(traces_in_range)):
            print("TRACE_ID:",traces_in_range[i][0]['case:id'], "(trace number", i+start+1, ")")
            print(" ", attributes[0])
            for event in traces_in_range[i]:
                print(">", event.get_value(attributes[0]))
            print()

    def __print_two_attributes(self, attributes, start: int=0, num: int=1):

        traces_in_range = [self.traces[case_id]['events'] for case_id in self.traces][start:start+num]

        for i in range(len(traces_in_range)):
            print("TRACE_ID:",traces_in_range[i][0]['case:id'], "(trace number", i+start+1, ")")
            print("  {:24}{:36}".format(attributes[0], attributes[1]))
            for event in traces_in_range[i]:
                print("> {:24}{:36}".format(event.get_value(attributes[0]), event.get_value(attributes[1])))
            print()

    def __print_three_attributes(self, attributes, start: int=0, num: int=1):
        traces_in_range = [self.traces[case_id]['events'] for case_id in self.traces][start:start+num]

        for i in range(len(traces_in_range)):
            print("TRACE_ID:",traces_in_range[i][0]['case:id'], "(trace number", i+start+1, ")")
            print("  {:24}{:36}{:15}".format(attributes[0], attributes[1], attributes[2]))
            for event in traces_in_range[i]:
                print("> {:24}{:36}{:15}".format(event.get_value(attributes[0]), event.get_value(attributes[1]), event.get_value(attributes[2])))
            print()

    def print(self):
        """Prints the whole log."""

        self.print_traces(0, len(self.traces))
