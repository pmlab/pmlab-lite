import unittest
from pmlab_lite.pn import PetriNet


class TestPetriNetMethods(unittest.TestCase):

	def test_is_enabled(self):
		net = PetriNet()
		net.add_transition('A')
		net.add_place(1).add_place(2).add_place(3)
		net.add_edge(1, -1).add_edge(-1, 3).add_edge(2, -1)

		# ----------------------------------
		self.assertFalse(net.is_enabled(-1))

		net.add_marking(1)
		self.assertFalse(net.is_enabled(-1))

		net.add_marking(2)
		self.assertTrue(net.is_enabled(-1))

	def test_all_enabled_transitions(self):
		net = PetriNet()
		net.add_transition('A').add_transition('B')
		net.add_place(1).add_place(2).add_place(3).add_place(4)
		net.add_edge(1, -1).add_edge(-1, 3).add_edge(2, -1) \
			.add_edge(3, -2).add_edge(-2, 4)

		# ----------------------------------
		net.add_marking(1).add_marking(2)

		transitions = net.all_enabled_transitions()
		self.assertListEqual(transitions, [-1])

	def test_fire_transition(self):
		net = PetriNet()
		net.add_transition('A').add_transition('B')
		net.add_place(1).add_place(2).add_place(3).add_place(4)
		net.add_edge(1, -1).add_edge(-1, 3).add_edge(2, -1) \
			.add_edge(3, -2).add_edge(-2, 4)

		net.add_marking(1).add_marking(2)

		# ----------------------------------
		net.fire_transition(-1)
		transitions = net.all_enabled_transitions()
		self.assertListEqual(transitions, [-2])

	def test_add_place_df_pn(self):
		dpn = PetriNet()
		dpn.add_place(1)
		dpn.add_place(2, 3)

		# ----------------------------------
		self.assertDictEqual(dpn.places, {0: 1, 1: 2})
		self.assertListEqual(dpn.marking, [0, 0])
		self.assertListEqual(dpn.capacity, [1, 3])

	def test_remove_place_df_pn(self):
		dpn = PetriNet()
		dpn.add_place(1)
		dpn.add_place(2)
		dpn.add_place(3)

		dpn.add_marking(3)

		# ----------------------------------
		dpn.remove_place(2)
		self.assertDictEqual(dpn.places, {0: 1, 1: 3})
		self.assertListEqual(dpn.marking, [0, 1])
		self.assertListEqual(dpn.capacity, [1, 1])

		dpn.remove_place(3)
		self.assertDictEqual(dpn.places, {0: 1})
		self.assertListEqual(dpn.marking, [0])
		self.assertListEqual(dpn.capacity, [1])

	def test_add_transition_df_pn(self):
		dpn = PetriNet()
		dpn.add_transition('A')
		dpn.add_transition('B')
		dpn.add_transition('A')

		self.assertDictEqual(dpn.transitions, {'A': [-1, -3], 'B': [-2]})

	def test_remove_transition_df_pn(self):
		dpn = PetriNet()
		dpn.add_transition('A')
		dpn.add_transition('B')
		dpn.add_transition('C')
		dpn.add_transition('A')

		# ----------------------------------
		dpn.remove_transition(-2)
		dpn.remove_transition(-1)

		self.assertDictEqual(dpn.transitions, {'A': [-4], 'C': [-3]})

	def test_add_edge_df_pn(self):
		dpn = PetriNet()
		dpn.add_transition('A')

		dpn.add_place(1)
		dpn.add_place(2)

		# ----------------------------------
		dpn.add_edge(1, -1, True)

		self.assertEqual(dpn.edges,
						 [(1, -1), (-1, 1)])

	def test_remove_edge_df_pn(self):
		dpn = PetriNet()
		dpn.add_transition('A')

		dpn.add_place(1)
		dpn.add_place(2)

		dpn.add_edge(1, -1, True)
		dpn.add_edge(-1, 2)

		# ----------------------------------
		dpn.remove_edge(-1, 1)

		self.assertEqual(dpn.edges, [(1, -1), (-1, 2)])

	def test_remove_all_edges_of_df_pn(self):
		dpn = PetriNet()
		dpn.add_transition('A')
		dpn.add_transition('B')

		dpn.add_place(1)
		dpn.add_place(2)

		dpn.add_edge(1, -1, True)
		dpn.add_edge(-1, 2)
		dpn.add_edge(1, -2)

		# ----------------------------------
		dpn.remove_all_edges_of(-1)

		self.assertEqual(dpn.edges, [(1, -2)])

	def test_add_marking_df_pn(self):
		dpn = PetriNet()

		dpn.add_place(1)
		dpn.add_place(2)
		dpn.add_place(3)

		# ----------------------------------
		dpn.add_marking(3)

		self.assertListEqual(dpn.marking, [0, 0, 1])

	def test_replay_df_pn(self):
		dpn = PetriNet()
		dpn.add_transition('A')
		dpn.add_transition('B')
		dpn.add_transition('C')

		dpn.add_place(1)
		dpn.add_place(2)
		dpn.add_place(3)

		dpn.add_edge(1, -1)
		dpn.add_edge(-1, 2)

		dpn.add_edge(1, -3)
		dpn.add_edge(-3, 3)

		# dpn.add_edge(1, -2)  # deadlock
		dpn.add_edge(2, -2)
		# dpn.add_edge(3, -2)
		dpn.add_edge(-2, 3)

		dpn.add_marking(1)
		# dpn.add_marking(2, 2)
		# dpn.add_marking(3, 2)

		# start replay
		dpn.replay(5)
		self.assertListEqual(dpn.marking, [0, 0, 1])

	# dpn.fire_transition('B')

	def test_chain_operations_df_pn(self):
		dpn = PetriNet()

		dpn.add_place(1) \
			.add_place(2) \
			.add_place(3) \
			.add_transition('A') \
			.add_transition('B') \
			.add_edge(1, -1) \
			.add_edge(-1, 2) \
			.add_edge(1, -2) \
			.add_edge(-2, 2) \
			.add_transition('C') \
			.add_transition('A') \
			.add_marking(1, 2) \
			.remove_place(3) \
			.add_edge(1, -3) \
			.remove_edge(1, -3) \
			.remove_transition(-3)

		self.assertDictEqual(dpn.places, {0: 1, 1: 2})
		self.assertDictEqual(dpn.transitions, {'A': [-1, -4], 'B': [-2]})
		self.assertListEqual(dpn.marking, [2, 0])

	def test_place_capacity(self):
		net = PetriNet()
		for i in range(1,4):
			net.add_place(i)
		net.add_transition('A')
		net.add_transition('B')
		net.add_edge(1,-1)
		net.add_edge(-1,2)
		net.add_edge(-1,3)
		net.add_edge(2,-2)

		net.add_marking(1,1)
		net.add_marking(2,4)

		net.fire_transition(-1)

		print(net.get_exceeded_places())
		net.fire_transition(-2)
		net.fire_transition(-2)
		net.fire_transition(-2)
		net.fire_transition(-2)
		print(net.get_exceeded_places())
