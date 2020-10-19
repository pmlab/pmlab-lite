import unittest

from pmlab_lite.helper.graph import Graph
import pmlab_lite.log as eLog

class TestGraphMethods(unittest.TestCase):

	def test_from_log(self):

		log = eLog.EventLog()
		log.add_trace(1, ['A', 'B', 'C', 'E'])
		log.add_trace(2, ['A', 'B', 'D', 'E'])

		g = Graph()

		g.from_event_log(log)

		solution = {'A': ['B'],
					'B': ['C', 'D'],
					'C': ['E'],
					'D': ['E'],
					'E': []}

		for k, v in g.graph.items():
			self.assertListEqual(sorted(v), sorted(solution[k]))

	def test_find_scc(self):

		g = Graph()
		g.add_edge('a', 'b')
		g.add_edge('b', 'c')
		g.add_edge('c', 'd')
		g.add_edge('d', 'b')
		g.add_edge('c', 'e')
		g.add_edge('e', 'f')
		g.add_edge('f', 'g')
		g.add_edge('g', 'h')
		g.add_edge('h', 'f')
		g.add_edge('g', 'i')
		g.add_edge('i', 'j')
		g.add_edge('j', 'i')
		g.add_edge('j', 'k')
		g.add_edge('k', 'l')


		# -----

		solution = [['a'], ['b','c','d'], ['e'], ['f','g','h'], ['i','j'],
					['k'], ['l']]


		c = g.get_scc()

		
		self.assertEqual(len(c), len(solution))

		for comp1 in c:
			exisits = False
			for comp2 in solution:
				if sorted(comp1) == sorted(comp2):
					exisits = True
			self.assertTrue(exisits)