from pmlab_lite.helper.graph import Graph

def scc(g: Graph):
    """
    Find all strongly connected components in a given graph.

    Args:
        g: Graph

    Return:
        return: List of strongly connected components
    """

    mapping = {}

    def map_nodes():
        """
        Maps each node label to an numeric representation.
        """
        for node in g.graph:
            if node not in mapping.keys():
                mapping[node] = len(mapping)

    def transpose(graph: Graph):
        """
        Invert all edges of the given graph.

        Args:
        	graph: Graph

        Return:
        	retrun: Graph
        """

        graph_t = Graph()
        for n in graph.graph:
            for c in graph.graph[n]:
                graph_t.add_edge(c, n)
        return graph_t

    def build_stack(graph, node, visited, stack):
        """
        Build stack of nodes using deep first search.

        Args:
        	graph: Graph
        	node: integer number of current node
        	visited: list of boolean
        	stack: list of visited nodes
        """

        if not visited[node - 1]:
            visited[node - 1] = True
            for successor in graph.graph[node]:
                build_stack(graph, successor, visited, stack)
            stack.append(node)

    def visit(graph, node, visited, component):
        """
        Collect nodes, that belong to the same strongly connected component.

        Args:
        	graph: Graph
        	node: integer number of current node
        	visited: list of boolean
        	component: list of nodes
        """

        if not visited[node - 1]:
            visited[node - 1] = True
            component.append(node)
            for successor in graph.graph[node]:
                visit(graph, successor, visited, component)

    # === Algorithm ===

    # first map all nodes to an numeric representation and build a new graph
    map_nodes()
    graph_mapped = Graph()
    for n in g.graph:
        for c in g.graph[n]:
            graph_mapped.add_edge(mapping[n], mapping[c])

    # 1. step: build stack
    stack = []
    visited = [False] * (len(g.graph) + 1)
    for n in graph_mapped.graph:
        build_stack(graph_mapped, n, visited, stack)

    # 2. step: transpose graph
    graph_t = transpose(graph_mapped)

    # 3. step: find scc
    visited = [False] * (len(g.graph) + 1)
    result = []
    component = []
    while stack:
        node = stack.pop()
        if visited[node - 1] is False:
            visit(graph_t, node, visited, component)
            result.append(component)
            component = []

    # 4. step: invert mapping
    inv_mapping = {v: k for k, v in mapping.items()}
    result_mapped = []
    for comp in result:
        temp = []
        for node in comp:
            temp.append(inv_mapping[node])
        result_mapped.append(temp)

    # return result
    return result_mapped