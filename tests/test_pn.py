import unittest
import pmlab_lite.pn as pn


class TestPetriNetMethods(unittest.TestCase):

	def test_add_place_df_pn(self):
		dpn = pn.PetriNet()
		dpn.add_place(1)
		dpn.add_place(2)

		self.assertEqual(dpn.places,
						 [(1, 1), (2, 1)])

	def test_remove_place_df_pn(self):
		dpn = pn.PetriNet()
		dpn.add_place(1, 1)
		dpn.add_place(2, 1)
		dpn.add_place(3, 1)

		dpn.remove_place(2)

		self.assertEqual(dpn.places,
						 [(1, 1), (3, 1)])

	def test_add_transition_df_pn(self):
		dpn = pn.PetriNet()
		dpn.add_transition('A')
		dpn.add_transition('B')

		self.assertEqual(dpn.transitions,
						 ['A', 'B'])

	def test_remove_transition_df_pn(self):
		dpn = pn.PetriNet()
		dpn.add_transition('A')
		dpn.add_transition('B')
		dpn.add_transition('C')

		dpn.remove_transition('B')

		self.assertEqual(dpn.transitions,
						 ['A', 'C'])

	def test_add_edge_df_pn(self):
		dpn = pn.PetriNet()
		dpn.add_transition('A')

		dpn.add_place(1)
		dpn.add_place(2)

		dpn.add_edge(1, 'A', True)

		self.assertEqual(dpn.edges,
						 [(1, 'A'), ('A', 1)])

	def test_remove_edge_df_pn(self):
		dpn = pn.PetriNet()
		dpn.add_transition('A')

		dpn.add_place(1)
		dpn.add_place(2)

		dpn.add_edge(1, 'A', True)
		dpn.add_edge('A', 2)

		dpn.remove_edge('A', 1)

		self.assertEqual(dpn.edges,
						 [(1, 'A'), ('A', 2)])

	def test_remove_all_edges_of_df_pn(self):
		dpn = pn.PetriNet()
		dpn.add_transition('A')
		dpn.add_transition('B')

		dpn.add_place(1)
		dpn.add_place(2)

		dpn.add_edge(1, 'A', True)
		dpn.add_edge('A', 2)
		dpn.add_edge(1, 'B')

		dpn.remove_all_edges_of('A')

		self.assertEqual(dpn.edges,
						 [(1, 'B')])

	def test_add_marking_df_pn(self):
		dpn = pn.PetriNet()
		dpn.add_transition('A')
		dpn.add_transition('B')

		dpn.add_place(1)
		dpn.add_place(2)

		dpn.add_edge(1, 'A', True)
		dpn.add_edge('A', 2)
		dpn.add_edge(1, 'B')

		dpn.add_marking(1)
		dpn.add_marking(2, 3)

		self.assertEqual(dpn.marking,
						 {1: 1, 2: 3})

	def test_is_enabled(self):
		dpn = pn.PetriNet()
		dpn.add_transition('A')
		dpn.add_transition('B')

		dpn.add_place(1)
		dpn.add_place(2)

		dpn.add_edge(1, 'A', True)
		# dpn.add_edge(2, 'A')
		dpn.add_edge('A', 2)
		dpn.add_edge(1, 'B')

		dpn.add_marking(1)
		dpn.add_marking(2)

		self.assertTrue(dpn.is_enabled('A'))

	def test_replay_df_pn(self):
		dpn = pn.PetriNet()
		dpn.add_transition('A')
		dpn.add_transition('B')
		dpn.add_transition('C')

		dpn.add_place(1)
		dpn.add_place(2)
		dpn.add_place(3)

		dpn.add_edge(1, 'A')
		dpn.add_edge('A', 2)

		dpn.add_edge(1, 'C')
		dpn.add_edge('C', 3)

		# dpn.add_edge(1, 'B')  # deadlock
		dpn.add_edge(2, 'B')
		# dpn.add_edge(3, 'B')
		dpn.add_edge('B', 3)

		dpn.add_marking(1, 1)
		# dpn.add_marking(2, 2)
		# dpn.add_marking(3, 2)

		# start replay
		dpn.replay()
		self.assertEqual(dpn.marking,
						 {3: 1})

	# dpn.fire_transition('B')

	def test_chain_operations_df_pn(self):
		dpn = pn.PetriNet()

		dpn.add_place(1) \
			.add_place(2) \
			.add_place(3) \
			.add_transition('A') \
			.add_transition('B') \
			.add_edge(1, 'A') \
			.add_edge('A', 2) \
			.add_edge(1, 'B') \
			.add_edge('B', 2) \
			.add_transition('C') \
			.add_marking(1, 2) \
			.remove_place(3) \
			.add_edge(1, 'C') \
			.remove_edge(1, 'C') \
			.remove_transition('C')

		self.assertEqual(dpn.places, [(1, 1), (2, 1)])
		self.assertEqual(dpn.transitions, ['A'])
		self.assertEqual(dpn.marking, {1: 2})
