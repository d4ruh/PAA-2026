"""Geração dos casos de teste: amostras do enunciado + pequenos + médios + estresse."""
from __future__ import annotations

import json
import random
import shutil
import time
from pathlib import Path

from .core import Problem, write_case


def _case_rng(seed, prob: Problem, tier: str, idx: int) -> random.Random:
    return random.Random(f"{seed}|{prob.key}|{tier}|{idx}")     # str -> determinístico entre execuções


def build_cases(prob: Problem, seed: int, n_small: int, n_medium: int, scale: float):
    """Gera (yield) dicts de casos, na ordem: sample, small, medium, stress."""
    # amostras do enunciado
    for i, (args, _hint) in enumerate(prob.samples):
        exp = prob.oracle(*prob.decode(json.loads(json.dumps(args))))
        yield dict(tier="sample", kind="sample", size="ex", time_limit=prob.tl_small, args=args, expected=exp)
    def _case(tier, kind, rng, size, tl):
        if prob.normalize_kind is not None:
            kind = prob.normalize_kind(kind, size)
        args = prob.gen(rng, size, kind)
        real_size = prob.size_of(args, kind, size) if prob.size_of is not None else size
        return dict(tier=tier, kind=kind, size=real_size, time_limit=tl, args=args,
                    expected=prob.oracle(*prob.decode(args)))

    lo, hi = prob.small
    for i in range(n_small):
        kind = prob.small_kinds[i % len(prob.small_kinds)]
        rng = _case_rng(seed, prob, "small", i)
        size = rng.randint(lo, hi)
        yield _case("small", kind, rng, size, prob.tl_small)
    mkinds = prob.medium_kinds or prob.small_kinds
    for i in range(n_medium):
        kind = mkinds[i % len(mkinds)]
        rng = _case_rng(seed, prob, "medium", i)
        size = max(2, int(prob.medium * (1 if prob.fixed_size else scale)))
        size = min(size, prob.max_size)
        yield _case("medium", kind, rng, size, prob.tl)
    for i, (kind, frac) in enumerate(prob.stress):
        rng = _case_rng(seed, prob, "stress", i)
        size = max(1, int(prob.max_size * frac * (1 if prob.fixed_size else scale)))
        yield _case("stress", kind, rng, size, prob.tl)


def generate(problems, out_dir: Path, seed=2026, fmt="json", n_small=14, n_medium=4, scale=1.0, log=print):
    out_dir = Path(out_dir)
    for prob in problems:
        folder = out_dir / f"lista-{prob.lista:02d}" / prob.qid
        if folder.exists():
            shutil.rmtree(folder)
        folder.mkdir(parents=True)
        t0 = time.time()
        n = 0
        index = []
        for i, case in enumerate(build_cases(prob, seed, n_small, n_medium, scale), 1):
            case.update(lista=prob.lista, question=prob.qid, id=f"{prob.qid}_{i:03d}")
            path = write_case(folder / f"{i:03d}_{case['tier']}_{case['kind']}", case, fmt)
            index.append(dict(file=path.name, tier=case['tier'], kind=case['kind'], size=case['size'],
                              tl=case['time_limit']))
            n += 1
        (folder / "meta.json").write_text(json.dumps(
            dict(question=prob.qid, seed=seed, format=fmt, small=n_small, medium=n_medium, scale=scale, cases=n, index=index)),
            encoding="utf-8")
        log(f"  Lista {prob.lista} {prob.qid:<5} {prob.title:<42} {n:>3} casos  ({time.time() - t0:5.1f}s)")
