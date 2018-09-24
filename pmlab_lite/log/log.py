from pmlab_lite.manipulable import Manipulable


class Event(dict):
    """"
    An event is the minimum observable unit of information. It actually is a dictionary with, at least, two attributes:
    'activity_name' and 'case_id'.
    """
    def __init__(self, activity_name, case_id):
        self["activity_name"] = activity_name
        self["case_id"] = case_id

    def get_activity_name(self):
        return self["activity_name"]

    def get_case_id(self):
        return self["case_id"]

    def get_attributes(self):
        return self.keys()


class EventCollection(Manipulable):
    """"
    An event collection is an abstract iterable collection of events. This is the smallest collection of events
    """
    def __iter__(self):
        return self

    def __next__(self) -> Event:
        raise NotImplemented


class EventLog(EventCollection):
    """"
    An event log is a collection of events with a fixed size. It can also extend the 'Manipulable' (or whatever we call
    it) class. With this implementation, it is not possible to have trace attributes, but only events attributes.
    Direct access to single traces is also possible
    """
    def __init__(self):
        self.events = list() # events are still stored as list of events
        self.traces = dict() # traces are stored as dictionary of case id -> list of events

    def add_event(self, event: Event):
        self.events.append(event)
        if event.get_case_id() in self.traces:
            self.traces[event.get_case_id()].append(event)
        else:
            self.traces[event.get_case_id()] = [event]
        return self

    def add_trace(self, case_id, activity_names: []):
        for activity_name in activity_names:
            self.add_event(Event(activity_name, case_id))
        return self

    def get_traces(self):
        return self.traces.values()

    def get_trace(self, case_id):
        return self.traces[case_id]

    def __iter__(self):
        return self.events.__iter__()

    def __next__(self):
        return self.events.__iter__().__next__()