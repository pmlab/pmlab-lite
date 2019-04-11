"""
This package provides a class to build simple graph data structures,
like directly follows graph.
"""
from copy import copy, deepcopy
from collections import defaultdict
from pmlab_lite.pn import PetriNet


class Graph():

    def __init__(self):
        self.vertexes = defaultdict(list)
        self.start_nodes = []
        self.end_nodes = []
        self.collapsed_comp = {}

    def add_edge(self, o, t):
        if t not in self.vertexes[o]:
            self.vertexes[o].append(t)

        if t not in self.vertexes.keys():
            self.vertexes[t] = []


    def is_reachable(self, o, t):
        # set all nodes to unvisited
        nodes = list(self.vertexes.keys())
        visited = [False] * len(nodes)

        queue = []

        # vistit origin
        queue.append(o)
        visited[nodes.index(o)] = True

        while queue:
            n = queue.pop(0)
            if n == t:
                return True

            # loop all succiding vertexes
            for i in self.vertexes[n]:
                if not visited[nodes.index(i)]:
                    queue.append(i)
                    visited[nodes.index(i)] = True

        return False

    def from_log(self, log: list):
        for trace in log:
            if len(trace) >= 1:
                self.start_nodes.append(trace[0])
                self.end_nodes.append(trace[-1])
            self.from_seq(trace)

        return self

    def from_seq(self, seq: list):
        if len(seq) > 1:
            for o, t in zip(seq, seq[1:]):
                self.add_edge(o, t)
        elif len(seq) == 1:
            if seq[0] not in self.vertexes.keys():
                self.vertexes[seq[0]] = []

    def from_petrinet(self, pn: PetriNet):
        """
        Derive directly follows graph from Petri net.

        :param pn: PetriNet
        """
        l1 = list(filter(lambda x: not isinstance(x[0], int), pn.edges))
        for l in l1:
            for e in pn.edges:
                if l[1] == e[0]:
                    self.add_edge(l[0], e[1])

    def get_cc(self):

        def dfs(temp, node, visited, nodes):

            visited[nodes.index(node)] = True
            temp.append(node)

            for n in u_graph[node]:
                if visited[nodes.index(n)] == False:
                    temp = dfs(temp, n, visited, nodes)
            return temp

        cc = []

        # copy for undirected graph
        u_graph = deepcopy(self.vertexes)
        nodes = list(u_graph)
        visited = [False] * len(nodes)

        for k, v in u_graph.items():
            for n in v:
                if k not in u_graph[n]:
                    u_graph[n].append(k)

        for n in u_graph.keys():
            if visited[nodes.index(n)] == False:
                temp = []
                cc.append(dfs(temp, n, visited, nodes))

        return cc

    def get_scc(self):

        def build_stack(graph, node, nodes, visited, stack):
            if not visited[nodes.index(node)]:
                visited[nodes.index(node)] = True
                for succ in graph.vertexes[node]:
                    build_stack(graph, succ, nodes, visited, stack)

                stack.append(node)

        def transpose():
            g_t = Graph()
            for node, succ in self.vertexes.items():
                for s in succ:
                    g_t.add_edge(s, node)

            return g_t

        def visit(graph, node, nodes, visited, comp):
            if not visited[nodes.index(node)]:
                visited[nodes.index(node)] = True
                comp.append(node)
                for succ in graph.vertexes[node]:
                    visit(graph, succ, nodes, visited, comp)

        nodes = list(self.vertexes.keys())

        # 1. step
        stack = []
        visited = [False] * len(nodes)

        for n in self.vertexes:
            build_stack(self, n, nodes, visited, stack)

        # 2. step: invert graph
        g_t = transpose()

        # 3. step: find components
        visited = [False] * len(nodes)
        scc = []
        temp = []

        while stack:
            n = stack.pop()
            if not visited[nodes.index(n)]:
                visit(g_t, n, nodes, visited, temp)
                scc.append(temp)
                # reset comp
                temp = []

        return scc

    def invert_old(self):
        g_i = Graph()
        g_i.start_nodes = self.start_nodes
        g_i.end_nodes = self.end_nodes
        activities = self.vertexes.keys()
        for o in activities:
            for t in activities:
                if o != t:
                    if o not in self.vertexes[t] or t not in self.vertexes[o]:
                        g_i.add_edge(o, t)
                        g_i.add_edge(t, o)
                    else:
                        if o not in list(g_i.vertexes.keys()):
                            g_i.vertexes[o]

        return g_i

    def invert(self):
        g_i = Graph()
        g_i.start_nodes = self.start_nodes
        g_i.end_nodes = self.end_nodes
        activities = self.vertexes.keys()
        for o in activities:
            for t in activities:
                if o != t:
                    if o not in self.vertexes[t] and t in self.vertexes[o]:
                        g_i.add_edge(o, t)
                        g_i.add_edge(t, o)
                    else:
                        if o not in list(g_i.vertexes.keys()):
                            g_i.vertexes[o]

        return g_i

    # def get_start_nodes(self):
    #    nodes = list(self.vertexes.keys())
    #    succ = [act for sub in list(self.vertexes.values()) for act in sub]
    #    return list(set(nodes) - set(succ))

    # def get_end_nodes(self):
    #    return list(filter(lambda k: len(self.vertexes[k]) == 0,
    #                       self.vertexes.keys()))

    def remove_start(self):
        g_reduced = copy(self)
        new_ver = defaultdict(list)

        for node, succ in self.vertexes.items():
            if node not in self.start_nodes:
                if node not in new_ver.keys():
                    new_ver[node] = []
                for s in succ:
                    if s not in self.start_nodes:
                        new_ver[node].append(s)

        g_reduced.vertexes = new_ver

        return g_reduced

    def remove_end(self):
        g_reduced = copy(self)

        new_ver = defaultdict(list)

        for node, succ in self.vertexes.items():
            if node not in self.end_nodes:
                if node not in new_ver.keys():
                    new_ver[node] = []
                for s in succ:
                    if s not in self.end_nodes:
                        new_ver[node].append(s)

        g_reduced.vertexes = new_ver

        return g_reduced
