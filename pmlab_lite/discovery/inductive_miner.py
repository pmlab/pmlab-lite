from functools import reduce
from pmlab_lite.discovery import ProcessTree, Cut
from pmlab_lite.log import EventLog


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

	def discover(self):
		return ProcessTree(self, self.log)

	def split_log(self, split: list, cut, log: list):
		log_left = []
		log_right = []

		if cut == Cut.SEQ:
			# max sequence cut
			logs = []
			for part in split:
				sub_log = []

				if len(part) > 1:
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