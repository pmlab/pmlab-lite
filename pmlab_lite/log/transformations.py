from pmlab_lite.log import EventLog
from ..manipulable import Filter


class EventLogFilters(Filter):
    def __init__(self, log: EventLog):
        self.log = log


class FilterPerAttribute(EventLogFilters):
    def __call__(self, name: str, value) -> EventLog:
        f = EventLog()
        for e in self.log:
            if isinstance(value, list):
                if e[name] in value:
                    f.add_event(e)
            else:
                if e[name] is value:
                    f.add_event(e)
        self.log = f
        return self.log


class ProjectActivities(EventLogFilters):
    def __call__(self, activities_to_keep) -> EventLog:
        f = EventLog()
        for e in self.log:
            if e.get_activity_name() in activities_to_keep:
                f.add_event(e)
        self.log = f
        return self.log


class TracesStartingWith(EventLogFilters):
    def __call__(self, starting_activity) -> EventLog:
        f = EventLog()
        for t in self.log.get_traces():
            if t[0].get_activity_name() is starting_activity :
                for e in t:
                    f.add_event(e)
        self.log = f
        return self.log


class TracesEndingWith(EventLogFilters):
    def __call__(self, ending_activity) -> EventLog:
        f = EventLog()
        for t in self.log.get_traces():
            if t[-1].get_activity_name() is ending_activity :
                for e in t:
                    f.add_event(e)
        self.log = f
        return self.log


class TracesWithDirectFollowing(EventLogFilters):
    def __call__(self, first_activity, second_activity) -> EventLog:
        f = EventLog()
        for t in self.log.get_traces():
            contains_df = False
            for e1, e2 in zip(t[:-1], t[1:]):
                if e1.get_activity_name() is first_activity and e2.get_activity_name() is second_activity:
                    contains_df = True
                    break
            if contains_df:
                for e in t:
                    f.add_event(e)
        self.log = f
        return self.log
