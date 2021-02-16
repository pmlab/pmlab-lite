from . import constants as c

#class to store te specifications if the found alignment(s)
class Alignment:
	def __init__(self):
		self.alignments = []
		self.alignment_moves = []
		self.model_moves = []
		self.log_moves = []
		self.fitness = []

	def _fitness(self):
		for node in self.alignments:
			u = node.alignment
			self.fitness.append( round ( len( [e for e in u if ((e[0]!=c.BLANK and e[1]!=c.BLANK) or ('tau' in e[0])) ]) / len(u), 3) )

	def _alignment_moves(self):
		for node in self.alignments:
			u = node.alignment
			self.alignment_moves.append( [e for e in u if ('tau' not in e[0])] )

	def _model_moves(self):
		for node in self.alignments:
			u = node.alignment
			self.model_moves.append( [e[0] for e in u if (e[0]!=c.BLANK and ('tau' not in e[0]))] )

	def _log_moves(self):
		for node in self.alignments:
			u = node.alignment
			self.log_moves.append( [e[1] for e in u if e[1] != c.BLANK])

	def print_alignment(self):
		row_one  = '| log trace          |'
		row_two  = '| execution sequence |'
		separator = ''


		for node in self.alignments:
			for tup in node.alignment:
				row_one += ' ' + tup[1] + ' '*max(0, -(len(tup[1])-len(tup[0]))) + ' |'
				row_two += ' ' + tup[0] + ' '*max(0, -(len(tup[0])-len(tup[1]))) + ' |'

			print('-'*len(row_one))
			print(row_one)
			print('-'*len(row_one))
			print(row_two)
			print('-'*len(row_one))
