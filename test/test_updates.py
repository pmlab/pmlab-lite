from pmlab_lite.pn import PetriNet, TraceNet, SynchronousProduct

net = PetriNet()
transitions = ['A', 'B']
edges = [(1, -1), (-1, 2), (2, -2), (-2, 3)]
for p in range(1, 4):
    net.add_place(p)
for t in transitions:
    net.add_transition(t)
for e in edges:
    net.add_edge(e[0], e[1])

trace = ['A', 'B']
trace_net = TraceNet(trace)

sp = SynchronousProduct(net, trace_net)
print(sp)
print("Success")
