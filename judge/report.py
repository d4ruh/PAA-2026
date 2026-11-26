"""Impressão dos resultados (estilo LeetCode)."""
from __future__ import annotations

import os
import sys

from .core import trunc

COLORS = {"AC": "32", "WA": "31", "TLE": "33", "RE": "35", "dim": "2", "bold": "1", "cyan": "36"}


class Out:
    def __init__(self, color: bool = True):
        self.color = color and sys.stdout.isatty() and not os.environ.get("NO_COLOR")
        if self.color and os.name == "nt":
            os.system("")      # habilita ANSI no console do Windows 10+

    def c(self, text: str, key: str) -> str:
        return f"\033[{COLORS[key]}m{text}\033[0m" if self.color else text

    def v(self, verdict: str) -> str:
        return self.c(f"{verdict:<3}", verdict)


def human_time(t: float) -> str:
    return f"{t * 1000:7.1f}ms" if t < 1 else f"{t:7.3f}s "
