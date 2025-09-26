from collections import Counter
from datetime import datetime
from typing import List, Dict, Any, TYPE_CHECKING

if TYPE_CHECKING:
    from .constellation import ConstellationMemory


class DiscoveredPattern:
    """
    Represents a discovered pattern in the knowledge graph.
    """
    def __init__(self, description: str, frequency: int, confidence: float, last_seen: datetime, nodes: List[Dict[str, Any]]):
        self.description = description
        self.frequency = frequency
        self.confidence = confidence
        self.last_seen = last_seen
        self.nodes = nodes

    def to_dict(self):
        return {
            "description": self.description,
            "frequency": self.frequency,
            "confidence": self.confidence,
            "last_seen": str(self.last_seen),
            "nodes": self.nodes,
        }


class PatternAnalyzer:
    """
    Analyzes the knowledge graph to discover recurring patterns and relationships.
    """
    def __init__(self, memory: 'ConstellationMemory'):
        self.memory = memory

    def analyze_common_relationships(self, domain: str = None, time_range: tuple = None, min_frequency: int = 2) -> List[DiscoveredPattern]:
        """
        Finds the most common relationships (edge types) between fact types within a given time range.
        """
        graph = self.memory.graph

        target_nodes = set(graph.nodes())
        if domain:
            target_nodes = {n for n, data in graph.nodes(data=True) if domain in data.get('type', '')}

        if not target_nodes:
            return []

        relationship_counts = Counter()
        edge_timestamps = {}

        start_date, end_date = time_range if time_range else (None, None)

        for u, v, data in graph.edges(data=True):
            edge_timestamp = data.get('timestamp')
            if start_date and (not edge_timestamp or edge_timestamp < start_date):
                continue
            if end_date and (not edge_timestamp or edge_timestamp > end_date):
                continue

            if u in target_nodes and v in target_nodes:
                source_node = graph.nodes[u]
                target_node = graph.nodes[v]

                pattern_key = (
                    source_node.get('type', 'unknown'),
                    data.get('label', 'related_to'),
                    target_node.get('type', 'unknown')
                )
                relationship_counts[pattern_key] += 1

                timestamp = data.get('timestamp', datetime.min)
                if pattern_key not in edge_timestamps or timestamp > edge_timestamps[pattern_key]:
                    edge_timestamps[pattern_key] = timestamp

        patterns = []
        for pattern, freq in relationship_counts.items():
            if freq >= min_frequency:
                source_type, label, target_type = pattern
                description = f"Pattern: '{source_type}' nodes are often linked to '{target_type}' nodes via '{label}' relationship."

                confidence = 0.8  # Placeholder for a more advanced confidence metric
                last_seen = edge_timestamps.get(pattern, datetime.utcnow())

                example_nodes = []
                for u, v, data in graph.edges(data=True):
                    if u in target_nodes and v in target_nodes:
                        source_node = graph.nodes[u]
                        target_node = graph.nodes[v]
                        current_pattern_key = (source_node.get('type', 'unknown'), data.get('label', 'related_to'), target_node.get('type', 'unknown'))
                        if current_pattern_key == pattern:
                            example_nodes.append({'source': source_node, 'target': target_node})
                            if len(example_nodes) >= 3:
                                break

                patterns.append(DiscoveredPattern(
                    description=description,
                    frequency=freq,
                    confidence=confidence,
                    last_seen=last_seen,
                    nodes=example_nodes
                ))

        patterns.sort(key=lambda p: p.frequency, reverse=True)
        return patterns

    def analyze_pattern_evolution(self, domain: str, time_span_months: int = 6, frequency: str = "monthly"):
        """
        Analyzes how patterns have evolved over a given time span.
        """
        from dateutil.relativedelta import relativedelta

        timeline = {}
        end_date = datetime.utcnow()

        if frequency == "monthly":
            step = relativedelta(months=1)
            start_date = end_date - relativedelta(months=time_span_months)
        else: # Default to monthly
            step = relativedelta(months=1)
            start_date = end_date - relativedelta(months=time_span_months)

        current_date = start_date
        while current_date < end_date:
            window_end = current_date + step
            patterns = self.analyze_common_relationships(domain=domain, time_range=(current_date, window_end))

            # Use ISO format for dict key
            timeline_key = current_date.strftime('%Y-%m')
            timeline[timeline_key] = [p.to_dict() for p in patterns]

            current_date = window_end

        return timeline

    def analyze(self, analysis_type: str, time_range=None, domain=None, time_span_months: int = 6, frequency: str = "monthly"):
        """
        Main entry point for pattern analysis.
        """
        if analysis_type == "common_relationships":
            return self.analyze_common_relationships(domain=domain, time_range=time_range)
        elif analysis_type == "evolution":
            return self.analyze_pattern_evolution(domain=domain, time_span_months=time_span_months, frequency=frequency)
        else:
            return []