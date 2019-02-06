import random
import string
from copy import copy


#import inductive_miner as IM
from pmlab_lite.helper.graph import Graph

from pmlab_lite.pn import PetriNet
#from pmlab_lite.discovery.inductive_miner import InductiveMiner as IM

class ProcessTree():

    def __init__(self, miner, log: list, level: int = 0, parent: str = 'root'):
        print('------------------------')
        print('(tree) LOG %s' % log)
        self.miner = miner
        self.level = level
        self.parent = parent
        self.id = self.gen_id()
        self.log = copy(log)
        self.dfg = Graph().from_log(log)
        self.scc = self.dfg.get_scc()
        self.cut = None
        self.children = []

        self.find_cuts()

    def gen_id(self):
        id = [str(self.level)]
        for i in range(4):
            id.append(random.choice(string.ascii_letters))
        return ''.join(id)

    def find_cuts(self):

        seq_cut = self.find_seq()
        para_cut = self.find_para()
        excl_cut = self.find_excl()
        loop_cut = self.find_loop()

        print('(tree) seq: %s, para: %s, excl: %s, loop: %s.' %
              (seq_cut, para_cut, excl_cut, loop_cut))

        if excl_cut:
            logs = self.miner.split_log(self.log, excl_cut, self.miner.EXC)
            self.cut = self.miner.EXC
            for sub_log in logs:
                print('(tree) excl_cut %s' % sub_log)
                self.children.append(ProcessTree(self.miner, sub_log,
                self.level + 1, self.id))
        # ------------------------------------
        elif seq_cut:
            # print(seq_cut)
            logs = self.miner.split_log(self.log, seq_cut, self.miner.SEQ)
            self.cut = self.miner.SEQ
            # print('(tree) seq_cut logs: %s ' % logs)
            # for cut in seq_cut:
            #    if len(cut) <= 1:
            #        self.leafs.append(cut)
            for sub_log in logs:
                # print('(tree) sub_log %s' % sub_log)
                if len(sub_log) > 1:
                    # at least 2 traces
                    if any([len(trace) > 1 for trace in sub_log]):
                        # print('(tree) 1.1')
                        self.children.append(ProcessTree(self.miner, sub_log,
                                                         self.level + 1,
                                                         self.id))
                    else:
                        if any([len(trace) == 0 for trace in sub_log]):
                            # print('(tree) 1.2.1')
                            self.children.append(ProcessTree(self.miner,
                            sub_log,
                                                             self.level,
                                                             self.parent))
                        else:
                            # print('(tree) 1.2.2')
                            self.children.append(sub_log[0][0])
                else:
                    if len(sub_log[0]) == 1:
                        # print('(tree) 2.1')
                        self.children.append(sub_log[0][0])
                    else:
                        # print('(tree) 2.2')
                        self.children.append(ProcessTree(self.miner, sub_log,
                                                         self.level + 1,
                                                         self.id))
        # ------------------------------------
        elif para_cut:
            self.cut = self.miner.PAR
            logs = self.miner.split_log(self.log, para_cut, self.miner.PAR)
            for sub_log in logs:
                if len(sub_log) > 1:
                    self.children.append(ProcessTree(self.miner, sub_log,
                    self.level + 1, self.id))
                else:
                    # print('(tree) para sub_log %s' % sub_log)
                    if len(sub_log[0]) > 0:
                        self.children.append(sub_log[0][0])
                    else:
                        self.children.append('tau')
        # ------------------------------------
        elif loop_cut:
            logs = self.miner.split_log(self.log, loop_cut, self.miner.LOOP)
            self.cut = self.miner.LOOP
            # for cut in loop_cut:
            #    if len(cut) <= 1:
            #        self.children.append(cut[0])
            for sub_log in logs:
                print('(tree) sub log loop %s' % sub_log)
                if len(sub_log) > 1:
                    self.children.append(ProcessTree(self.miner, sub_log,
                    self.level + 1, self.id))
                else:
                    print('(tree) loop sub_log %s' % sub_log)
                    if len(sub_log[0]) > 1:
                        self.children.append(ProcessTree(self.miner, sub_log,
                                                         self.level + 1,
                                                         self.id))
                    if len(sub_log[0]) == 1:
                        self.children.append(sub_log[0][0])
                    # else:
                    #    self.children.append('tau')
        # ------------------------------------
        else:  # base case
            for trace in self.log:
                # print('(tree) base case %s' %trace)
                if len(trace) == 1:  # single activity
                    if trace[0] not in self.children:
                        self.children.append(trace[0])
                elif len(trace) > 1:  # flower
                    self.cut = self.miner.LOOP
                    if trace[0] not in self.children:
                        self.children.append(trace[0])
                    self.children.append('tau')
                else:  # empty trace
                    self.cut = self.miner.EXC
                    self.children.append('tau')
            print('(tree) trivial %s' % self.log)

        self.reduce()

    def find_seq(self):
        # print('(tree) vertexes %s' % self.dfg.vertexes)
        # print('(tree) scc %s' % self.scc)
        # candidates = []
        for o in self.scc:
            for t in self.scc:
                # if o[0] != t[0]:
                if self.dfg.is_reachable(o[0], t[0]) and \
                        not self.dfg.is_reachable(t[0], o[0]):
                    # print('(tree) find_seq %s' % o)
                    # if o not in candidates:
                    #    candidates.append(o)
                    return o
        # print('(tree) candidates %s' % candidates)

        # return candidates
        return []

    def find_excl(self):
        for o in self.scc:
            for t in self.scc:
                if o[0] != t[0]:
                    if not self.dfg.is_reachable(o[0], t[0]) and \
                            not self.dfg.is_reachable(t[0], o[0]):
                        return [o, t]
        return []

    def find_para(self):
        g_i = self.dfg.invert()
        # pprint('(tree) g %s' % self.dfg.vertexes)
        # pprint('(tree) g_i %s' % g_i.vertexes)
        scc_i = g_i.get_scc()
        # print('(tree) para scc_i %s' % scc_i)
        for o in scc_i:
            for t in scc_i:
                if o[0] != t[0]:
                    if self.dfg.is_reachable(o[0], t[0]) and \
                            self.dfg.is_reachable(t[0], o[0]):
                                                # TODO: maybe rework this
                        if o[0] in g_i.start_nodes and t[0] in g_i.start_nodes:
                            return [o, t]
        return []

    def find_loop(self):

        def cmp_in_scc(cmp):
            for s in self.scc:
                if sorted(cmp) == sorted(s):
                    return True
            return False

        g_i = self.dfg.invert()
        scc_i = g_i.get_scc()
        # print('(tree) start nodes %s' % g_i.start_nodes)
        print('(tree) loop scc_i %s' % scc_i)

        g_reduced = g_i.remove_start()
        g_reduced = g_reduced.remove_end()
        branches = g_reduced.get_scc()
        # print('(tree) branches %s' % branches)
        # print('(tree) start/end %s/%s' % (self.dfg.start_nodes, self.dfg.end_nodes))
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
                    # print('(tree) 1.1')
                    if isinstance(b, list):
                        forward += b
                    else:
                        forward.append(b)
                elif b[0] in self.dfg.vertexes[self.dfg.end_nodes[0]]:
                    # print('(tree) 1.2')
                    backward = b
                else:
                    # print('(tree) 1.3')
                    # print('(tree) add backward %s' % b)
                    backward += b
                # add previusly removed nodes
            # print('(tree) backward %s' % backward)
            # print('(tree) forward %s' % forward)
            forward = [self.dfg.start_nodes[0]] + forward \
                + [self.dfg.end_nodes[0]]
            return[forward, backward]

    def print_tree(self):
        self.reduce()
        print('%s (%s/%s): %s (%s) chil: %s' %
              (self.level, self.parent, self.id,
               self.miner.print_cut(self.cut), self.leafs, len(self.children)))

        for child in self.children:
            child.print_tree()

    def reduce(self):
        for idx, child in enumerate(self.children):
            if isinstance(child, ProcessTree) and self.cut == child.cut:
                new_children = self.children[:idx]
                new_children += child.children
                new_children += self.children[idx + 1:]
                self.children = new_children
                self.reduce()
                break
            elif isinstance(child, ProcessTree):
                child.reduce()

    def to_petri_net(self, net=None):
        if net is None:
            net = PetriNet()

        for child in self.children:
            if isinstance(child, ProcessTree):
                child.to_petri_net(net)
            else:
                net.add_transition(child)

        print(net)
