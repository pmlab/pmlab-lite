import unittest
from pmlab_lite.helper.io import xes

log = xes.import_from_xes('../logs/Sepsis_Log.xes')
#log.print_log()

print("Number of traces:", log.len)
print("Number of events:", log.num_events)

log.print_traces()