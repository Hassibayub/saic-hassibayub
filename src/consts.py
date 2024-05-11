import os
from pathlib import Path

ROOT_DIR = Path(os.path.dirname(os.path.abspath(__file__))).parent
DATA_DIR = os.path.join(ROOT_DIR, 'data')
CHROMA_DB_PATH = os.path.join(ROOT_DIR, 'index')