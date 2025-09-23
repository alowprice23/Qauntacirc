import gzip
import bz2
import lzma
from typing import List, Callable

class MultiCompressor:
    """
    A utility class to apply multiple compression algorithms and find the best one.
    """
    def __init__(self, compressors: List[Callable[[bytes], bytes]] = None):
        if compressors is None:
            self.compressors = [
                gzip.compress,
                bz2.compress,
                lzma.compress,
            ]
        else:
            self.compressors = compressors

    def compress(self, data: bytes) -> bytes:
        """
        Compresses data with multiple algorithms and returns the smallest result.
        """
        compressed_data = [c(data) for c in self.compressors]
        return min(compressed_data, key=len)

    def get_best_compression_size(self, data: bytes) -> int:
        """
        Returns the size of the data after compressing with the best algorithm.
        """
        return len(self.compress(data))
