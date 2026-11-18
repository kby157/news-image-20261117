"""news-image-20261117: copy the front-page PNG to the grader output path.

Deterministic: identical bytes every run. No network. Standard library only.
"""
from __future__ import annotations

import os
import shutil

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "entry.png")
OUT = os.path.join(os.environ.get("MAKEFUN_OUTPUT_DIR", "/output"), "entry.png")

os.makedirs(os.path.dirname(OUT) or ".", exist_ok=True)
shutil.copyfile(SRC, OUT)
