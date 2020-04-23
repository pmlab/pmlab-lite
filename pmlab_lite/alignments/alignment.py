#class to store te specifications if the found alignment(s)
class Alignment:
	def __init__(self):
		self.alignment_move = []
		self.move_in_model = []
		self.move_in_log = []
		self.fitness = []
		self.closed_list_end = []
