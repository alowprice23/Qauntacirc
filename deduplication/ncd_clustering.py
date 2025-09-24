import numpy as np

class NCDClustering:
    def __init__(self, threshold=0.5):
        self.threshold = threshold

    def ncd(self, x, y):
        """
        A simple Normalized Compression Distance (NCD) based on length.
        """
        len_x = len(x)
        len_y = len(y)
        # A mock compression, just using the length
        len_xy = len(x) + len(y)
        return (len_xy - min(len_x, len_y)) / max(len_x, len_y)

    def cluster(self, items):
        """
        A simple NCD clustering algorithm.
        """
        clusters = []
        for item in items:
            if not clusters:
                clusters.append([item])
                continue

            # Find the best cluster for the item
            best_cluster = None
            min_dist = float('inf')
            for i, cluster in enumerate(clusters):
                dist = self.ncd(item, cluster[0])
                if dist < min_dist:
                    min_dist = dist
                    best_cluster = i

            if min_dist < self.threshold:
                clusters[best_cluster].append(item)
            else:
                clusters.append([item])

        return {"clusters": clusters}
