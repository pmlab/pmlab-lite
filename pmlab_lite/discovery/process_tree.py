import random
import string
from copy import copy

from pmlab_lite.discovery.cut import Cut
from pmlab_lite.helper.graph import Graph


class ProcessTree():

	def __init__(self, miner, log: list, level: int = 0,
				 parent='root', discover = True):

		self.miner = miner
		self.level = level
		self.parent = parent
		self.id = self.gen_id()
		self.log = copy(log)
		self.dfg = Graph().from_log(log)
		self.scc = self.dfg.get_scc()
		self.cc = self.dfg.get_cc()
		self.cut = None
		self.children = []

		print('---------')
		print('(tree) number of cc: %s' %len(self.cc))
		print('(tree) number of scc: %s' %len(self.scc))

		if discover:
			self.find_cuts()

	def gen_id(self) -> str:
		"""
		Returns random generated id.
		:return: String
		"""
		id = [str(self.level)]
		for i in range(4):
			id.append(random.choice(string.ascii_letters))
		return ''.join(id)

	def find_cuts(self):

		def insert_base_case(activity):
			if activity == []:
				return 'tau'
			else:
				return activity[0]

		seq_cut = self.find_seq()
		para_cut = self.find_para()
		excl_cut = self.find_excl()
		loop_cut = self.find_loop()

		print()
		print('(tree) found seq: %s, para: %s, excl: %s, loop: %s'
			  %(seq_cut, para_cut, excl_cut, loop_cut))

		if len(seq_cut) > 0:
			self.cut = Cut.SEQ
			sub_logs = self.miner.split_log(seq_cut, Cut.SEQ, self.log)
			print('(tree) seq. cut %s' %(sub_logs))


			for sub_log in sub_logs:
				if len(sub_log) > 1:
					self.children.append(ProcessTree(self.miner, sub_log,
													 self.level + 1, self))
				else:
					self.children.append(insert_base_case(sub_log[0]))

		elif len(excl_cut) > 0:
			self.cut = Cut.EXCL
			log_left, log_right = self.miner.split_log(excl_cut, Cut.EXCL,
													   self.log)

			print('(tree) excl. cut %s / %s' %(log_left, log_right))

			for sub_log in [log_left, log_right]:
				if len(sub_log) > 1:
					self.children.append(ProcessTree(self.miner, sub_log,
													 self.level + 1, self))
				else:
					self.children.append(insert_base_case(sub_log[0]))

		elif len(para_cut) > 0:
			self.cut = Cut.PARA
			log_left, log_right = self.miner.split_log(para_cut, Cut.PARA,
													   self.log)

			print('(tree) para. cut %s / %s' % (log_left, log_right))

			for sub_log in [log_left, log_right]:
				if len(sub_log) > 1:
					self.children.append(ProcessTree(self.miner, sub_log,
													 self.level + 1, self))
				else:
					self.children.append(insert_base_case(sub_log[0]))

		elif len(loop_cut) > 0:
			self.cut = Cut.LOOP
			log_left, log_right = self.miner.split_log(loop_cut, Cut.LOOP,
													self.log)

			print('(tree) loop cut %s / %s' % (log_left, log_right))


			self.children.append(ProcessTree(self.miner, log_left,
											 self.level + 1, self))

			self.children.append(ProcessTree(self.miner, log_right,
											 self.level + 1, self))

		else:
			print('(tree) base case: %s' %self.log)
			if len(self.log) > 1:
				if all([len(set(sub_log)) == 1 for sub_log in self.log]):
					self.cut = Cut.EXCL
					for ele in self.log:
						self.children.append(insert_base_case(ele))
				else:
					self.cut = Cut.EXCL
					for sub_log in self.log:

						if len(sub_log) < 2:
							self.children.append(insert_base_case(sub_log))
						else:
							tree = ProcessTree(self.miner, sub_log,
											   self.level + 1, self.id, False)
							tree.cut = Cut.LOOP
							tree.children.append(insert_base_case(sub_log))
							self.children.append(tree)
			else:
				self.children.append(insert_base_case(sub_log))

	def find_seq(self):
		print('(tree) search for SEQ')

		if(len(self.scc) > 1 and len(set(self.dfg.start_nodes))) == 1:
			if(len(self.cc) == 1):

				mapping = {}
				for comp in self.scc:
					mapping[len(mapping)] = comp

				def get_mapping(value):
					for k, v in mapping.items():
						if value[0] in v:
							return k
					return None

				sorted_scc = {}
				scc = self.scc  # TODO don't use mapping
				# print(scc)
				g = self.dfg  # TODO don't use mapping
				# pprint.pprint(g.vertexes)

				for comp in scc:
					sorted_scc[get_mapping(comp)] = [[], [], []]
					for comp2 in scc:
						if comp is not comp2:
							if g.is_reachable(comp[0], comp2[0]) and \
									not g.is_reachable(comp2[0], comp[0]):
								# comp before comp2
								sorted_scc[get_mapping(comp)][0].append(comp2)
							elif not g.is_reachable(comp[0], comp2[0]) and \
									g.is_reachable(comp2[0], comp[0]):
								# comp after comp2
								sorted_scc[get_mapping(comp)][1].append(comp2)
							else:
								# either parallel or exclusive
								sorted_scc[get_mapping(comp)][2].append(comp2)


				# find very first activity
				first = []
				for key, relations in sorted_scc.items():
					if len(relations[1]) == 0:
						first.append(key)

				# get all succeeding events in no order
				first = mapping[first[0]]
				next_candidates = []
				for key, relations in sorted_scc.items():
					if first in relations[1]:  # [before][after][para/excl]
						next_candidates.append(mapping[key])


				# sort succeeding events
				pre = [first]
				while (len(next_candidates) > 0):
					add = True
					for candidate in next_candidates:
						for key, relations in sorted_scc.items():
							if candidate in relations[0]:
								if mapping[key] not in pre:
									add = False
						if add:
							pre.append(candidate)
							next_candidates.remove(candidate)

				result = []
				for idx, comp in enumerate(pre):
					print(comp)
					if len(sorted_scc[get_mapping(comp)][2]) > 0:
						if idx > 0 and \
								len(sorted_scc[get_mapping(pre[idx - 1])][2]) > 0:
							result[-1].append(comp)
						else:
							result.append([comp])
					else:
						result.append(comp)
				return result
			else:
				print('(tree) No sequence -> multiple CC OR multiple start '
					  'points')
				return []
		else:
			print('(tree) No sequence -> single SCC')
			return []

	def find_para(self):
		print('(tree) search for PARA')
		g_i = self.dfg.invert()
		scc_i = g_i.get_scc()

		candidates = []
		for o in scc_i:
			for t in scc_i:
				if o[0] != t[0]:
					if self.dfg.is_reachable(o[0], t[0]) and \
							self.dfg.is_reachable(t[0], o[0]):
						# TODO: maybe rework this
						if o[0] in g_i.start_nodes and t[0] in g_i.start_nodes:
							if o not in candidates:
								candidates.append(o)
							if t not in candidates:
								candidates.append(t)

		return candidates

	def find_excl(self):
		print('(tree) search for EXCL')
		for o in self.scc:
			for t in self.scc:
				if o[0] != t[0]:
					if not self.dfg.is_reachable(o[0], t[0]) and \
							not self.dfg.is_reachable(t[0], o[0]):
						return [o, t]
		return []

	def find_loop(self):
		print('(tree) search for LOOP')


		g_i = self.dfg.invert()

		g_reduced = g_i.remove_start()
		g_reduced = g_reduced.remove_end()
		branches = g_reduced.get_scc()
		if len(branches) == 0:
			return []
		elif len(branches) == 1:
			backward = branches[0]
			forward = [self.dfg.start_nodes[0], self.dfg.end_nodes[0]]
			return [forward, backward]
		else:
			backward = []
			forward = []
			for b in branches:
				if b[0] in self.dfg.vertexes[self.dfg.start_nodes[0]]:
					if isinstance(b, list):
						forward += b
					else:
						forward.append(b)
				elif b[0] in self.dfg.vertexes[self.dfg.end_nodes[0]]:
					backward = b
				else:
					backward += b
			forward = [self.dfg.start_nodes[0]] + forward \
					  + [self.dfg.end_nodes[0]]

			return [forward, backward]

	def print_tree(self):
		"""
		Print tree structure to console.
		"""

		def print_cut(cut: int) -> str:
			if cut == Cut.SEQ:
				return 'SEQ'
			elif cut == Cut.PARA:
				return 'PAR'
			elif cut == Cut.EXCL:
				return 'EXL'
			elif cut == Cut.LOOP:
				return 'LOOP'

		if isinstance(self.parent, ProcessTree):
			parent = self.parent.id
		else:
			parent = 'root'
		print('%s (%s/%s) node: %s children: %s' %
			  (self.level, parent, self.id,
			   print_cut(self.cut), self.children))

		for child in self.children:
			if isinstance(child, ProcessTree):
				child.print_tree()