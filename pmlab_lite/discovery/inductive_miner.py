SEQ = 1
PAR = 2
EXC = 3
LOOP = 4


def split_log(log, argument, cut):
    if cut == SEQ:
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
                L1.append([])
                L2.append(trace)
        # print('(IM) logs %s' % [L1, L2])
        return [L1, L2]
    # ------------------------------------
    elif cut == PAR:
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
    elif cut == EXC:
        log_collectiong = [[] for _ in range(len(argument))]
        for trace in log:
            for idx, arg in enumerate(argument):
                if any([item in trace for item in arg]):
                    # if all(event in arg for event in trace):
                    log_collectiong[idx].append(trace)
        return log_collectiong
    # ------------------------------------
    elif cut == LOOP:
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


def print_cut(cut):
    if cut == SEQ:
        return 'SEQ'
    elif cut == PAR:
        return 'PAR'
    elif cut == EXC:
        return 'EXL'
    elif cut == LOOP:
        return 'LOOP'
