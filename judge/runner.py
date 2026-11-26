"""Executa casos de teste contra a solução do aluno (um subprocesso por "lote") e julga."""
from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from typing import Callable, Optional

from .core import ROOT, Problem, case_files, read_case

WORKER = Path(__file__).resolve().parent / "worker.py"
HARD_GRACE = 20.0   # folga (s) p/ o pai matar um worker travado fora do alcance do watchdog


def _read_lines(path: Path, pos: int):
    """Lê (em binário) as linhas completas novas a partir de `pos`."""
    with open(path, "rb") as f:
        f.seek(pos)
        data = f.read()
    nl = data.rfind(b"\n")
    if nl < 0:
        return [], pos
    chunk = data[: nl + 1]
    return [l for l in chunk.decode("utf-8").splitlines() if l.strip()], pos + len(chunk)


def run_cases(prob: Problem, sol: Path, paths: list, tls: list, tl_scale: float,
              on_result: Callable[[int, dict], bool]) -> None:
    """Roda `paths` em ordem. `on_result(i, raw)` é chamado a cada resultado; se retornar True, aborta."""
    idx = 0
    tmp = Path(tempfile.mkdtemp(prefix="judge_"))
    try:
        while idx < len(paths):
            batch = [{"path": str(p), "tl": t} for p, t in zip(paths[idx:], tls[idx:])]
            cases_file = tmp / "cases.json"
            out_file = tmp / f"out_{idx}.jsonl"
            err_file = tmp / f"err_{idx}.txt"
            cases_file.write_text(json.dumps(batch), encoding="utf-8")
            out_file.write_text("", encoding="utf-8")
            with open(err_file, "w") as ef:
                proc = subprocess.Popen(
                    [sys.executable, "-X", "utf8", str(WORKER), str(ROOT), str(sol), prob.key,
                     str(cases_file), str(out_file), str(tl_scale)],
                    stdout=subprocess.DEVNULL, stderr=ef, cwd=str(sol.parent))
            pos = 0
            last_progress = time.monotonic()
            got = 0          # resultados recebidos neste lote
            last_status = None
            killed_hang = False
            while True:
                finished = proc.poll() is not None      # lido ANTES de ler o arquivo (evita corrida)
                lines, pos = _read_lines(out_file, pos)
                for line in lines:
                    rec = json.loads(line)
                    last_progress = time.monotonic()
                    got = rec["i"] + 1
                    last_status = rec["status"]
                    if on_result(idx + rec["i"], rec):
                        proc.kill(); proc.wait()
                        return
                if finished:
                    break
                cur = idx + got
                if cur < len(paths) and time.monotonic() - last_progress > tls[cur] * tl_scale + HARD_GRACE:
                    proc.kill(); proc.wait()
                    killed_hang = True
                    break
                time.sleep(0.01)

            idx += got
            if idx < len(paths) and not (last_status == "TLE" and not killed_hang):
                # o worker morreu/travou sem responder o caso `idx`
                if killed_hang:
                    raw = {"i": 0, "status": "TLE", "time": tls[idx] * tl_scale}
                else:
                    tail = ""
                    try:
                        tail = Path(err_file).read_text(errors="replace")[-600:]
                    except OSError:
                        pass
                    raw = {"i": 0, "status": "RE", "time": 0.0,
                           "error": f"o processo terminou abruptamente (código {proc.returncode}) — "
                                    f"crash/estouro de pilha/memória?\n{tail}"}
                if on_result(idx, raw):
                    return
                idx += 1
    finally:
        import shutil
        shutil.rmtree(tmp, ignore_errors=True)


def judge_case(prob: Problem, path: Path, raw: dict, tl: float):
    """Converte o resultado bruto do worker em veredito: (verdict, mensagem, case_dict)."""
    case = read_case(path, with_expected=True)
    st = raw["status"]
    if st == "TLE":
        return "TLE", f"excedeu {tl:g}s", case
    if st == "RE":
        return "RE", raw.get("error", ""), case
    out = raw["output"]
    if out is None:
        return "WA", "a função retornou None (ainda não implementada?)", case
    py_args = prob.decode(case["args"])
    try:
        ok, msg = prob.check(py_args, out, case["expected"])
    except Exception as e:  # saída com formato inesperado quebrou o verificador
        ok, msg = False, f"saída com formato inválido ({type(e).__name__}: {e})"
    return ("AC" if ok else "WA"), msg, case


def load_cases(tests_dir: Path, prob: Problem, tiers: Optional[list] = None) -> list:
    """Retorna [{path, tier, kind, size, tl}] na ordem de execução (usa meta.json; aceita casos extras do usuário)."""
    folder = tests_dir / f"lista-{prob.lista:02d}" / prob.qid
    files = case_files(folder)
    meta = {}
    mp = folder / "meta.json"
    if mp.exists():
        meta = {e["file"]: e for e in json.loads(mp.read_text(encoding="utf-8")).get("index", [])}
    out = []
    for f in files:
        e = meta.get(f.name)
        if e is None:          # caso adicionado à mão: lê o cabeçalho (custa carregar o arquivo)
            c = read_case(f, with_expected=False)
            e = dict(tier=c.get("tier", "custom"), kind=c.get("kind", "custom"), size=c.get("size", "?"),
                     tl=c.get("time_limit", prob.tl))
        out.append(dict(path=f, tier=e["tier"], kind=e["kind"], size=e["size"], tl=e["tl"]))
    if tiers:
        out = [c for c in out if c["tier"] in tiers]
    return out
