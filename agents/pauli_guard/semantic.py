import ast
import numpy as np
import textwrap
from collections import Counter

class SemanticSimilarity:

    def _get_feature_map(self):
        # Statically define the feature space to ensure vectors are always the same size
        node_types = sorted([name for name in dir(ast) if isinstance(getattr(ast, name), type) and issubclass(getattr(ast, name), ast.AST)])
        op_types = sorted(['Add', 'Sub', 'Mult', 'Div', 'Mod', 'Pow', 'LShift', 'RShift', 'BitOr', 'BitXor', 'BitAnd', 'FloorDiv'])
        all_feature_names = sorted(list(set(node_types + op_types)))
        return {name: i for i, name in enumerate(all_feature_names)}

    def extract_features(self, code):
        feature_map = self._get_feature_map()
        feature_vector = np.zeros(len(feature_map))
        OPERATOR_WEIGHT = 10.0
        # Weight only the most semantically significant operators for this context
        op_types = {'Add', 'Mult'}

        try:
            tree = ast.parse(textwrap.dedent(code))

            # Count AST node types
            node_counts = Counter(type(node).__name__ for node in ast.walk(tree))

            # Count operators from both BinOp and AugAssign nodes
            for node in ast.walk(tree):
                if isinstance(node, (ast.BinOp, ast.AugAssign)):
                    op_name = type(node.op).__name__
                    node_counts[op_name] += 1

            # Populate the feature vector with weights
            for feature_name, count in node_counts.items():
                if feature_name in feature_map:
                    weight = OPERATOR_WEIGHT if feature_name in op_types else 1.0
                    feature_vector[feature_map[feature_name]] = count * weight

            return feature_vector

        except (SyntaxError, TypeError):
            # Return a zero vector for code that can't be parsed
            return feature_vector

    def cosine_similarity(self, v1, v2):
        v1 = np.array(v1)
        v2 = np.array(v2)

        if np.array_equal(v1, v2):
            return 1.0

        dot_product = np.dot(v1, v2)
        norm_v1 = np.linalg.norm(v1)
        norm_v2 = np.linalg.norm(v2)

        if norm_v1 == 0 or norm_v2 == 0:
            return 0.0

        return dot_product / (norm_v1 * norm_v2)

    def orthogonality_measure(self, v1, v2):
        return 1 - self.cosine_similarity(v1, v2)
