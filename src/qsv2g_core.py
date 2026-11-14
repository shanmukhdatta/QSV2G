"""Compatibility module for historical notebooks/tests. New code: import qsv2g."""
import time  # legacy monkeypatch target is the same process-wide time module
from qsv2g.crypto import *
from qsv2g.quantum import *
from qsv2g.resources import *
from qsv2g.state import *
from qsv2g.protocol import *
