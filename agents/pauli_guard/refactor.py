class RefactoringProposer:
    def generate_proposal(self, duplicate_cluster):
        return {
            'common_function': 'def common(): pass',
            'adapters': [],
            'estimated_complexity': 1
        }
