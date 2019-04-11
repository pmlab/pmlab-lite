import unittest

from pmlab_lite.discovery.cut import Cut
from pmlab_lite.helper.graph import Graph
from pmlab_lite.discovery.inductive_miner import InductiveMiner
import pmlab_lite.log as eLog
from pmlab_lite.helper.io.xes import import_from_xes
from pmlab_lite.helper.viz import dot
from pmlab_lite.log import EventLog


class TesInductiveMinerMethods(unittest.TestCase):

	def log2_dfg(self):
		print()
		log = eLog.EventLog()
		log.add_trace(1, ['A', 'B', 'G', 'H', 'I', 'K'])
		log.add_trace(2, ['A', 'B', 'G', 'H', 'J', 'K'])
		log.add_trace(3, ['A', 'B', 'C', 'D', 'E', 'H', 'J', 'I', 'K'])
		log.add_trace(4, ['A', 'B', 'C', 'D', 'E', 'H', 'I', 'J', 'K'])
		log.add_trace(5, ['A', 'B', 'C', 'D', 'E', 'F', 'C', 'D', 'E', 'H',
						  'I', 'K'])
		log.add_trace(6, ['A', 'B', 'C', 'D', 'E', 'F', 'C', 'D', 'E', 'H',
						  'J', 'K'])

		g = Graph()
		g.from_event_log(log)
		g.find_entry()
		g.find_exit()
		g.get_order()
		# print('entry: %s, exit: %s' %(g.entry, g.exit))
		#print('order %s ' %g.order)
		# print('Activities: %s' %g.activities)

		# dot.draw_graph(g, 'init_dfg', 'png', render=True)

		comp = scc.find_scc(g)
		print('SCC: %s' %comp)

		miner = InductiveMiner(g)

		"""
		g_con, scc_mapping = IM.condense_components(g, comp)
		g_con.find_entry()
		g_con.find_exit()
		g_con.get_order()
		print(g_con.order)
		# dot.draw_graph(g_con, 'con_dfg', 'png', render=True)
		excl_cuts = IM.find_exclusive_cut(g_con, scc_mapping)
		print('exclusive cut(s): %s ' %excl_cuts)

		IM.find_sequential_cut(g_con, scc_mapping)
		"""

	"""
	def test_condens_components(self):
		g = Graph()
		g.add_edge('a', 'b').add_edge('b', 'c').add_edge('b', 'g') \
			.add_edge('c', 'd').add_edge('d', 'e').add_edge('e', 'f') \
			.add_edge('f', 'c').add_edge('e', 'h').add_edge('g', 'h') \
			.add_edge('h', 'i').add_edge('h', 'j').add_edge('i', 'k') \
			.add_edge('j', 'k').add_edge('i', 'j').add_edge('j', 'i')

		comp = SCC.scc(g)

		#print(comp)

		g2 = IM.condense_components(g, comp)

	def test_condens_xor_components(self):
		g = Graph()
		g.add_edge('a', 'b').add_edge('b', 'c').add_edge('b', 'g') \
			.add_edge('c', 'd').add_edge('d', 'e').add_edge('e', 'f') \
			.add_edge('f', 'c').add_edge('e', 'h').add_edge('g', 'h') \
			.add_edge('h', 'i').add_edge('h', 'j').add_edge('i', 'k') \
			.add_edge('j', 'k').add_edge('i', 'j').add_edge('j', 'i')

		comp = SCC.scc(g)
		g2 = IM.condense_components(g, comp)

		IM.condense_xor_components(g2)
	"""

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

		logs = miner.split_log(max_seq_split, 5, log)
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

	def test_bpi_12(self):
		# log = import_from_xes('/Users/Simon/Google Drive/Universität/Master/Semester 4/Masterarbeit/master-thesis-code/data/BPI Challenge 2012/logs/BPI_Challenge_2012.xes')
		# log = import_from_xes('/Users/Simon/Google Drive/Universität/Master/Semester 4/Masterarbeit/master-thesis-code/data/Road_Traffic_Fine_Management_Process/logs/Road_Traffic_Fine_Management_Process.xes')
		lg = EventLog()

		lg.add_trace(1, ['EventA test', 'EventB', 'EventG', 'EventH', 'EventI',
						 'EventJ', 'EventK'])
		lg.add_trace(2, ['EventA test', 'EventB', 'EventG', 'EventH', 'EventJ',
						 'EventI', 'EventK'])
		lg.add_trace(3, ['EventA test', 'EventB', 'EventG', 'EventH', 'EventI',
						 'EventK'])
		lg.add_trace(4, ['EventA test', 'EventB', 'EventG', 'EventH', 'EventJ',
						 'EventK'])
		lg.add_trace(5, ['EventA test', 'EventB', 'EventC', 'EventD', 'EventE',
						 'EventH', 'EventI', 'EventK'])
		lg.add_trace(6, ['EventA test', 'EventB', 'EventC', 'EventD', 'EventE',
						 'EventF test test test test', 'EventC', 'EventD',
						 'EventE', 'EventH', 'EventI', 'EventK'])

		lg = EventLog()

		miner = InductiveMiner(lg)
		tree = miner.discover()


		tree.print_tree()
		dot.draw_process_tree(tree)

	def test_loop_of_one(self):
		lg = EventLog()
		lg.add_trace(1, ['a', 'b', 'b', 'c'])
		lg.add_trace(2, ['a', 'c'])

		miner = InductiveMiner(lg)
		tree = miner.discover()

		tree.print_tree()
		dot.draw_process_tree(tree, format='pdf')