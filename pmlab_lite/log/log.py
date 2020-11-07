from pmlab_lite.manipulable import Manipulable
from datetime import datetime

class Event(dict):
    """An event is the minimum observable unit of information. It actually is a dictionary with, at least, three attributes: 'case_id', 'activity_name' and 'timestamp'."""

    def __init__(self, activity_name, case_id):
        self["concept:name"] = activity_name
        self["case_id"] = case_id

    def get_activity_name(self):
        return self["concept:name"]

    def get_case_id(self):
        return self["case_id"]

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
        self.traces = dict() # traces are stored as dictionary of case id -> list of events
        self.len = 0         # number of traces
        self.num_events = 0  # number of events
        self.A = set() 

    def add_event(self, event: Event):
        self.events.append(event)
        self.traces[event.get_case_id()] = self.traces.get(event.get_case_id(), []) + [event] 
        return self

    def add_trace(self, case_id, activity_names: []):
        for activity_name in activity_names:
            self.add_event(Event(activity_name, case_id))
        return self

    def activity_set(self):
        """Creates the set of unique activities for the log."""
        
        for event in self.events:
            self.A.add(event['concept:name'])

    def get_traces(self):
        return self.traces.values()

    def get_trace(self, case_id):
        return self.traces[case_id]

    def __iter__(self):
        return self.events.__iter__()

    def __next__(self):
        return self.events.__iter__().__next__()

    def print_traces(self, start: int=0, num: int=1):
        """
            Prints the traces of the log from 'start' to 'end'. 
            For instance to print 3 traces starting from the 4th trace: log.print_traces(4, 3)

            Args:
                start (int, optional): The index of the start trace to print. Defaults to 0.
                num (int, optional): The number of the traces to print from start. Defaults to 1.

            Raises:
                Index out of bounds Error: Num > len(log) - 1
        """  
        
        traces_in_range = list(self.traces.items())[start:start+num]               #gives us the traces as tuples: [ (case_id, [event1, event2, ...], ...) ] so we can index with numbers rather than case_id

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