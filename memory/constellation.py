class ConstellationMemory:
    def __init__(self, config):
        self.config = config

    def query(self, query):
        print(f"Querying memory with {query}")
        from datetime import datetime
        class DummyResult:
            def __init__(self, type, timestamp, summary, relevance_score):
                self.type = type
                self.timestamp = timestamp
                self.summary = summary
                self.relevance_score = relevance_score
            def to_dict(self):
                return {'type': self.type, 'timestamp': str(self.timestamp), 'summary': self.summary, 'relevance_score': self.relevance_score}
        return [DummyResult("decision", datetime.now(), "A dummy decision", 0.9)]
