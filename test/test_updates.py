from pprint import pprint
from pmlab_lite.helper.io import xes, pnml
from pmlab_lite.pn import PetriNet, TraceNet, SynchronousProduct
from pmlab_lite.alignments.a_star import A_Star

log_file = '../conf_tutorial/financial_log.xes'
log = xes.import_xes(log_file)

print('Load log with %s traces.' % len(log.traces))

trace_variants = {}
for trace in log.get_traces():
    events = []
    for event in trace:
        events.append(event['concept:name'])
    trace_variants[tuple(events)] = trace_variants.get(tuple(events), 0) + 1

# print the two most frequent variants
trace_variants_sorted_by_freq = sorted(trace_variants.items(),
                                       key=lambda kv: kv[1], reverse=True)
pprint(trace_variants_sorted_by_freq[:2])
print()

net = PetriNet()
pnml.load(net, "../conf_tutorial/financial_log_80_noise.pnml")

# mark the initial place
net.add_marking(1, 1)

# make sure to assign unique labels to silent transitions
t_transitions = dict()
for t in net.transitions['tau']:
    net.transitions['tau' + str(t)] = [t]
net.transitions.pop('tau', None)

# select some most frequent traces
traces = dict()
for k in range(10):
    traces[k] = list(trace_variants_sorted_by_freq[k][0])


trace_net = TraceNet(traces[0])
synchronous_product = SynchronousProduct(net, trace_net)

alignments = {}
for i in range(3):
    trace = traces[i]
    print('Trace in the log:\n', trace)
    print('Optimal Alignment: ')
    trace_model = TraceNet(trace)
    sp = SynchronousProduct(net, trace_model)
    a = A_Star(sp, trace, heuristic='tl')    # insert heuristic='lp' as well
    a.search()
    a.print_alignment()  # print(a.alignment_moves)
    alignments[i] = a.alignment_moves
    print('\n')
