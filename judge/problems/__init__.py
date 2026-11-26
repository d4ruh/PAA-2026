"""Registro dos problemas.  ⚠ Os módulos lista01/lista02 contêm o GABARITO (soluções de referência)."""
from .lista01 import PROBLEMS as P1
from .lista02 import PROBLEMS as P2

ALL = P1 + P2


def get_by_key(key: str):
    for p in ALL:
        if p.key == key:
            return p
    raise KeyError(key)


def select(listas=None, qids=None):
    out = [p for p in ALL if (not listas or p.lista in listas)]
    if qids:
        wanted = {q.lower().replace("question_", "q") for q in qids}
        out = [p for p in out if p.qid in wanted]
    return out
