from pmlab_lite.helper.graph import Graph


def find_scc(graph: Graph):


	def visit(n, v, s, g):
		if not v[n]:
			print(n)
			v[n] = True
			for i in g[n]:
				visit(i, v, s, g)
			s.append(n)


	stack = []
	visited = [False] * len(graph.graph)

	for node in graph.graph:
		visit(node, visited, stack, graph.graph)
		# if not visited[node]:
		# 	visited[node] = True
		# 	children = graph.graph[node]
		# 	for c in children:
	print(stack)

