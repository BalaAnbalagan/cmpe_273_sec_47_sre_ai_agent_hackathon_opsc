import os
import sys

# Include backend folder in Python path
sys.path.append(os.path.dirname(__file__))

from api.main import app

__all__ = ["app"]
