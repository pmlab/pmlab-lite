from unittest import TestCase

from pmlab_lite.discovery.inductive_miner import InductiveMiner
from pmlab_lite.discovery.process_tree import ProcessTree
from pmlab_lite.helper.graph import Graph
from pmlab_lite.helper.viz import dot
from pmlab_lite.log import EventLog


class TestProcessTree(TestCase):

	def test_find_seq(self):
		log = [['a', 'x', 'b', 'c'],
			   ['a', 'x', 'c', 'b'],
			   ['a', 'x', 'd', 'e'],
			   ['a', 'x', 'd', 'e', 'f', 'd', 'e']]

		tree = ProcessTree(InductiveMiner(EventLog()), log, discover=False)

		split = tree.find_seq()
		self.assertListEqual(split, [['a', 'x']])
		self.fail()

	def test_find__max_seq(self):
		log = [['a', 'x', 'b', 'c'],
			   ['a', 'x', 'c', 'b'],
			   ['a', 'x', 'd', 'e'],
			   ['a', 'x', 'd', 'e', 'f', 'd', 'e']]

		tree = ProcessTree(InductiveMiner(EventLog()), log, discover=False)

		split = tree.find_seq()
		list(map(lambda sub: sub.sort(), split))
		for ele in split:
			for sub in ele:
				if isinstance(sub, list):
					sub.sort()
		# split.sort()
		self.assertListEqual(split, [['a'], ['x'], [['b', 'c'], ['d', 'e',
																 'f']]])


	def test_find_para(self):
		log = [['a', 'b'],
			   ['a', 'b'],
			   ['b', 'a']]

		# log = [['supervisor signature',  # i
		# 		'sign application'],  # j
		# 		['sign application',  # j
		# 		'supervisor signature']]  # i

		tree = ProcessTree(InductiveMiner(EventLog()), log, discover=False)

		split = tree.find_para()
		split.sort()
		print(split)
		self.assertListEqual(split, [['a'], ['b']])


	def test_find_excl(self):
		log = [['b', 'c'],
			   ['c', 'b'],
			   ['d', 'e'],
			   ['d' , 'e', 'f', 'd', 'e']]

		tree = ProcessTree(InductiveMiner(EventLog()), log, discover=False)

		split = tree.find_excl()
		list(map(lambda  sub: sub.sort(), split))
		split.sort()
		self.assertListEqual(split, [['b', 'c'], ['d', 'e', 'f']])

	def test_find_loop(self):
		log = [['d', 'e'],
			   ['d', 'e', 'f', 'g', 'd', 'e']]

		tree = ProcessTree(InductiveMiner(EventLog()), log, discover=False)

		split = tree.find_loop()
		list(map(lambda sub: sub.sort(), split))
		print(split)
		self.assertListEqual(split, [['d', 'e'], ['f', 'g']])


	def test_find_cuts(self):
		log4 = [['a', 'b', 'g', 'h', 'i', 'j', 'k'],
				['a', 'b', 'g', 'h', 'j', 'i', 'k'],
				['a', 'b', 'g', 'h', 'i', 'k'],
				['a', 'b', 'g', 'h', 'j', 'k'],
				['a', 'b', 'c', 'd', 'e', 'h', 'i', 'k'],
				['a', 'b', 'c', 'd', 'e', 'f', 'c', 'd', 'e', 'h', 'i', 'k']]

		log2 = [['a', 'b', 'c'],
				['a', 'c', 'b'],
				['a', 'd', 'e'],
				['a', 'd', 'e', 'f', 'd', 'e']]

		miner = InductiveMiner(EventLog())
		tree = ProcessTree(miner, log2)
		print()
		tree.print_tree()

		dot.draw_process_tree(tree)

	def test_scc(self):
		log = [['g'],
			   ['c', 'd', 'e'],
			   ['c', 'd', 'e', 'f', 'c', 'd', 'e']]

		g = Graph()

		g = g.from_log(log)

		print(g.start_nodes)
		print(g.vertexes)
