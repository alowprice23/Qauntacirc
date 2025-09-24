import re

class CNLProcessor:
    def __init__(self):
        pass

    def parse(self, text):
        """
        A simple CNL parser that splits the text into sentences.
        """
        sentences = re.split(r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?)\s', text)
        return {"sentences": sentences}
