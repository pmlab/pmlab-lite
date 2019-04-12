from functools import reduce
from pmlab_lite.discovery import ProcessTree, Cut
from pmlab_lite.log import EventLog
from pmlab_lite.pn import PetriNet


class InductiveMiner():

	def __init__(self, log: EventLog):
		self.log = self.prepare_log(log)

	def prepare_log(self, event_log: EventLog) -> list:
		"""
		Convert EventLog into simple list structure.
		:param event_log: EventLog
		:return: list
		"""

		log = []
		for trace in event_log.get_traces():
			red_trace = []
			[red_trace.append(event['activity_name']) for event in trace]
			log.append(red_trace)
		return log

	def discover(self) -> ProcessTree:
		return ProcessTree(self, self.log)

	def split_log(self, split: list, cut, log: list):
		log_left = []
		log_right = []

		if cut == Cut.SEQ:
			# max sequence cut
			logs = []
			for part in split:
				sub_log = []

				if len(part) > 1 and \
						all([isinstance(sub, list) for sub in part]):
					part = list(reduce(lambda x, y: x + y, part))

				for trace in log:
					if any([ele in trace for ele in part]):
						part_of_trace = list(filter(lambda x: x in part, trace))
						if part_of_trace not in sub_log:
							sub_log.append(part_of_trace)
					else:
						if [] not in sub_log:

							sub_log.append([])
				logs.append(sub_log)

			return logs

		elif cut == Cut.PARA:
			for trace in log:
				if split[0][0] in trace and split[1][0] in trace:
					left_part = [split[0][0]]
					right_part = [split[1][0]]
				elif split[0][0] in trace:
					left_part = [split[0][0]]
					right_part = []
				else:
					left_part = []
					right_part = [split[1][0]]

				if right_part not in log_right:
					log_right.append(right_part)

				if left_part not in log_left:
					log_left.append(left_part)

		elif cut == Cut.EXCL:
			for trace in log:
				if any([ele in trace for ele in split[0]]):
					log_left.append(trace)
				else:
					log_right.append(trace)

		elif cut == Cut.LOOP:
			for trace in log:
				if any([ele in trace for ele in split[1]]):
					left_part = split[0]
					right_part = split[1]
				else:
					left_part = trace
					right_part = []

				if right_part not in log_right:
					log_right.append(right_part)

				if left_part not in log_left:
					log_left.append(left_part)

		return log_left, log_right

	def tree_to_petri_net(self, tree: ProcessTree) -> PetriNet:
		net = PetriNet()
		net.add_place(1)
		# net.add_marking(1, 1)

		def add_region(sub_tree, place_in, place_out):

			if isinstance(sub_tree, ProcessTree):
				if sub_tree.cut == Cut.PARA:
					# add additional input place
					add_region(sub_tree.children[0], place_in, place_out)
					for child in sub_tree.children[1:]:
						new_place_in = max(list(net.places.values()))[0] + 1
						add_region(sub_tree.children[0], new_place_in,
								   place_out)

				elif sub_tree.cut == Cut.EXCL:
					pass
				elif sub_tree.cut == Cut.SEQ:
					pass
				elif sub_tree.cut == Cut.LOOP:
					pass
				else:
					next = min(list(net.transitions.values()))[0] - 1
					net.add_transition(''.join(['sub region', str(next)]))
					trans = min(list(net.transitions.values()))[0]
					net.add_edge(place_in, trans)
					net.add_edge(trans, place_out)
			else:
				net.add_transition(sub_tree)
				trans = min(list(net.transitions.values()))[0]
				net.add_edge(place_in, trans)
				net.add_edge(trans, place_out)



		for child in tree.children:
			pre_place = max(list(net.places.values()))
			net.add_place(pre_place + 1)
			add_region(child, pre_place, pre_place + 1)



		return net