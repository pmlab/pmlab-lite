from pmlab_lite.manipulable import Manipulable
from datetime import datetime

class Event(dict):
    """An event is the minimum observable unit of information. It actually is a dictionary with, at least, three attributes: 'case_id', 'activity_name' and 'timestamp'."""

    def __init__(self, case_id):
        self["case:id"] = case_id

    def get_activity_name(self):
        return self["concept:name"]

    def get_case_id(self):
        return self["case:id"]

    def get_timestamp(self):
        return self['time:timestamp']

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
        self.metadata = dict() # stores log attributes

    def add_event(self, event: Event):
        self.events.append(event)
        case_id = event.get_case_id()
        self.traces[case_id] = self.traces.get(case_id, {})
        self.traces[case_id]['events'] = self.traces[case_id].get('events', []) + [event] 
        return self

    def add_trace(self, case_id):
        self.traces[case_id] = {}
        return self

    def activity_set(self):
        """Creates the set of unique activities for the log."""
        
        for event in self.events:
            self.A.add(event['concept:name'])

    def get_traces(self):
        """ Returns the list of events associated to the traces. """
        traces_only = []
        for key in self.traces:
            traces_only.append(self.traces[key]['events'])
        return traces_only

    def get_trace(self, case_id):
        return self.traces[case_id]

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

    def __iter__(self):
        return self.events.__iter__()

    def __next__(self):
        return self.events.__iter__().__next__()

    def print_traces(self, start: int=0, num: int=1): #maybe change to print global attributes so printing is flexible to different logs
        """
            Prints specified number of traces from the log given the start index. 
            For instance to print 3 traces starting from the 4th trace: log.print_traces(4, 3)

            Args:
                start (int, optional): The index of the start trace to print. Defaults to 0.
                num (int, optional): The number of the traces to print from start. Defaults to 1.

            Raises:
                Index out of bounds Error: Num > len(log) - 1
        """  
        
        traces_in_range = list(self.traces.items())[start:start+num]               #gives us the traces as tuples: [ (case_id, [event1, event2, ...]), ... ] so we can index with numbers rather than case_id

        for i in range(len(traces_in_range)):
            print("TRACE_ID:",traces_in_range[i][0], "(trace number", i+start, ")")
            print("  {:28}{:31}{:15}".format("activity name", "time", "transition"))
            for event in traces_in_range[i][1]:
                activity = event.get_activity_name()
                time = event.get_timestamp().strftime("%m/%d/%Y %H:%M:%S.%f %Z")
                transition = event['lifecycle:transition']
                print("> {:28}{:31}{:15}".format(activity, time, transition)) #
            print()

    def print(self):
        """Prints the whole log."""
        
        self.print_traces(0, self.len)