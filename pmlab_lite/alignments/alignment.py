"""The Alignment class."""
from . import constants as c
from . node import Node


# class to store te specifications if the found alignment(s)
class Alignment:
    """Represents an alignment."""

    def __init__(self):
        """
        Initialize the alignment and it's characteristics.

        Set class variables: the alignments, the moves divided into log, model
        and alignment moves and the fitness values.
        """
        self.alignments = []
        self.alignment_moves = []
        self.model_moves = []
        self.log_moves = []
        self.fitness = []

    def _fitness(self):
        for node in self.alignments:
            u = node.alignment
            n_aligned = len([e for e in u if (e[0] == e[1] or 'tau' in e[0])])
            fitness = round(n_aligned / len(u), 3)
            self.fitness.append(fitness)

    def _alignment_moves(self):
        for node in self.alignments:
            u = node.alignment
            self.alignment_moves.append([e for e in u])

    def _model_moves(self):
        for node in self.alignments:
            u = node.alignment
            model_move = [e[0] for e in u if (e[0] != c.BLANK)]
            self.model_moves.append(model_move)

    def _log_moves(self):
        for node in self.alignments:
            u = node.alignment
            self.log_moves.append([e[1] for e in u if e[1] != c.BLANK])

    def print_alignments(self):
        """Print all alignments."""
        for node in self.alignments:
            self.print_alignment(node)
            print()

    def print_alignment(self, node: Node):
        """Print one alignment, given as a Node."""
        row_one = c.ROW1
        row_two = c.ROW2
        n_indents = 0
        len_alignment = len(node.alignment)

        for i, tup in enumerate(node.alignment):
            n_trailing_whitespaces1 = max(0, -(len(tup[1])-len(tup[0])))
            n_trailing_whitespaces2 = max(0, -(len(tup[0])-len(tup[1])))
            trace_act = ' ' + tup[1] + ' '*n_trailing_whitespaces1 + ' |'
            model_act = ' ' + tup[0] + ' '*n_trailing_whitespaces2 + ' |'

            # print part of the alignment that would exceed line length
            if len(row_one) + len(trace_act) > c.CHARS_PER_ROW:
                self.__print_rows(row_one, row_two, n_indents)
                n_indents += 1
                row_one = c.INDENT + '    '*n_indents + '| ' + trace_act
                row_two = c.INDENT + '    '*n_indents + '| ' + model_act
            else:
                row_one += trace_act
                row_two += model_act

            if i == len_alignment-1:  # print if last element of alignment
                self.__print_rows(row_one, row_two, n_indents)

    def __print_rows(self, row_one, row_two, n_indents):
        start_idx = row_one.index('|')
        break_line = ' '*start_idx + '-'*(len(row_one)-start_idx)

        print(break_line)
        print(row_one)
        print(break_line)
        print(row_two)
        print(break_line)
