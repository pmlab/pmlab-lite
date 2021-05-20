from . import constants as c


# class to store te specifications if the found alignment(s)
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
            self.fitness.append(round(len([e for e in u if ((e[0] != c.BLANK and e[1] != c.BLANK) or ('tau' in e[0]))]) / len(u), 3))

    def _alignment_moves(self):
        for node in self.alignments:
            u = node.alignment
            self.alignment_moves.append([e for e in u if ('tau' not in e[0])])

    def _model_moves(self):
        for node in self.alignments:
            u = node.alignment
            self.model_moves.append([e[0] for e in u if (e[0] != c.BLANK and ('tau' not in e[0]))])

    def _log_moves(self):
        for node in self.alignments:
            u = node.alignment
            self.log_moves.append([e[1] for e in u if e[1] != c.BLANK])

    def print_alignment(self):
        chars_per_row = 110
        row_one = '| log trace          |'
        row_two = '| execution sequence |'
        indent = '                     '

        for node in self.alignments:
            n_indents = 0
            for tup in node.alignment:
                n_trailing_whitespaces1 = max(0, -(len(tup[1])-len(tup[0])))
                n_trailing_whitespaces2 = max(0, -(len(tup[0])-len(tup[1])))
                trace_act = ' ' + tup[1] + ' '*n_trailing_whitespaces1 + ' |'
                model_act = ' ' + tup[0] + ' '*n_trailing_whitespaces2 + ' |'

                if len(row_one) + len(trace_act) > chars_per_row:
                    self.__print_rows(row_one, row_two, n_indents)
                    n_indents += 1
                    row_one = indent + '    '*n_indents + '| ' + trace_act
                    row_two = indent + '    '*n_indents + '| ' + model_act
                else:
                    row_one += trace_act
                    row_two += model_act
            print()

    def __print_rows(self, row_one, row_two, n_indents):
        start_idx = row_one.index('|')
        break_line = ' '*start_idx + '-'*(len(row_one)-start_idx)

        print(break_line)
        print(row_one)
        print(break_line)
        print(row_two)
        print(break_line)
