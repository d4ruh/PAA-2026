"""Processo-filho que executa a solução do aluno sobre uma sequência de casos.

Uso (interno): python worker.py <root> <solucao.py> <problem_key> <cases.json> <out.jsonl> <tl_scale>

- A saída do aluno (prints) é descartada; o resultado vai para <out.jsonl> (uma linha por caso).
- O gabarito NUNCA é carregado aqui (só os argumentos).
- Um watchdog em thread encerra o processo (os._exit) ao estourar o limite -> TLE.
- O tempo medido é só o da chamada da função (sem import, sem leitura do JSON).
"""
import importlib.util
import json
import os
import sys
import threading
import time
import traceback
from pathlib import Path


def main() -> None:
    root, sol, key, cases_file, out_file, tl_scale = sys.argv[1:7]
    tl_scale = float(tl_scale)
    sys.path.insert(0, root)
    from judge.core import read_case
    from judge.problems import get_by_key

    prob = get_by_key(key)
    with open(cases_file, encoding="utf-8") as f:
        cases = json.load(f)

    out = open(out_file, "a", encoding="utf-8")
    lock = threading.Lock()

    def emit(rec):
        out.write(json.dumps(rec) + "\n")
        out.flush()

    real_stdout = sys.stdout
    devnull = open(os.devnull, "w", encoding="utf-8")
    sys.stdout = devnull

    # --- importa a solução do aluno -------------------------------------------------
    try:
        sys.path.insert(0, str(Path(sol).parent))
        spec = importlib.util.spec_from_file_location("student_solution", sol)
        mod = importlib.util.module_from_spec(spec)
        sys.modules["student_solution"] = mod
        spec.loader.exec_module(mod)
        if not hasattr(mod, prob.func):
            raise AttributeError(f"'{prob.func}' não existe em {Path(sol).name}")
    except BaseException:
        tb = traceback.format_exc()
        for i in range(len(cases)):
            emit({"i": i, "status": "RE", "time": 0.0, "error": "erro ao importar a solução:\n" + tb[-1200:]})
        return

    # --- executa os casos ----------------------------------------------------------
    for i, c in enumerate(cases):
        case = read_case(Path(c["path"]), with_expected=False)
        args = prob.decode(case["args"])
        del case
        limit = c["tl"] * tl_scale
        state = {"done": False}

        def on_timeout(i=i, limit=limit, state=state):
            with lock:
                if state["done"]:
                    return
                state["done"] = True
                emit({"i": i, "status": "TLE", "time": limit})
            os._exit(0)

        timer = threading.Timer(limit, on_timeout)
        timer.daemon = True
        err = None
        res = None
        timer.start()
        t0 = time.perf_counter()
        try:
            res = prob.run(mod, args)
        except BaseException as e:  # RecursionError, MemoryError, SystemExit, ...
            err = "".join(traceback.format_exception(type(e), e, e.__traceback__))
        elapsed = time.perf_counter() - t0
        with lock:
            if state["done"]:          # o watchdog já respondeu e está encerrando o processo
                time.sleep(60)
            state["done"] = True
        timer.cancel()

        if err is not None:
            emit({"i": i, "status": "RE", "time": elapsed, "error": err[-1500:]})
        elif elapsed > limit:
            emit({"i": i, "status": "TLE", "time": elapsed})
        else:
            try:
                json.dumps(res)
            except (TypeError, ValueError) as e:
                emit({"i": i, "status": "RE", "time": elapsed,
                      "error": f"saída não serializável ({type(res).__name__}): {e}"})
            else:
                emit({"i": i, "status": "OK", "time": elapsed, "output": res})
        del args, res


if __name__ == "__main__":
    main()
