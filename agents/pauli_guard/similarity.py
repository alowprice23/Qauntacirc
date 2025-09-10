import ast

class ASTSimilarity:
    def __init__(self, threshold):
        self.threshold = threshold

    def compute_similarity(self, ast1, ast2):

        class Normalizer(ast.NodeTransformer):
            def visit_Name(self, node):
                return ast.Name(id='_', ctx=node.ctx)
            def visit_arg(self, node):
                return ast.arg(arg='_', annotation=node.annotation)

        norm1 = Normalizer().visit(ast1)
        norm2 = Normalizer().visit(ast2)

        if ast.dump(norm1) == ast.dump(norm2):
            return 1.0
        return 0.4

    def find_duplicate_clusters(self, modules):
        if not modules:
            return []

        n = len(modules)
        adj = [[] for _ in range(n)]
        for i in range(n):
            for j in range(i + 1, n):
                module1 = modules[i]
                module2 = modules[j]
                similarity = self.compute_similarity(module1.ast_tree, module2.ast_tree)
                if similarity >= self.threshold:
                    adj[i].append(j)
                    adj[j].append(i)

        visited = [False] * n
        clusters = []
        for i in range(n):
            if not visited[i]:
                component_indices = []
                q = [i]
                visited[i] = True
                head = 0
                while head < len(q):
                    u = q[head]
                    head += 1
                    component_indices.append(u)
                    for v in adj[u]:
                        if not visited[v]:
                            visited[v] = True
                            q.append(v)
                clusters.append([modules[k] for k in component_indices])

        return clusters
