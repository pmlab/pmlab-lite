import random
import string
from copy import copy
import pprint

#import inductive_miner as IM
from pmlab_lite.helper.graph import Graph

from pmlab_lite.pn import PetriNet
#from pmlab_lite.discovery.inductive_miner import InductiveMiner as IM

class ProcessTreeOLD():

    def __init__(self, miner, log: list, level: int = 0, parent = 'root'):
        print('------------------------')
        # print('(tree) LOG %s' % log)
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

        # print('(tree) cc: %s' %self.cc)
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
        print('(tree) scc: %s' %self.scc)
        print('(tree) cc: %s' %self.cc)
        # prefer excl over seq:
        # if seq_cut and excl_cut:
        #     print('(tree) seq: %s' %seq_cut)
        #     print('(tree) excl %s' %excl_cut)
        #     a = seq_cut[0] in excl_cut[0]
        #     # a = all([item] in excl_cut for item in seq_cut)
        #     if a:
        #         seq_cut = []
        #     print('(tree) %s' %a)

        if seq_cut:
            print('(tree) found seq cut %s' %seq_cut)


            logs = self.miner.split_log(self.log, seq_cut, self.miner.SEQ)
            print('(tree) logs:')
            pprint.pprint(logs)
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
                                                         self))
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
                                                         self))
        # ------------------------------------
        elif excl_cut:
            logs = self.miner.split_log(self.log, excl_cut, self.miner.EXC)
            self.cut = self.miner.EXC
            for sub_log in logs:
                print('(tree) excl_cut %s' % sub_log)
                self.children.append(ProcessTree(self.miner, sub_log,
                self.level + 1, self))
        # ------------------------------------
        elif para_cut:
            self.cut = self.miner.PAR
            logs = self.miner.split_log(self.log, para_cut, self.miner.PAR)
            for sub_log in logs:
                if len(sub_log) > 1:
                    self.children.append(ProcessTree(self.miner, sub_log,
                    self.level + 1, self))
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
                                                         self))
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
        print('(tree) search for SEQ')
        """
        # TODO prüfe für scc's und cc's
        if(len(self.scc) > 1 and len(self.dfg.start_nodes) == 1):
            if(len(self.cc) == 1):
                mapping = {}
                for comp in self.scc:
                    mapping[len(mapping)] = comp

                # pprint.pprint(mapping)

                def get_mapping(value):
                    for k, v in mapping.items():
                        if value[0] in v:
                            return k
                    return None

                sorted_scc = {}
                scc = self.scc # TODO dont use mapping
                # print(scc)
                g = self.dfg # TODO dont use mapping
                # pprint.pprint(g.vertexes)

                for comp in scc:
                    sorted_scc[get_mapping(comp)] = [[], [], []]
                    for comp2 in scc:
                        if comp is not comp2:
                            if  g.is_reachable(comp[0], comp2[0]) and \
                                not g.is_reachable(comp2[0], comp[0]):
                                # comp before comp2
                                # print('%s is BEFORE %s' %(comp, comp2))
                                sorted_scc[get_mapping(comp)][0].append(comp2)
                            elif not g.is_reachable(comp[0], comp2[0]) and \
                                g.is_reachable(comp2[0], comp[0]):
                                # comp after comp2
                                # print('%s is AFTER %s' %(comp, comp2))
                                sorted_scc[get_mapping(comp)][1].append(comp2)
                            else:
                                # eather parallel or exclusive
                                # print('%s and %s are PARALLEL/EXCL' %(comp, comp2))
                                sorted_scc[get_mapping(comp)][2].append(comp2)

                # pprint.pprint(sorted_scc)

                #############
                # find very first activity
                first = []
                for key, relations in sorted_scc.items():
                    if len(relations[1]) == 0:
                        first.append(key)

                #############
                # get all succeeding events in no order
                first = mapping[first[0]]
                next_candidates = []
                for key, relations in sorted_scc.items():
                    if first in relations[1]: # [before][after][para/excl]
                        next_candidates.append(mapping[key])

                # print('next candidates')
                # pprint.pprint(next_candidates)
                #############
                # sort succeeding events
                pre = [first]

                next = None
                while(len(next_candidates) > 0):
                    add = True
                    # print('pre: %s' %pre)
                    for candidate in next_candidates:
                        for key, relations in sorted_scc.items():
                            if candidate in relations[0]:
                                if mapping[key] not in pre:
                                    # print('%s removed -> %s; %s' %(candidate, relations[1], key))
                                    add = False
                        if add:

                            next = candidate
                            # print('%s is next' %next)
                            pre.append(next)
                            next_candidates.remove(next)
                # print('total order of scc %s' %pre)

                result = []

                for idx, comp in enumerate(pre):
                    if len(sorted_scc[get_mapping(comp)][2]) > 0:
                        if idx > 0 and len(sorted_scc[get_mapping(pre[idx -1])][2]) > 0:
                            result[-1].append(comp)
                        else:
                            result.append([comp])
                    else:
                        result.append(comp)

                # print('result %s' %result)

                return result
            else:
                print('Graph is not connected.')
                return []
        else:
            print('Graph has only a single scc.')
            return []
        """
        ###############
        # ALTER STAND:
        # if (len(self.scc) > 1 and len(self.dfg.start_nodes) == 1):
        #     if (len(self.cc) == 1):
        for o in self.scc:
            for t in self.scc:
                if self.dfg.is_reachable(o[0], t[0]) and \
                        not self.dfg.is_reachable(t[0], o[0]):
                    return o
            return []
            # return candidates
        #     else:
        #         return []
        # else:
        #     return []

    def find_excl(self):
        print('(tree) search for EXCL')
        for o in self.scc:
            for t in self.scc:
                if o[0] != t[0]:
                    if not self.dfg.is_reachable(o[0], t[0]) and \
                            not self.dfg.is_reachable(t[0], o[0]):
                        return [o, t]
        return []

    def find_para(self):
        print('(tree) search for PARA')
        g_i = self.dfg.invert()
        # pprint('(tree) g %s' % self.dfg.vertexes)
        # pprint('(tree) g_i %s' % g_i.vertexes)
        scc_i = g_i.get_scc()
        # print('(tree) para scc_i %s' % scc_i)
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
        print('(tree) para candidates %s '% candidates)
        return candidates

    def find_loop(self):
        print('(tree) search for LOOP')

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
        if isinstance(self.parent, ProcessTree):
            parent = self.parent.id
        else:
            parent = 'root'
        print('%s (%s/%s): %s chil: %s' %
              (self.level, parent, self.id,
               self.miner.print_cut(self.cut), self.children))

        for child in self.children:
            if isinstance(child, ProcessTree):
                child.print_tree()

    def reduce(self):
        """
        1. node = exc
        2. and all children == seq
        3. and all children == leafs
        4. pull leafs to parten node
        5. change parent node to SEQ
        6. add new Tree = exc and add children as children
        """
        """
        if self.cut == self.miner.EXC:
            all_seq = True
            for c in self.children:
                if isinstance(c, ProcessTree):
                    all_seq = c.cut == self.miner.SEQ
                else:
                    all_seq = False
            # print('(tree) id %s' %self.id)
            # print('(tree) all_seq %s' %all_seq)
            if all_seq:
                leafs = []
                for c in self.children:
                    l = []
                    for cc in c.children:
                        if not isinstance(cc, ProcessTree):
                            l.append(cc)
                    leafs.append(l)
                print('(tree) leafs %s' %leafs)

                all_leafs = True
                for l in leafs:
                    for l2 in leafs:
                        all_leafs = l == l2

                if all_leafs:
                    print('(tree) all_leafs')
                    self.cut = self.miner.SEQ
                    chosen = self.children[0]
                    chosen.cut = self.miner.EXC
                    chosen.children.remove(leafs[0][0])
                    print('*** %s'%chosen.children)
                    for c in self.children[1:]:
                        chosen.children += c.children
                        c.parent = chosen
                    chosen.children.remove(leafs[0][0])
                    self.children = [leafs[0][0], chosen]
                    print('#### %s' %self.children)
                    """
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

    """
    def to_petri_net(self, transitions=None, net=None):
        if net is None:
            net = PetriNet()
        if transitions is None:
            transitions = {}


        for idx, child in reversed(list(enumerate(self.children))):
            if isinstance(child, ProcessTree):
                child.to_petri_net(transitions, net)
            else:
                if self.cut == self.miner.SEQ:
                    print('(PT) SEQ')
                    # add new transition
                    #if child not in net.transitions.keys():
                    net.add_transition(child)

                    # connect transition
                    if idx < len(self.children) - 1:
                        # net.add_place(len(net.places) + 1)
                        net.add_edge(net.transitions[child][-1],len(net.places))
                        net.add_place(len(net.places) + 1)
                        net.add_edge(len(net.places),
                        net.transitions[child][-1])
                    else:
                        net.add_place(len(net.places) + 1)
                        net.add_edge(len(net.places),
                        net.transitions[child][-1])
                    # if idx < len(self.children) - 1:
                    #     net.add_edge(net.transitions[child][0],
                    #     self.level + 1 + idx + 1)
                    # else:
                    #     # final place
                    #     net.add_place(self.level + 1 + idx + 1)
                    #     net.add_edge(net.transitions[child][0],
                    #     self.level + 1 + idx + 1)
                elif self.cut == self.miner.EXC:
                    print('(PT) EXC')
                    plc = len(net.places) + 1
                    net.add_place(plc)
                    net.add_place(plc + 1)
                    net.add_transition('tau')
                    net.add_edge(plc, net.transitions['tau'][-1])
                    net.add_edge(net.transitions['tau'][-1], plc + 1)



        # print(net)
        return net
        """

    def to_petri_net(self, net: PetriNet = None, connection: int = 1):
        if net is None:
            net = PetriNet()
            net.add_place(1)

        if self.cut == self.miner.EXC:
            print('(PT) EXC')
            plc = max(net.places.values()) + 1
            net.add_transition('tau')
            if connection is None:
                net.add_place(plc)
                net.add_edge(plc, net.transitions['tau'][-1])
            else:
                net.add_edge(connection, net.transitions['tau'][-1])
            net.add_place(plc + 1)
            net.add_edge(net.transitions['tau'][-1], plc + 1)


            # exit
            net.add_transition('tau')
            trans_id = net.transitions['tau'][-1]
            connection = max(net.places.values())
            for child in self.children:
                if isinstance(child, ProcessTree):
                    child.to_petri_net(net, connection)
                net.add_edge(max(net.places.values()), trans_id)

            net.add_place(max(net.places.values()) + 1)
            net.add_edge(trans_id, max(net.places.values()))

        elif self.cut == self.miner.SEQ:
            print('(PT) SEQ')
            for child in self.children:
                plc = max(net.places.values()) + 1
                if isinstance(child, ProcessTree):
                    child.to_petri_net(net, max(net.places.values()))
                else:
                    net.add_transition(child)
                    if connection is None:
                        net.add_place(plc)
                        net.add_place(plc + 1)
                        net.add_edge(plc, net.transitions[child][-1])
                        net.add_edge(net.transitions[child][-1], plc + 1)
                    else:
                        net.add_place(plc)
                        net.add_edge(connection, net.transitions[child][-1])
                        net.add_edge(net.transitions[child][-1], plc)
                    connection = plc
        elif self.cut == self.miner.PAR:
            print('(PT) PARA')
            # plc = max(net.places.values()) + 1
            # out = plc + 1
            net.add_transition('tau')
            join_tau = net.transitions['tau'][-1]
            net.add_transition('tau')
            net.add_edge(connection, net.transitions['tau'][-1])
            for child in self.children:
                if isinstance(child, ProcessTree):
                    child.to_petri_net(net, max(net.places.values()))
                else:
                    # split
                    net.add_place(max(net.places.values()) + 1)
                    net.add_edge(net.transitions['tau'][-1], max(net.places.values()))
                    # branch
                    net.add_transition(child)
                    net.add_edge(max(net.places.values()), net.transitions[child][-1])
                    net.add_place(max(net.places.values()) + 1)
                    net.add_edge(net.transitions[child][-1], max(net.places.values()))

                # join
                net.add_edge(max(net.places.values()), join_tau)
            net.add_place(max(net.places.values()) + 1)
            net.add_edge(join_tau, max(net.places.values()))
        elif self.cut == self.miner.LOOP:
            print('(PT) LOOP')
            ingoing = connection
            for child in self.children:
                if isinstance(child, ProcessTree):
                    if child.cut == self.miner.SEQ:
                        child.to_petri_net(net, connection)
                    elif child.cut == self.miner.EXC:
                        # back loop

                        #child.to_petri_net(net, max(net.places.values()))
                        for inner_child in child.children:
                            if isinstance(inner_child, ProcessTree):
                                pass
                            else:
                                if inner_child != 'tau':
                                    net.add_transition(inner_child)
                                    net.add_edge(max(net.places.values()),
                                                    net.transitions[inner_child][-1])
                        net.add_edge(min(net.transitions.values())[-1], ingoing)
                        #pass
                else:
                    print('(PT) inner LOOP')



        return net

    def to_petri_net_new(self, net: PetriNet = None, connection: int = 1):
        if net is None:
            net = PetriNet()
            net.add_place(1)


        if self.cut == self.miner.SEQ:

            for child in self.children:
                if isinstance(child, ProcessTree):
                    print('SEQ -')
                    # net.add_transition('child')
                    # net.add_edge(connection, net.transitions['child'][-1])
                    # connection += 1
                    # net.add_place(connection)
                    # net.add_edge(net.transitions['child'][-1],  connection)
                    child.to_petri_net_new(net, net.places[max(net.places.keys())])
                else:
                    print('SEQ +')
                    net.add_transition(child)
                    net.add_edge(net.places[max(net.places.keys())] , net.transitions[child][-1])
                    net.add_place(net.places[max(net.places.keys())] + 1)
                    print(net)
                    print(net.transitions[child][-1],  net.places[max(net.places.keys())])
                    net.add_edge(net.transitions[child][-1],  net.places[max(net.places.keys())])

        elif self.cut == self.miner.PAR:
            for child in self.children:
                if isinstance(child, ProcessTree):
                    child.to_petri_net_new(net, net.places[max(net.places.keys())])
                else:
                    pass
        elif self.cut == self.miner.EXC:

            entry_place = net.places[max(net.places.keys())]
            exit_place = entry_place + 1
            for child in self.children:
                if isinstance(child, ProcessTree):
                    print('EXC -')
                    child.to_petri_net_new(net, entry_place)

                    # if(exit_place < net.places[max(net.places.keys())]):
                    #     exit_place = net.places[max(net.places.keys())]
                    # if exit_place is not net.places[max(net.places.keys())]:
                    #     net.add_place(exit_place)
                    # net.add_edge(net.transitions[child][-1], exit_place)
                else:
                    print('EXC +')
                    net.add_transition(child)
                    net.add_edge(entry_place, net.transitions[child][-1])
                    # if exit_place is not net.places[max(net.places.keys())]:
                    #     net.add_place(exit_place)
                    net.add_edge(net.transitions[child][-1], exit_place)


        elif self.cut == self.miner.LOOP:
            for child in self.children:
                if isinstance(child, ProcessTree):
                    # child.to_petri_net_new(net, connection)
                    net.add_transition('child')
                    net.add_edge(connection, net.transitions['child'][-1])
                    connection += 1
                    net.add_place(connection)
                    net.add_edge(net.transitions['child'][-1],  connection)
                else:
                    pass

        return net
