#constant string
#class to store te specifications if the found alignment(s)
#merge this with a_star.py so that file == alignment.py and alignment is one class with astar as member function
class Alignment:
	def __init__(self):
		self.alignment_move = []
		self.move_in_model = []
		self.move_in_log = []
		self.fitness = []
