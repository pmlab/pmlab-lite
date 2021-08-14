"""This file is used to test changes, new functions, dependencies etc."""
from pprint import pprint
from pmlab_lite.pn import PetriNet, TraceNet, SynchronousProduct
from pmlab_lite.helper.io import pnml
from pmlab_lite.alignments.a_star import A_Star


running_example = PetriNet()
pnml.load(running_example, '../conf_tutorial/running_example.pnml')

trace = ['As', 'Aa', 'Sso', 'Ro', 'Ao', 'Aaa', 'Aaa']
trace = ['As', 'Aa', 'Ao', 'Aaa', 'Af']
trace_net = TraceNet(trace)

sp = SynchronousProduct(running_example, trace_net)


ilp_searcher1 = A_Star(sp, trace, heuristic='ilp', n_alignments=1)
ilp_searcher1.search()

print('Optimal Alignments found using the ilp heuristic:')
ilp_searcher1.print_alignments()

for i in range(len(ilp_searcher1.alignments)):
    print('Alignment 1 cost: ', round(ilp_searcher1.alignments[i].total_cost, 2))
print()

print()
print(len(ilp_searcher1.alignments))


trace = ['As', 'Aa', 'Fa', 'Do', 'Da', 'Af']

# assign a cost of 0.2 (instead of 1) to Aa and Fa
# compute optimal alignments with these updated costs
