import pprint
import unittest

from pmlab_lite.discovery.cut import Cut
from pmlab_lite.helper.graph import Graph
from pmlab_lite.discovery.inductive_miner import InductiveMiner
from pmlab_lite.helper.io.xes import import_from_xes
from pmlab_lite.helper.viz import dot
from pmlab_lite.log import EventLog


class TesInductiveMinerMethods(unittest.TestCase):


	def test_split_seq_cut(self):
		log = [['a', 'x', 'b', 'c'],
			   ['a', 'x', 'c', 'b'],
			   ['a', 'x', 'd', 'e'],
			   ['d', 'e'],
			   ['a', 'x', 'd', 'e', 'f', 'd', 'e']]

		lg = EventLog()

		miner = InductiveMiner(lg)

		ll, lr = miner.split_log([['a', 'x'], ['b', 'c', 'd', 'e', 'f']],
								 Cut.SEQ,
								log)


		self.assertListEqual(ll, [['a', 'x'], []])
		self.assertListEqual(lr, [['b', 'c'], ['c', 'b'], ['d', 'e'],
								  ['d', 'e', 'f', 'd', 'e']])


	def test_split_max_seq_cut(self):
		log = [['a', 'x', 'b', 'c'],
			   ['a', 'x', 'c', 'b'],
			   ['a', 'd', 'e'],
			   ['a', 'x', 'd', 'e', 'f', 'd', 'e']]

		miner = InductiveMiner(EventLog())

		max_seq_split = [['a'], ['x'], [['b', 'c'], ['d', 'e', 'f']]]

		logs = miner.split_log(max_seq_split, Cut.SEQ, log)
		print(logs)

	def test_split_para_cut(self):
		log = [['a', 'b'],
			   ['b', 'a'],
			   ['a']]

		miner = InductiveMiner(EventLog())

		ll, lr = miner.split_log([['a'], ['b']], Cut.PARA, log)

		self.assertListEqual(ll, [['a']])
		self.assertListEqual(lr, [['b'], []])

	def test_split_excl_cut(self):
		log = [['a', 'b'],
			   ['d', 'e', 'f', 'd','e'],
			   ['d', 'e']]

		miner = InductiveMiner(EventLog())

		ll, lr = miner.split_log([['a', 'b'], ['d', 'e', 'f']], Cut.EXCL, log)

		self.assertListEqual(ll, [['a', 'b']])
		self.assertListEqual(lr, [['d', 'e', 'f', 'd','e'],
								  ['d', 'e']])

	def test_split_loop_cut(self):
		log = [['d', 'e', 'f', 'g', 'd', 'e'],
			   ['d', 'e']]

		miner = InductiveMiner(EventLog())

		ll, lr = miner.split_log([['d', 'e'], ['f', 'g']], Cut.LOOP, log)

		self.assertListEqual(ll, [['d', 'e']])
		self.assertListEqual(lr, [['f', 'g'], []])

	def test_prepare_log(self):

		lg = EventLog()

		lg.add_trace(1, ['a', 'b', 'g', 'h', 'i', 'j', 'k'])
		lg.add_trace(2, ['a', 'b', 'g', 'h', 'j', 'i', 'k'])
		lg.add_trace(3, ['a', 'b', 'g', 'h', 'i', 'k'])
		lg.add_trace(4, ['a', 'b', 'g', 'h', 'j', 'k'])
		lg.add_trace(5, ['a', 'b', 'c', 'd', 'e', 'h', 'i', 'k'])
		lg.add_trace(6, ['a', 'b', 'c', 'd', 'e', 'f', 'c', 'd',
						 'e', 'h', 'i', 'k'])

		miner = InductiveMiner(lg)

		result = [	['a', 'b', 'g', 'h', 'i', 'j', 'k'],
					['a', 'b', 'g', 'h', 'j', 'i', 'k'],
					['a', 'b', 'g', 'h', 'i', 'k'],
					['a', 'b', 'g', 'h', 'j', 'k'],
					['a', 'b', 'c', 'd', 'e', 'h', 'i', 'k'],
					['a', 'b', 'c', 'd', 'e', 'f', 'c', 'd', 'e', 'h', 'i', 'k']]

		result.sort()
		miner.log.sort()

		self.assertListEqual(miner.log, result)

	def test_simple_example(self):
		lg = EventLog()

		lg.add_trace(1, ['a', 'b', 'g', 'h', 'i', 'j', 'k'])
		lg.add_trace(2, ['a', 'b', 'g', 'h', 'j', 'i', 'k'])
		lg.add_trace(3, ['a', 'b', 'g', 'h', 'i', 'k'])
		lg.add_trace(4, ['a', 'b', 'g', 'h', 'j', 'k'])
		lg.add_trace(5, ['a', 'b', 'c', 'd', 'e', 'h', 'i', 'k'])
		lg.add_trace(6, ['a', 'b', 'c', 'd', 'e', 'f', 'c', 'd',
						 'e', 'h', 'i', 'k'])

		miner = InductiveMiner(lg)
		tree = miner.discover()

		tree.print_tree()
		dot.draw_process_tree(tree, format='pdf')


	def test_extended_example(self):
		lg = EventLog()

		lg.add_trace(1, ['submit application',  # a
						 'review application',  # b
						 'fast forwarding',  # g
						 'final review',  # h
						 'supervisor signature',  # i
						 'sign application',  # j
						 'close application'])  # k
		lg.add_trace(2, ['submit application',  # a
						 'review application',  # b
						 'fast forwarding',  # c
						 'final review',  # h
						 'sign application',  # j
						 'supervisor signature',  # i
						 'close application'])  # k
		lg.add_trace(3, ['submit application',  # a
						 'review application',  # b
						 'fast forwarding',  # g
						 'final review',  # h
						 'supervisor signature',  # i
						 'close application'])  # k
		lg.add_trace(4, ['submit application',  # a
						 'review application',  # b
						 'fast forwarding',  # g
						 'final review',  # h
						 'sign application',  # j
						 'close application'])  # k
		lg.add_trace(5, ['submit application',  # a
						 'review application',  # b
						 'check documents',  # c
						 'check financial status',  # d
						 'write report',  # e
						 'final review',  # h
						 'supervisor signature',  # i
						 'close application'])  # k
		lg.add_trace(6, ['submit application',  # a
						 'review application',  # b
						 'check documents',  # c
						 'check financial status',  # d
						 'write report',  # e
						 'reject report',  # f
						 'check documents',  # c
						 'check financial status',  # d
						 'write report',  # e
						 'final review',  # h
						 'supervisor signature',  # i
						 'close application'])  # k

		miner = InductiveMiner(lg)
		tree = miner.discover()

		g = Graph()
		g = g.from_log(miner.log)
		d = dot.draw_graph(g)
		dot.render_dot(d, 'dfg_process_tree')

		tree.print_tree()
		dot.draw_process_tree(tree, 'example', format='pdf')

	def test_bpi_12(self):
		log = import_from_xes('BPI_Challenge_2012.xes')

		miner = InductiveMiner(log)
		tree = miner.discover()


		tree.print_tree()
		dot.draw_process_tree(tree, 'bpi12', format='pdf')

	def test_loop_of_one(self):
		lg = EventLog()
		lg.add_trace(1, ['a', 'b', 'b', 'c'])
		lg.add_trace(2, ['a', 'c'])

		miner = InductiveMiner(lg)
		tree = miner.discover()

		print()
		tree.print_tree()
		dot.draw_process_tree(tree, 'single_loop', format='pdf')


	def test_tree_to_net(self):
		lg = EventLog()

		lg.add_trace(1, ['a', 'b', 'g', 'h', 'i', 'j', 'k'])
		lg.add_trace(2, ['a', 'b', 'g', 'h', 'j', 'i', 'k'])
		lg.add_trace(3, ['a', 'b', 'g', 'h', 'i', 'k'])
		lg.add_trace(4, ['a', 'b', 'g', 'h', 'j', 'k'])
		lg.add_trace(5, ['a', 'b', 'c', 'd', 'e', 'h', 'i', 'k'])
		lg.add_trace(6, ['a', 'b', 'c', 'd', 'e', 'f', 'c', 'd',
						 'e', 'h', 'i', 'k'])

		miner = InductiveMiner(lg)
		tree = miner.discover()

		tree.print_tree()
		# dot.draw_process_tree(tree, format='pdf')

		net = miner.tree_to_petri_net(tree)
		dot.draw_petri_net(net, 'process_tree_to_net')