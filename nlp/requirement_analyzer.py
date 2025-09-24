import re

class RequirementAnalyzer:
    def __init__(self):
        pass

    def analyze(self, text):
        """
        A simple requirement analyzer that counts the number of sentences and words.
        """
        sentences = re.split(r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?)\s', text)
        words = text.split()
        return {"sentence_count": len(sentences), "word_count": len(words)}
