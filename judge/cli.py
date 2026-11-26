"""CLI:  python -m judge {list,gen,run,scaling,selftest} ..."""
from __future__ import annotations

import argparse
import math
import sys
import tempfile
import time
from pathlib import Path

from .core import ROOT, find_solution, read_case, trunc, write_case
from .gen import generate
from .problems import select
from .report import Out, human_time
from .runner import judge_case, load_cases, run_cases
from .selftest import selftest_problem


def _add_filters(p):
    p.add_argument("--lista", "-l", type=int, nargs="+", choices=[1, 2], help="listas (padrão: todas)")
    p.add_argument("--q", "-q", nargs="+", help="questões, ex.: q2 q7_a q8_a")


def _probs(a):
    ps = select(a.lista, a.q)
    if not ps:
        sys.exit("Nenhuma questão corresponde ao filtro. Use `python -m judge list`.")
    return ps


# ---------------------------------------------------------------------------
def cmd_list(a):
    for p in select(a.lista, a.q):
        print(f"Lista {p.lista}  {p.qid:<5} {p.func:<14} {p.title:<44} {p.complexity:<18} n_max={p.max_size:<8} TL={p.tl:g}s")


def cmd_gen(a):
    ps = _probs(a)
    t0 = time.time()
    print(f"Gerando casos (seed={a.seed}, formato={a.format}, scale={a.scale}) em {a.out}/")
    generate(ps, Path(a.out), a.seed, a.format, a.small, a.medium, a.scale)
    print(f"Pronto em {time.time() - t0:.1f}s.")


def cmd_selftest(a):
    bad = 0
    for p in _probs(a):
        issues = selftest_problem(p, a.rounds)
        print(f"  Lista {p.lista} {p.qid:<5} {'OK' if not issues else 'FALHOU'}")
        for i in issues:
            print("     -", i)
        bad += bool(issues)
    return 1 if bad else 0


def _show_failure(o: Out, verdict, msg, case, raw, prob):
    pad = "        "
    print(pad + o.c("Input:   ", "dim") + trunc(case["args"], 400))
    if verdict == "WA":
        print(pad + o.c("Esperado:", "dim") + " " + trunc(case["expected"], 300))
        print(pad + o.c("Obtido:  ", "dim") + " " + trunc(raw.get("output"), 300))
    if msg:
        for line in str(msg).strip().splitlines()[-12:]:
            print(pad + o.c("> ", "dim") + line)


def cmd_run(a):
    o = Out(not a.no_color)
    tests = Path(a.tests)
    ps = _probs(a)
    summary = []
    if a.file and len({p.lista for p in ps}) > 1:
        sys.exit("--file só pode ser usado com uma única lista (use --lista).")
    for p in ps:
        sol = find_solution(p.lista, ROOT, a.file)
        cases = load_cases(tests, p, a.tier)
        print()
        print(o.c(f"=== Lista {p.lista} · {p.qid.upper()} — {p.title}   [{p.complexity}]", "bold"))
        if not cases:
            print(f"  (sem casos em {tests}/lista-{p.lista:02d}/{p.qid} — rode `python -m judge gen`)")
            summary.append((p, 0, 0, 0.0, "SEM CASOS"))
            continue
        state = dict(ok=0, maxt=0.0, first=None, shown=False)

        def on_result(i, raw, p=p, cases=cases, state=state):
            c = cases[i]
            tl = c["tl"] * a.tl_scale
            verdict, msg, case = judge_case(p, c["path"], raw, tl)
            t = raw.get("time", 0.0)
            if verdict == "AC":
                state["ok"] += 1
            elif state["first"] is None:
                state["first"] = (i + 1, verdict)
            if verdict != "TLE":
                state["maxt"] = max(state["maxt"], t)
            else:
                state["maxt"] = max(state["maxt"], tl)
            tstr = ("   >" + f"{tl:g}s") if verdict == "TLE" else human_time(t)
            print(f"  #{i + 1:02d} {c['tier']:<6} {str(c['kind']):<12} n={str(c['size']):<8} {o.v(verdict)} {tstr}")
            if verdict != "AC" and (a.verbose or not state["shown"]):
                state["shown"] = True
                _show_failure(o, verdict, msg, case, raw, p)
            return a.fail_fast and verdict != "AC"

        run_cases(p, sol, [c["path"] for c in cases], [c["tl"] for c in cases], a.tl_scale, on_result)
        done = state["ok"] == len(cases)
        final = "AC" if done else (state["first"][1] if state["first"] else "?")
        label = "Accepted" if done else f"Falhou no caso #{state['first'][0]} ({final})" if state["first"] else "Incompleto"
        print("  " + o.c(f"-> {label}: {state['ok']}/{len(cases)} casos | tempo máx {human_time(state['maxt']).strip()}",
                         "AC" if done else final if final in ("WA", "TLE", "RE") else "WA"))
        summary.append((p, state["ok"], len(cases), state["maxt"], "AC" if done else final))

    print()
    print(o.c("=" * 72, "dim"))
    print(f"{'Questão':<8}{'Título':<46}{'Casos':>8}{'T.máx':>9}  Resultado")
    for p, ok, n, mt, res in summary:
        print(f"{p.qid:<8}{p.title[:44]:<46}{f'{ok}/{n}':>8}{mt:>8.2f}s  {o.c(res, res) if res in COLOR_KEYS else res}")
    tot_ok = sum(1 for s in summary if s[4] == "AC")
    print(f"\n{tot_ok}/{len(summary)} questões aceitas.")
    return 0 if tot_ok == len(summary) else 1


COLOR_KEYS = ("AC", "WA", "TLE", "RE")


# ---------------------------------------------------------------------------
def _fit_slope(pts):
    pts = [(math.log(n), math.log(t)) for n, t in pts if t >= 0.004 and n > 1]
    if len(pts) < 2:
        return None
    mx = sum(x for x, _ in pts) / len(pts)
    my = sum(y for _, y in pts) / len(pts)
    den = sum((x - mx) ** 2 for x, _ in pts)
    return sum((x - mx) * (y - my) for x, y in pts) / den if den else None


def cmd_scaling(a):
    """Mede o tempo em tamanhos crescentes e estima o expoente (regressão log-log)."""
    import random
    o = Out(not a.no_color)
    print("Modo scaling: estima o crescimento do tempo (t ~ n^expoente) com 4 tamanhos. É uma ESTIMATIVA —")
    print("ruído de máquina e constantes do Python influenciam; use como alerta, não como prova.\n")
    for p in _probs(a):
        if p.slope is None:
            print(f"Lista {p.lista} {p.qid}: sem modelo de escalonamento (sizes pequenos/limitados) — pulei.")
            continue
        sol = find_solution(p.lista, ROOT, a.file)
        fracs = [0.125, 0.25, 0.5, 1.0]
        sizes = sorted({max(2, int(p.max_size * f * a.scale)) for f in fracs})
        print(o.c(f"=== Lista {p.lista} · {p.qid.upper()} — {p.title}   [{p.complexity}]  (kind={p.scale_kind})", "bold"))
        reps = 3
        with tempfile.TemporaryDirectory(prefix="judge_scale_") as td:
            paths, tls = [], []
            for n in sizes:
                rng = random.Random(f"scaling|{p.key}|{n}")
                args = p.gen(rng, n, p.scale_kind)
                f = write_case(Path(td) / f"s{n}", dict(lista=p.lista, question=p.qid, id=f"s{n}", tier="scale",
                                                        kind=p.scale_kind, size=n, time_limit=a.tl,
                                                        args=args, expected=None), "json")
                paths += [f] * reps
                tls += [a.tl] * reps
            res = {}

            def on_result(i, raw):
                res[i] = raw
                return False
            run_cases(p, sol, paths, tls, 1.0, on_result)
        pts, aborted = [], False
        for k, n in enumerate(sizes):
            rs = [res.get(k * reps + j) for j in range(reps)]
            ts = [r["time"] for r in rs if r and r["status"] == "OK"]
            bad = [r for r in rs if r and r["status"] in ("RE", "TLE")]
            if bad:
                st = bad[0]["status"]
                print(f"   n={n:<8} {o.c(st, st)} {('> %gs' % a.tl) if st == 'TLE' else ''}")
                if st == "RE":
                    print("        " + str(bad[0].get("error", "")).strip().splitlines()[-1])
                aborted = True
                break
            if not ts:
                aborted = True
                break
            pts.append((n, min(ts)))
            print(f"   n={n:<8} {human_time(min(ts))}")
        if aborted:
            print("   -> medição interrompida (erro/timeout)\n")
            continue
        s = _fit_slope(pts)
        if s is None:
            print("   -> inconclusivo (execução muito rápida para medir; bom sinal)\n")
        elif s <= p.slope:
            print("   " + o.c(f"-> OK: crescimento ~ n^{s:.2f} (tolerado até n^{p.slope:g}) — compatível com {p.complexity}", "AC") + "\n")
        else:
            print("   " + o.c(f"-> SUSPEITO: crescimento ~ n^{s:.2f}, esperado ≲ n^{p.slope:g} para {p.complexity}", "TLE") + "\n")
    return 0


# ---------------------------------------------------------------------------
def main(argv=None):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    ap = argparse.ArgumentParser(prog="python -m judge", description="Gerador de casos + juiz (corretude e tempo) — PAA")
    sub = ap.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("list", help="lista as questões"); _add_filters(s); s.set_defaults(fn=cmd_list)

    s = sub.add_parser("gen", help="gera os casos de teste")
    _add_filters(s)
    s.add_argument("--out", default=str(ROOT / "tests"), help="pasta de saída (padrão: <raiz>/tests)")
    s.add_argument("--seed", type=int, default=2026)
    s.add_argument("--format", choices=["json", "txt"], default="json")
    s.add_argument("--small", type=int, default=14, help="nº de casos pequenos por questão")
    s.add_argument("--medium", type=int, default=4, help="nº de casos médios por questão")
    s.add_argument("--scale", type=float, default=1.0, help="multiplica o tamanho dos casos médios/estresse")
    s.set_defaults(fn=cmd_gen)

    s = sub.add_parser("run", help="julga a sua solução")
    _add_filters(s)
    s.add_argument("--tests", default=str(ROOT / "tests"))
    s.add_argument("--file", help="caminho do .py da solução (padrão: lista-0X/…-paa.py)")
    s.add_argument("--tl-scale", type=float, default=1.0, help="multiplica todos os limites de tempo")
    s.add_argument("--tier", nargs="+", choices=["sample", "small", "medium", "stress"], help="roda só estes grupos")
    s.add_argument("--fail-fast", action="store_true", help="para no primeiro caso que falhar (como o LeetCode)")
    s.add_argument("--verbose", "-v", action="store_true", help="detalha TODAS as falhas")
    s.add_argument("--no-color", action="store_true")
    s.set_defaults(fn=cmd_run)

    s = sub.add_parser("scaling", help="estima a complexidade empírica (tempo x tamanho)")
    _add_filters(s)
    s.add_argument("--file")
    s.add_argument("--scale", type=float, default=1.0)
    s.add_argument("--tl", type=float, default=60.0, help="limite (s) por execução")
    s.add_argument("--no-color", action="store_true")
    s.set_defaults(fn=cmd_scaling)

    s = sub.add_parser("selftest", help="valida o gabarito do juiz contra força bruta")
    _add_filters(s)
    s.add_argument("--rounds", type=int, default=150)
    s.set_defaults(fn=cmd_selftest)

    a = ap.parse_args(argv)
    return a.fn(a) or 0
