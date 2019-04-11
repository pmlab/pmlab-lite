from enum import Enum

from pmlab_lite.discovery.process_tree import ProcessTree
from pmlab_lite.log import EventLog
from pmlab_lite.discovery.process_tree_OLD import ProcessTreeOLD

# class Cut(Enum):
#     SEQ = 1
#     PAR = 2
#     EXC = 3
#     LOOP = 4

class InductiveMinerOLD():


    def __init__(self, log: EventLog):
        self.log = self.prepare_log(log)

        # cut constants
        self.SEQ = 1
        self.PAR = 2
        self.EXC = 3
        self.LOOP = 4

    def discover(self) -> ProcessTree:
        return ProcessTree(self, self.log)

    def prepare_log(self, event_log: EventLog) -> list:
        log = []
        for trace in event_log.get_traces():
            red_trace = []
            [red_trace.append(event['activity_name']) for event in trace]
            log.append(red_trace)
        return log

    def split_log(self, log, argument, cut):
        if cut == self.SEQ:
            L1 = []
            L2 = []
            # print('(IM) seq_cut %s' % argument)
            for trace in log:
                cut_idx = []
                # find cut position
                for arg in argument:
                    if arg in trace:
                        i = len(trace) - 1 - trace[::-1].index(arg)
                        cut_idx.append(i)
                # print(trace, cut_idx)
                if len(cut_idx) > 0:  # some event in trace
                    if trace[:max(cut_idx) + 1] not in L1:
                        L1.append(trace[:max(cut_idx) + 1])
                    L2.append(trace[max(cut_idx) + 1:])
                else:
                    if [] not in L1:
                        L1.append([])
                    if trace not in L2:
                        L2.append(trace)
            # print('(IM) logs %s' % [L1, L2])
            return [L1, L2]
        # ------------------------------------
        elif cut == self.PAR:
            # print('(IM) para_cut %s' %argument)
            log_collectiong = [[] for _ in range(len(argument))]
            for trace in log:
                for idx, arg in enumerate(argument):
                    if arg[0] in trace:
                        s_idx = trace.index(arg[0])
                        e_idx = trace.index(arg[-1]) + 1
                        if trace[s_idx:e_idx] not in log_collectiong[idx]:
                            log_collectiong[idx].append(trace[s_idx:e_idx])
                    else:
                        log_collectiong[idx].append([])
            # print('(IM) par logs %s' % log_collectiong)
            return log_collectiong
        # ------------------------------------
        elif cut == self.EXC:
            log_collectiong = [[] for _ in range(len(argument))]
            for trace in log:
                for idx, arg in enumerate(argument):
                    if any([item in trace for item in arg]):
                        # if all(event in arg for event in trace):
                        log_collectiong[idx].append(trace)
            return log_collectiong
        # ------------------------------------
        elif cut == self.LOOP:
            '''
            argument = [[forward], [backward]]
            '''
            log_collectiong = [[] for _ in range(len(argument))]
            for trace in log:
                for idx, arg in enumerate(argument):
                    if arg[0] in trace:
                        s_idx = trace.index(arg[0])
                        e_idx = trace.index(arg[-1]) + 1
                        if trace[s_idx:e_idx] not in log_collectiong[idx]:
                            log_collectiong[idx].append(trace[s_idx:e_idx])
                    else:
                        log_collectiong[idx].append([])
            print('(IM) loop logs %s' % log_collectiong)
            return log_collectiong
        else:
            # trivial cut
            pass

    def print_cut(self, cut: int) -> str:
        if cut == self.SEQ:
            return 'SEQ'
        elif cut == self.PAR:
            return 'PAR'
        elif cut == self.EXC:
            return 'EXL'
        elif cut == self.LOOP:
            return 'LOOP'
