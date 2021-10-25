"""This file is used to test changes, new functions, dependencies etc."""
from itertools import islice
from random import randint
from pmlab_lite.helper.io.xes import import_xes


NAME = 'concept:name'
TIME = 'time:timestamp'

# create a function that injects noise into a certain log
# variables
# max_length_of_event_sets: to cope with combinatorial complexity this should ideally be 3; 4 at max
# max_uncertain_event_sets_per_trace: should be something like 2 or 3 at max
# positions_excluded: e.g. not starting on the first event or ending in the last event of a trace


def create_event_set_length(trace_length: int, max_n_uncertain_event_sets: int, max_length_of_event_set: int) -> list:
    """
    Creates a list of integers, which resemble the length of the events sets of a trace.

    This is used for a nosifying a trace. E.g. t = ['A', 'B', 'C', 'D'] the trace length is 4. Given the parameters the
    function could return the list [1, 2, 1] stating the first event to be of size 1, the second to be of size 2 and the
    last event set to be of size 1 again. This would imply the noisy trace to be: [['A'], ['B', 'C'], ['D']].

    Args:
        trace_length: the length of the trace
        max_n_uncertain_event_sets: the maximum number of uncertain event sets to appear in the noisified trace
        max_length_of_event_set: the maximum size of an event to have

    Returns:
        A list with the length' of the event sets for a trace to be noisified.
    """

    event_set_length = []
    n_total_uncertain_event_sets = randint(0, max_n_uncertain_event_sets)
    n_uncertain_event_sets = 0
    while True:

        # if there have been enough uncertain event sets all the next events set are certain
        if n_uncertain_event_sets == n_total_uncertain_event_sets:
            event_set_len = 1
        else:
            event_set_len = randint(1, max_length_of_event_set)

        # if the sum of all the event sets is or exceeds the length of the trace, shorten the last event set and break
        if sum(event_set_length) + event_set_len >= trace_length:
            event_set_len -= ((sum(event_set_length)
                              + event_set_len) - trace_length)
            event_set_length.append(event_set_len)
            break

        event_set_length.append(event_set_len)

        # an uncertain event set was added
        if event_set_len > 1:
            n_uncertain_event_sets += 1

    return event_set_length


def noisify_trace(trace: list, max_n_uncertain_event_sets: int, max_length_of_event_set: int) -> list:
    """
        Create a noisy trace from a certain trace.

        E.g. the trace ['A', 'B', 'C', 'D'] could turn into [['A'], ['B', 'C'], ['D']], meaning the activities 'B' and
        'C' are now uncertain for the noisy trace, i.e. there is no information in which order they have been executed.

        Args:
            trace: a list of activities that resemble a trace
            max_n_uncertain_event_sets: the maximum number of uncertain event sets to appear in the noisified trace
            max_length_of_event_set: the maximum size of an event to have

        Returns:
            The noisified trace, which now contains event sets.
        """

    event_set_length = create_event_set_length(
        len(trace), max_n_uncertain_event_sets, max_length_of_event_set)

    iter_trace = iter(trace)
    noisy_trace = [list(islice(iter_trace, length))
                   for length in event_set_length]

    return noisy_trace


max_n_uncertain_event_set = 1
max_length_of_event_set = 3

trace = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']
noisy_trace = noisify_trace(
    trace, max_n_uncertain_event_set, max_length_of_event_set)

print('Initial trace:', trace)
print('The noisified trace is:', noisy_trace)
print()

# A1 = './xes_certification/XES_certification_import_logs/Artificial/LevelA1.xes'
# D1 = './xes_certification/XES_certification_import_logs/Artificial/LevelD1.xes'
# event_log = import_xes(D1)
# traces = event_log.get_traces()
#
# trace = traces[0]
# noisy_trace = trace.copy()
#
# for i in range(len(trace)):
#     print(trace[i][NAME], '    ', trace[i][TIME], '\n')
#
# noisy_trace[1][TIME] = noisy_trace[0][TIME]
# noisy_trace[2][TIME] = noisy_trace[0][TIME]
# print()
#
# for i in range(len(noisy_trace)):
#     print(noisy_trace[i][NAME], '    ', noisy_trace[i][TIME], '\n')
