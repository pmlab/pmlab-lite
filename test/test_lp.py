import unittest
from pmlab_lite.pn import PetriNet, TraceNet, SynchronousProduct
from pmlab_lite.alignments import a_star
from pmlab_lite.helper.viz.dot import draw_petri_net, draw_synchronous_product, draw_a_star_search_space
import numpy as np
from numpy.linalg import lstsq, matrix_rank
from cvxopt import matrix, solvers

net = PetriNet()
transitions = ['A', 'B']
edges = [(1,-1), (-1,2), (2,-2), (-2,3)]
for p in range(1,4):
    net.add_place(p)
for t in transitions:
    net.add_transition(t)
for e in edges:
    net.add_edge(e[0], e[1])

trace = ['A', 'B']
trace_net = TraceNet(trace)

sp = SynchronousProduct(net, trace_net)
im = sp.incidence_matrix()
imv = sp.get_init_marking()
fmv = sp.get_final_marking()

b = fmv - imv
x = np.linalg.lstsq(im, b, rcond=None)[0]
#print(x)
#x[x > 0] = 1
#x[x <= 0] = 0
trans_to_idx = sp.transitions_by_index()
for key in trans_to_idx:
    if trans_to_idx[key].startswith('tau') or trans_to_idx[key].endswith('synchronous'):
        x[key] = 0

# print(np.argmax(x))
# print(np.argwhere(x == x.max()).flatten().tolist())

#draw_petri_net(net, filename='../lp_net')
#draw_petri_net(trace_net, filename='../trace_net')
#draw_synchronous_product(synchronous_product, filename='../synchronous_product')

print("Incidence matrix:")
print(im)
print("Final marking  :",fmv)
print("Current marking:",imv)
print("Solution       :",x)
print("Solutions cost :",x.sum())
print("Optimal cost would be:", 0.0)
print("--> overestimating the total cost:", x.sum()>0.0)
print()

# computing solution when all "redundant" columns in the incedence marix are left out
# here this means transition0 and transition2 are covered by transition 4 (similar for 1,3 covered by 5)
im2 = im[:, 4:]
x2 = np.linalg.lstsq(im2, b, rcond=None)[0]
print("Incidence matrix:")
print(im2)
print("Solution       :",x2)
print("Solutions cost :",x2.sum()*0.0) # pretending to have remembered which index was a synchronous move in the new inc-mat and thus aranging costs
print("Optimal cost would be:", 0.0)
print("--> overestimating the total cost:", False)

# formulate as linear program for cvxopt
# N = sp.num_transitions()
# d = net.num_transitions() + trace_net.num_transitions()
#
# # minimization term
# c = np.zeros((N,1))
# #c[[idx for idx in range(d)]] = 1.0
# c = matrix(c)
#
# # inequality constraints
# G = matrix(-np.eye(N))
# h = matrix(np.zeros(N))
#
# # equality constraints
# A = matrix(im[:,:4]*1.0)
# b = matrix((fmv-imv)*1.0)
#print(A)
#print("Rank of A:", matrix_rank(A), "\n And number of rows:", A.size[0])
#sol = solvers.lp(c, G, h, A, b)

# formulate as an cvxopt quadratic problem
# N = sp.num_transitions()
# d = net.num_transitions() + trace_net.num_transitions()
#
#
# P = matrix(np.zeros((N,N)))
#
# q = np.zeros((N,1))
# q[ [idx for idx in range(d)] ] = 1.0
# q = matrix(q)
#
# G = matrix(-np.eye(N))
# h = matrix(np.zeros(N))
# A = matrix((im*1.0))
# b = matrix((fmv - imv)*1.0)
#
# sol = solvers.qp(P, q, G, h, A, b)
#
# print(P)
# print(q)
# print(G)
# print(h)
# print(A)
# print(b)
# print("CVXOPT quadratic programm solution:",sol['x'])
