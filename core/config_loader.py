from .types import QuantaCircConfig

def load_config(path):
    print(f"Loading config from {path}")
    return QuantaCircConfig()
