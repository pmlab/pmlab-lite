import unittest
from pmlab_lite.pn import PetriNet, TraceNet, SynchronousProduct
from pmlab_lite.alignments.a_star import A_Star


class TestAStarMethods(unittest.TestCase):

  def test_multiple_optimal_alignments(self):
    net = PetriNet()
    for i in range(1,5):
      net.add_place(i)
    transitions = ['A', 'B', 'C', 'D']
    for t in transitions:
      net.add_transition(t)
    edges = [(1,-1), (1,-2), (-1,2), (-2,2), (2,-3), (-3,3), (3,-4), (-4,4)]
    for e in edges:
      net.add_edge(e[0], e[1])

    trace = ['C']
    trace_net = TraceNet(trace)

    sync_prod = SynchronousProduct(net, trace_net)

    ilp_searcher = A_Star(sync_prod, trace, heuristic='ilp', n_alignments=2)
    ilp_searcher.search()

    # ----------------------------------
    self.assertTrue(len(ilp_searcher.alignments) == 2)
    self.assertTrue([('B', '>>'), ('C', 'C'), ('D', '>>')] in ilp_searcher.alignment_moves)
    self.assertTrue([('A', '>>'), ('C', 'C'), ('D', '>>')] in ilp_searcher.alignment_moves)
