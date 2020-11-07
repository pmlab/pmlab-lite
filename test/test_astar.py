import unittest
from pmlab_lite.pn import PetriNet, TraceNet, SynchronousProduct
from pmlab_lite.alignments import a_star
from pmlab_lite.helper.viz.dot import draw_synchronous_product, draw_a_star_search_space

#create running example
running_example = PetriNet()
transitions = ['As', 'Aa', 'Da1', 'Fa', 'Sso', 'Ro', 'Co', 'tau', 'Ao', 'Do', 'Aaa', 'Da2', 'Af']
edges = [(1,-1), (-1,2), (2,-3), (2,-2), (-3,11), (-2,3), (-2,5), (3,-4), (-4,4), (4,-8), (5,-5), (-5,6), (6,-6), (-6,7), (7,-7), (-7,5), (7,-8),
         (-8,8), (8,-9), (-9,9), (9,-11), (-11,11), (8,-10), (-10,10), (10,-12), (-12,11), (11,-13), (-13,12)]

for p in range(1,13):
  running_example.add_place(p)
for t in transitions:
  running_example.add_transition(t)
for e in edges:
  running_example.add_edge(e[0], e[1])

#first example
#create trace net
trace1 = ['As', 'Aa', 'Sso', 'Ro', 'Ao', 'Aaa', 'Aaa']
trace_net1 = TraceNet(trace1)

#create synchronous product
sp1 = SynchronousProduct(running_example, trace_net1)


a = a_star.A_Star(sp1, trace1, heuristic='lp')
a.search()
a.print_alignment()


#second example
#create trace net
trace2 = ['As', 'Aa', 'Fa', 'Aaa', 'Ao', 'Af']
trace_net2 = TraceNet(trace2)

#create synchronous product
sp2 = SynchronousProduct(running_example, trace_net2)


b = a_star.A_Star(sp2, trace2, heuristic='lp', alignments=2)
b.search()
print()
b.print_alignment()

#draw_a_star_search_space(b)
#draw_synchronous_product(sp2)