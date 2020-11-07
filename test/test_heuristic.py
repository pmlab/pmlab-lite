import unittest
from pmlab_lite.pn import PetriNet, TraceNet, SynchronousProduct
from pmlab_lite.helper.viz import dot

import numpy as np
from scipy.optimize import minimize


edges = [(1,-1), (-1,2), (-1,3), (2,-2), (2,-5), (3,-2), (3,-6), (-2,4), (-2,5), (5,-5), (5,-6), (-5,1), (-6,1), (4,-3), (4,-4), (-3,2), (-4,3)]
#create example
net = PetriNet()
for i in range(1,6):
    net.add_place(i)
for c in '123456':
    net.add_transition(c)
for e in edges:
    net.add_edge(e[0], e[1])
net.add_marking(1)
dot.draw_petri_net(net)
net.get_marking()


def fit(X, params):
    return X.dot(params)

def cost_function(params, X, num_nonsync_moves: int):
    result = None
    for i in range(num_nonsync_moves):
        result += X[i]
    for i in range(num_nonsync_moves, len(X.shape[0])):
        result += X[i]
    return result