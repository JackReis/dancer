"""Pytest bootstrap: make the plugin root importable so `from quad_memory...` resolves.

The plugin directory is the package parent of `quad_memory/`. Inserting it onto
sys.path lets `pytest tests/` run from the plugin root without an installed package.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
