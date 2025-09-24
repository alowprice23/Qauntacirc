import math
from collections import Counter

class BleuValidator:
    def __init__(self):
        pass

    def validate(self, reference, candidate):
        """
        A simple implementation of the BLEU score.
        """
        # Brevity penalty
        ref_len = len(reference)
        can_len = len(candidate)
        if can_len == 0:
            return 0.0
        bp = 1.0 if can_len > ref_len else math.exp(1 - ref_len / can_len)

        # N-gram precision
        p_n = []
        for n in range(1, 5):
            ref_ngrams = Counter(zip(*[reference[i:] for i in range(n)]))
            can_ngrams = Counter(zip(*[candidate[i:] for i in range(n)]))
            clipped_ngrams = can_ngrams & ref_ngrams
            p_n.append(sum(clipped_ngrams.values()) / max(1, sum(can_ngrams.values())))

        return bp * math.exp(sum(math.log(p) if p > 0 else -9999 for p in p_n) / 4)
