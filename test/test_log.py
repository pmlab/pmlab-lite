import unittest
from pmlab_lite.helper.io import xes
from pprint import pprint

a_names = ['FlagX1.xes', 'FlagX2.xes', 'LevelA1.xes', 'LevelA2.xes', 'LevelB1.xes', 'LevelB2.xes',
           'LevelC1.xes', 'LevelC2.xes', 'LevelD1.xes', 'LevelD2.xes']

rl_names = ['BPIC12.xes', 'BPIC13_closed_problems.xes', 'BPIC13_incidents.xes', 'BPIC13_open_problems.xes',
            'BPIC15_1.xes', 'BPIC15_2.xes', 'BPIC15_3.xes', 'BPIC15_4.xes', 'BPIC15_5.xes', 'BPIC17.xes', 'BPIC17_Offer_log.xes']

a_path = '../XES_Certification/Artificial/'
rl_path = '../XES_Certification/Real-life/'

a_log = a_path + a_names[2]
rl_log = rl_path + rl_names[-2]

# new import
new_log = xes.import_xes(rl_log)

# pm4py log
from pm4py.objects.log.importer.xes import importer as xes_importer

#test_log = xes_importer.apply(a_log, variant=xes_importer.Variants.ITERPARSE)

# compare extensions --> success
""" print()
pprint(log.extensions)
print()
pprint(new_log.extensions)
print("Extensions are the same:", log.extensions==new_log.extensions)
print()
pprint(test_log.extensions)
print() """

# compare globals --> success
""" print()
pprint(log.globals)
print()
pprint(new_log.globals)
print("Globals are the same:", log.globals==new_log.globals)
print()
pprint(test_log.omni_present)
print() """

# compare classifiers --> success
""" print()
pprint(log.classifiers)
print()
pprint(new_log.classifiers)
print("Classifiers are the same:", log.classifiers==new_log.classifiers)
print()
pprint(test_log.classifiers)
print() """


# compare log attributes --> success
""" print()
pprint(log.attributes)
print()
pprint(new_log.attributes)
print("Log attributes are the same:", log.attributes==new_log.attributes)
print()
pprint(test_log.attributes)
print() """

# compare traces --> succes but former case_id, which was equivalent to the concept:name of a trace, is no a count from 0 to num_traces
""" traces = log.traces
new_traces = new_log.traces
for i, trace_id in enumerate(traces):

    new_traces[trace_id] = new_traces.pop(i+1)
    new_traces[trace_id]['concept:name'] = trace_id

    for event in new_traces[trace_id]['events']:
        event['case:id'] = trace_id

    if i == 1:
        pprint(traces[trace_id])
        print()
        pprint(new_traces[trace_id])

print("Events of traces are equal:", traces==new_traces, "(besides case:id)") """

#compare events --> success
""" events = log.events
pprint(log.events[:3])
print()
new_events = new_log.events
pprint(new_log.events[:3])

for event in events:
    del event['case:id']
for event in new_events:
    del event['case:id']

print("Events are the are equal:", events == new_events, "(besides case_id)") """


# test exporting
#xes.export_to_xes(new_log, 'X2.xes')
pprint(new_log.events[9])
print()
for val in new_log.events[9].values():
    print(val, type(val))
# print(new_log.events[9]['Accepted'], type(new_log.events[10]['Accepted']))
# print(new_log.events[9]['CreditScore'], type(new_log.events[10]['CreditScore']))
# print(new_log.events[9]['MonthlyCost'], type(new_log.events[10]['MonthlyCost']))
# print(new_log.events[9]['OfferedAmount'], type(new_log.events[10]['OfferedAmount']))
