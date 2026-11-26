"""Valida o GABARITO: confere o oráculo contra (1) as saídas do enunciado e (2) a força bruta, em casos pequenos."""
from __future__ import annotations

import json
import random

from .core import Problem


def selftest_problem(prob: Problem, rounds: int = 150, seed: int = 7):
    problems = []
    # 1) exemplos do enunciado: a saída do enunciado deve ser aceita pelo verificador
    for args, hint in prob.samples:
        a = json.loads(json.dumps(args))
        py = prob.decode(a)
        exp = prob.oracle(*prob.decode(json.loads(json.dumps(args))))
        ok, msg = prob.check(py, hint, exp)
        if not ok:
            problems.append(f"exemplo do enunciado {str(args)[:70]}: saída do enunciado {hint!r} rejeitada ({msg}); "
                            f"gabarito deu {exp!r}")
    # 2) oráculo vs força bruta (e vs o próprio verificador)
    if prob.brute:
        lo, hi = prob.brute_range
        rng = random.Random(f"{seed}|{prob.key}")
        kinds = list(dict.fromkeys(prob.small_kinds + (prob.medium_kinds or []) + [k for k, _ in prob.stress]))
        for r in range(rounds):
            kind = kinds[r % len(kinds)]
            size = rng.randint(lo, hi)
            args = prob.gen(rng, size, kind)
            py = prob.decode(json.loads(json.dumps(args)))
            exp = prob.oracle(*prob.decode(json.loads(json.dumps(args))))
            bru = prob.brute(*prob.decode(json.loads(json.dumps(args))))
            if bru is NotImplemented:
                continue
            ok, msg = prob.check(py, exp, bru)       # a saída do gabarito é aceita quando comparada com a bruta?
            if not ok:
                problems.append(f"[{kind}, size={size}] gabarito={exp!r} bruta={bru!r} {msg} | args={str(args)[:150]}")
                if len(problems) >= 3:
                    break
    return problems
