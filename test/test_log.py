import unittest
from pmlab_lite.helper.io import xes

a_names = ['FlagX1.xes', 'FlagX2.xes', 'LevelA1.xes', 'LevelA2.xes', 'LevelB1.xes', 'LevelB2.xes', 
           'LevelC1.xes', 'LevelC2.xes', 'LevelD1.xes', 'LevelD2.xes'] 

rl_names = ['BPIC12.xes', 'BPIC13_closed_problems.xes', 'BPIC13_incidents.xes', 'BPIC13_open_problems.xes', 
            'BPIC15_1.xes', 'BPIC15_2.xes', 'BPIC15_3.xes', 'BPIC15_4.xes', 'BPIC15_5.xes', 'BPIC17.xes', 'BPIC17_Offer_log.xes']

a_path = '../XES_Certification/Artificial/'
rl_path = '../XES_Certification/Real-life/'

a_log = a_path + a_names[2]
rl_log = rl_path + rl_names[0]

log = xes.import_from_xes(a_log)

print("Number of traces:", len(log.traces))
print("Number of events:", len(log.events))
print("Classifiers:", log.classifiers)
print()
print(log.events [2])
print()
for i, id in enumerate(log.traces):
    print(i, log.traces[id])
    if i > 0:
        break

xes.export_to_xes(log, 'test_log.xes')

#test classifier in pm4py
""" from pm4py.objects.log.importer.xes import importer as xes_importer

test_log = xes_importer.apply(a_log)
test_log2 = xes_importer.apply(a_path + a_names[5])
print("Number of traces:", len(test_log))
print("Classifiers:", test_log.classifiers)
print()
print(test_log[0][0]) """