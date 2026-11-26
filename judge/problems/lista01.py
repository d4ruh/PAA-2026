"""
Lista 1 — gabarito, geradores e verificadores.

⚠ SPOILER: este arquivo contém soluções de referência (necessárias para calcular a saída esperada
dos casos grandes). Se quiser estudar sem ver as respostas, não abra este arquivo: o comando
`python -m judge gen` já grava as saídas esperadas junto dos casos.

Convenção dos geradores:  gen(rng, size, kind) -> lista de argumentos da função (JSON-ável)
"""
from __future__ import annotations

import bisect
import heapq
from collections import Counter, OrderedDict, deque

from ..core import Problem

PROBLEMS: list = []


def reg(p: Problem) -> Problem:
    PROBLEMS.append(p)
    return p


# =============================================================================
# Q2 — Painel de Sensores: k-ésimo menor em matriz com linhas/colunas crescentes
# =============================================================================
def q2_gen(rng, n, kind):
    n = max(1, n)
    cnt = n * n
    pool = range(1, 3 * cnt + 1) if kind == "dense" else range(-10**9, 10**9 + 1)
    vals = rng.sample(pool, cnt)                      # valores distintos
    rows = [sorted(vals[i * n:(i + 1) * n]) for i in range(n)]
    grid = [list(r) for r in zip(*[sorted(c) for c in zip(*rows)])]   # ordena colunas: linhas continuam ordenadas
    k = {"k_first": 1, "k_last": cnt}.get(kind) or rng.randint(1, cnt)
    return [grid, k]


def q2_oracle(grade, k):
    return sorted(x for row in grade for x in row)[k - 1]


def q2_brute(grade, k):
    return heapq.nsmallest(k, [x for row in grade for x in row])[-1]


reg(Problem(
    1, "q2", "question_2", "Painel de Sensores", "O(n log D)", q2_gen, q2_oracle,
    samples=[([[(2, 6, 9), (8, 9, 12), (11, 13, 14)], 5], 9),
             ([[(2, 6, 9), (8, 9, 12), (11, 13, 14)], 1], 2),
             ([[(-15, -10, -5), (-12, -8, -2), (-9, -4, 0)], 4], -9),
             ([[(-10, -5, 2), (-4, 0, 6), (1, 5, 10)], 7], 5)],
    max_size=1000, tl=0.5, small=(1, 6), medium=150,
    small_kinds=["wide", "dense", "k_first", "k_last"],
    stress=[("wide", 1.0), ("dense", 0.5), ("k_last", 0.5)],
    decode=lambda a: [[tuple(r) for r in a[0]], a[1]],
    brute=q2_brute, brute_range=(1, 6), slope=1.65, scale_kind="wide"))


# =============================================================================
# Q3 — Maratona de Podcasts: maior janela com <= k categorias distintas
# =============================================================================
def q3_gen(rng, n, kind):
    n = max(1, n)
    if kind == "distinct":
        seq = rng.sample(range(-10**9, 10**9), n)
        k = rng.randint(1, n)
    elif kind == "runs":
        seq = []
        while len(seq) < n:
            seq += [rng.randint(-10**9, 10**9)] * rng.randint(1, max(1, n // 5))
        seq = seq[:n]
        k = rng.randint(1, max(1, min(n, 4)))
    elif kind == "k_n":
        seq = [rng.randint(-3, 3) for _ in range(n)]
        k = n
    else:
        p = {"pool_small": rng.randint(1, 5), "pool_mid": max(2, min(n, 1000))}.get(kind, rng.randint(1, 12))
        pool = [rng.randint(-10**9, 10**9) for _ in range(p)]
        seq = [rng.choice(pool) for _ in range(n)]
        k = max(1, p // 2) if kind == "pool_mid" else rng.randint(1, p + 1)
    return [seq, max(1, min(k, n))]


def q3_oracle(cats, k):
    cnt, left, best = {}, 0, 0
    for r, x in enumerate(cats):
        cnt[x] = cnt.get(x, 0) + 1
        while len(cnt) > k:
            y = cats[left]
            cnt[y] -= 1
            if cnt[y] == 0:
                del cnt[y]
            left += 1
        best = max(best, r - left + 1)
    return best


def q3_brute(cats, k):
    n, best = len(cats), 0
    for i in range(n):
        for j in range(i, n):
            if len(set(cats[i:j + 1])) <= k:
                best = max(best, j - i + 1)
    return best


reg(Problem(
    1, "q3", "question_3", "Maratona de Podcasts", "O(n)", q3_gen, q3_oracle,
    samples=[([[1, 2, 1, 2, 3], 2], 4), ([[1, 2, 3, 4], 1], 1), ([[4, 4, 4, 4], 1], 4)],
    max_size=10**6, tl=5.0, small=(1, 12), medium=2000,
    small_kinds=["pool_small", "distinct", "runs", "k_n", "pool_small"],
    stress=[("pool_mid", 1.0), ("distinct", 1.0), ("pool_small", 0.5), ("runs", 0.5)],
    brute=q3_brute, brute_range=(1, 14), slope=1.65, scale_kind="pool_mid"))


# =============================================================================
# Q4 — Central de Senhas: BFS em strings que diferem em exatamente 1 posição
# =============================================================================
DIG = "0123456789"


def q4_gen(rng, N, kind):
    N = max(1, N)
    L = rng.randint(6, 20) if kind == "chain" else rng.randint(1, 20)
    while 10**L < 2 * N:
        L += 1
    L = min(L, 20)

    def rand_str():
        return "".join(rng.choice(DIG) for _ in range(L))

    def mutate(s):
        i = rng.randrange(L)
        d = rng.choice([c for c in DIG if c != s[i]])
        return s[:i] + d + s[i + 1:]

    seen, nodes = set(), []

    def walk(count, chain):
        s = rand_str()
        while s in seen:
            s = rand_str()
        seen.add(s); nodes.append(s)
        start_len = len(nodes)
        fails = 0
        while len(nodes) - start_len + 1 < count:
            base = nodes[-1] if (chain and fails < 30) else rng.choice(nodes[start_len - 1:])
            t = mutate(base)
            if t in seen:
                fails += 1
                continue
            fails = 0
            seen.add(t); nodes.append(t)

    if kind == "random":
        while len(nodes) < N:
            s = rand_str()
            if s not in seen:
                seen.add(s); nodes.append(s)
    elif kind == "split":
        walk(max(1, N // 2), False)
        if N - len(nodes) > 0:
            walk(N - len(nodes), False)
    else:
        walk(N, kind == "chain")
    if kind == "chain":
        ini, fin = nodes[0], nodes[-1]
    else:
        ini, fin = rng.choice(nodes), rng.choice(nodes)
    banco = nodes[:]
    rng.shuffle(banco)
    return [ini, fin, banco]


def q4_oracle(ini, fin, banco):
    if ini == fin:
        return 0
    L = len(ini)
    buckets = {}
    for s in banco:
        for i in range(L):
            buckets.setdefault((i, s[:i] + s[i + 1:]), []).append(s)
    dist = {ini: 0}
    dq = deque([ini])
    while dq:
        s = dq.popleft()
        for i in range(L):
            for t in buckets[(i, s[:i] + s[i + 1:])]:
                if t not in dist:
                    dist[t] = dist[s] + 1
                    if t == fin:
                        return dist[t]
                    dq.append(t)
    return -1


def q4_brute(ini, fin, banco):
    def adj(a, b):
        return sum(x != y for x, y in zip(a, b)) == 1
    dist = {ini: 0}
    dq = deque([ini])
    while dq:
        s = dq.popleft()
        for t in banco:
            if t not in dist and adj(s, t):
                dist[t] = dist[s] + 1
                dq.append(t)
    return dist.get(fin, -1)


reg(Problem(
    1, "q4", "question_4", "Central de Senhas", "O(N·L)", q4_gen, q4_oracle,
    samples=[(["1000", "1003", ["1000", "1003"]], 1),
             (["1000", "1103", ["1000", "1003", "1103"]], 2),
             (["1000", "2200", ["1000", "1100", "2200"]], -1)],
    max_size=5000, tl=3.0, small=(1, 12), medium=300,
    small_kinds=["walk", "chain", "random", "split"],
    stress=[("chain", 1.0), ("walk", 1.0), ("random", 1.0), ("split", 1.0)],
    brute=q4_brute, brute_range=(1, 14), slope=1.65, scale_kind="chain"))


# =============================================================================
# Q5 — Cache Inteligente (LRU). Args: [capacidade, ops]; op = ["u", chave, valor] | ["c", chave]
# =============================================================================
def q5_gen(rng, size, kind):
    ops_n = max(1, size)
    maxC = 10**5
    if kind == "cap1":
        C, keyspace = 1, 3
    elif kind == "thrash":
        C = min(maxC, max(2, ops_n // 10)); keyspace = C + 1
    elif kind == "hot":
        C = min(maxC, max(2, ops_n // 10)); keyspace = max(2, int(C * 1.2))
    else:
        C = rng.randint(1, min(maxC, max(1, ops_n // 5))); keyspace = rng.randint(1, 3 * C + 3)
    ops = []
    for t in range(ops_n):
        if kind == "thrash":
            key = (t // 2) % keyspace
            ops.append(["u", key, t] if t % 2 == 0 else ["c", key])
            continue
        key = int(keyspace * rng.random() ** 2) if kind == "hot" else rng.randrange(keyspace)
        if rng.random() < 0.5:
            ops.append(["u", key, rng.randint(0, 10**9)])
        else:
            ops.append(["c", key])
    return [C, ops]


def q5_oracle(C, ops):
    d, out = OrderedDict(), []
    for op in ops:
        if op[0] == "c":
            if op[1] in d:
                d.move_to_end(op[1]); out.append(d[op[1]])
            else:
                out.append(-1)
        else:
            k, v = op[1], op[2]
            if k in d:
                d.move_to_end(k)
            elif len(d) >= C:
                d.popitem(last=False)
            d[k] = v
    return out


def q5_brute(C, ops):          # lista simples (MRU no fim), O(n·C)
    items, out = [], []
    for op in ops:
        k = op[1]
        pos = next((i for i, (kk, _) in enumerate(items) if kk == k), -1)
        if op[0] == "c":
            if pos < 0:
                out.append(-1)
            else:
                it = items.pop(pos); items.append(it); out.append(it[1])
        else:
            if pos >= 0:
                items.pop(pos)
            elif len(items) >= C:
                items.pop(0)
            items.append((k, op[2]))
    return out


def q5_call(mod, args):
    cap, ops = args
    cache = mod.Cache(cap)
    out = []
    for op in ops:
        if op[0] == "c":
            out.append(cache.consultar(op[1]))
        else:
            cache.atualizar(op[1], op[2])
    return out


reg(Problem(
    1, "q5", "Cache", "Cache Inteligente (LRU)", "O(1) por operação", q5_gen, q5_oracle,
    samples=[([2, [["u", "home", "conteudo_home"], ["u", "sobre", "conteudo_sobre"], ["c", "home"],
                   ["u", "contato", "conteudo_contato"], ["c", "sobre"], ["c", "contato"]]],
              ["conteudo_home", -1, "conteudo_contato"])],
    max_size=10**6, tl=10.0, small=(1, 30), medium=5000,
    small_kinds=["random", "cap1", "hot", "thrash"],
    stress=[("thrash", 1.0), ("random", 0.5), ("hot", 0.5)],
    call=q5_call, brute=q5_brute, brute_range=(1, 40), slope=1.65, scale_kind="thrash"))


# =============================================================================
# Q6 — Rádio Digital: top-k por frequência (qualquer desempate)
# =============================================================================
def q6_gen(rng, n, kind):
    n = max(1, n)
    if kind == "few":
        pool = rng.sample(range(0, n + 1), min(n + 1, rng.randint(1, 5)))
        rep = [rng.choice(pool) for _ in range(n)]
    elif kind == "skew":
        rep = [int(n * rng.random() ** 4) for _ in range(n)]
    elif kind == "ties":
        d = rng.randint(1, max(1, min(n, 50)))
        pool = rng.sample(range(0, n + 1), min(n + 1, d))
        rep = [pool[i % len(pool)] for i in range(n)]
        rng.shuffle(rep)
    else:
        rep = [rng.randint(0, n) for _ in range(n)]
    k = rng.choice([1, n, rng.randint(1, n), rng.randint(1, max(1, n // 4))])
    return [rep, max(1, min(k, n))]


def q6_oracle(rep, k):
    return [x for x, _ in Counter(rep).most_common(k)]


def q6_brute(rep, k):
    distinct = sorted(set(rep), key=lambda x: -rep.count(x))
    return distinct[:k]


def q6_check(args, out, expected):
    rep, k = args
    cnt = Counter(rep)
    if not isinstance(out, list):
        return False, "a saída deve ser uma lista"
    want = min(k, len(cnt))
    if len(out) != want:
        return False, f"tamanho {len(out)}, esperado {want}"
    if len(set(out)) != len(out) or any(x not in cnt for x in out):
        return False, "há ids repetidos ou que não aparecem no histórico"
    fr = [cnt[x] for x in out]
    if any(fr[i] < fr[i + 1] for i in range(len(fr) - 1)):
        return False, "ordem não é decrescente em número de reproduções"
    if sorted(fr) != sorted(cnt[x] for x in expected):
        return False, "não são as músicas mais tocadas (frequências diferem do top-k)"
    return True, ""


reg(Problem(
    1, "q6", "question_6", "Rádio Digital", "O(n)", q6_gen, q6_oracle,
    samples=[([[1, 1, 1, 2, 2, 3], 2], [1, 2]), ([[1, 1, 1, 1, 1, 1], 2], [1])],
    max_size=10**6, tl=6.0, small=(1, 12), medium=2000,
    small_kinds=["uniform", "few", "skew", "ties", "uniform"],
    stress=[("uniform", 1.0), ("skew", 0.5), ("few", 0.5), ("ties", 0.5)],
    check=q6_check, brute=q6_brute, brute_range=(1, 12), slope=1.65, scale_kind="uniform"))


# =============================================================================
# Q7 — Análise de Crédito: k-ésimo menor (a: esperado O(n); b: O(n) no pior caso)
# =============================================================================
def q7_gen(rng, n, kind):
    n = max(1, n)
    big = 10**9
    if kind == "sorted":
        v = sorted(rng.randint(-big, big) for _ in range(n))
    elif kind == "reversed":
        v = sorted((rng.randint(-big, big) for _ in range(n)), reverse=True)
    elif kind == "equal":
        v = [rng.randint(-big, big)] * n
    elif kind == "organ":
        h = sorted(rng.randint(-big, big) for _ in range(n // 2 + 1))
        v = (h + h[::-1])[:n]
    elif kind == "dups":
        v = [rng.randint(0, 4) for _ in range(n)]
    elif kind == "saw":
        v = [i % 7 for i in range(n)]
    elif kind == "few":
        pool = [rng.randint(-big, big) for _ in range(3)]
        v = [rng.choice(pool) for _ in range(n)]
    else:
        v = [rng.randint(-big, big) for _ in range(n)]
    k = rng.choice([1, n, (n + 1) // 2, rng.randint(1, n)])
    return [v, k]


def q7_oracle(scores, k):
    return sorted(scores)[k - 1]


_Q7_ADV = ["sorted", "reversed", "equal", "organ", "dups", "saw", "few", "random"]

reg(Problem(
    1, "q7_a", "question_7_a", "Análise de Crédito (a) — esperado O(n)", "O(n) esperado", q7_gen, q7_oracle,
    samples=[([[70, 10, 40, 3, 20, 15], 3], 15), ([[70, 10, 40, 3, 20, 15], 1], 3)],
    max_size=10**6, tl=10.0, small=(1, 30), medium=5000,
    small_kinds=_Q7_ADV, medium_kinds=["random"],
    stress=[("random", 1.0), ("random", 0.5)],          # (a) só é justa com entradas aleatórias
    brute=q7_oracle, brute_range=(1, 20), slope=1.65, scale_kind="random"))

reg(Problem(
    1, "q7_b", "question_7_b", "Análise de Crédito (b) — O(n) pior caso", "O(n) pior caso", q7_gen, q7_oracle,
    samples=[([[70, 10, 40, 3, 20, 15], 3], 15), ([[70, 10, 40, 3, 20, 15], 1], 3)],
    max_size=10**6, tl=20.0, small=(1, 30), medium=5000,
    small_kinds=_Q7_ADV, medium_kinds=_Q7_ADV,
    stress=[("random", 0.5), ("sorted", 0.25), ("equal", 0.25), ("organ", 0.25), ("dups", 0.25)],
    brute=q7_oracle, brute_range=(1, 20), slope=1.75, scale_kind="sorted"))


# =============================================================================
# Q8 — Feed Consolidado: intercalar k listas ordenadas
# =============================================================================
def q8_gen(rng, n, kind):
    n = max(1, n)
    if kind == "single":
        k = 1
    elif kind == "singletons":
        k = n
    elif kind == "sqrt":
        k = max(1, int(n ** 0.5))
    elif kind == "tenth":
        k = max(1, n // 20)
    else:
        k = rng.randint(1, n)
    if kind == "skew" and n > 1:
        k = max(2, min(n, int(n ** 0.5)))
        sizes = [1] * (k - 1) + [n - (k - 1)]
    else:
        cuts = sorted(rng.sample(range(1, n), k - 1)) if k > 1 else []
        bounds = [0] + cuts + [n]
        sizes = [bounds[i + 1] - bounds[i] for i in range(k)]
    lists = [sorted(rng.randint(1, 10**9) for _ in range(s)) for s in sizes]
    rng.shuffle(lists)
    return [lists]


def q8_oracle(comunidades):
    return sorted(x for l in comunidades for x in l)


reg(Problem(
    1, "q8", "question_8", "Feed Consolidado", "O(n log k)", q8_gen, q8_oracle,
    samples=[([[[1, 4, 5], [1, 3, 4], [2, 6]]], [1, 1, 2, 3, 4, 4, 5, 6])],
    max_size=10**6, tl=30.0, small=(1, 20), medium=3000,
    small_kinds=["random", "single", "singletons", "sqrt", "skew"],
    stress=[("sqrt", 1.0), ("tenth", 0.5), ("random", 0.5), ("skew", 0.5)],
    brute=q8_oracle, brute_range=(1, 20), slope=1.65, scale_kind="tenth"))


# =============================================================================
# Q9 — Autonomia Elétrica (circuito). a: qualquer partida válida | b: solução única (O(n))
# =============================================================================
def valid_starts(en, co):
    """Todas as estações de partida válidas, em O(n) (janela deslizante sobre somas de prefixo)."""
    n = len(en)
    P = [0] * (2 * n + 1)
    for i in range(2 * n):
        P[i + 1] = P[i] + en[i % n] - co[i % n]
    dq, res = deque(), []
    for i in range(1, 2 * n + 1):
        while dq and P[dq[-1]] >= P[i]:
            dq.pop()
        dq.append(i)
        s = i - n
        if 0 <= s < n:
            while dq[0] < s + 1:
                dq.popleft()
            if P[dq[0]] >= P[s]:
                res.append(s)
    return res


def is_valid_start(en, co, s):
    n, bat = len(en), 0
    for j in range(n):
        i = (s + j) % n
        bat += en[i] - co[i]
        if bat < 0:
            return False
    return True


def _from_d(rng, d):
    en, co = [], []
    for x in d:
        c = rng.randint(max(0, -x), min(10**9, 10**9 - x))
        co.append(c); en.append(c + x)
    return en, co


def q9_gen_factory(unique_only):
    """d[i] = energia[i] - consumo[i]. O número de partidas válidas depende do saldo total do circuito:
    com saldo 0 a partida válida é o mínimo das somas de prefixo (única, salvo empates) — por isso o
    gerador fixa o saldo e confere a unicidade com `valid_starts` (O(n))."""
    def gen(rng, n, kind):
        n = max(1, n)
        if n == 1:
            kind = "n1"
        S = max(1, min(rng.choice([1, 10, 10**3, 10**6, 10**8]), 4 * 10**8 // n))
        if kind == "big":
            S = max(1, 4 * 10**8 // n)
        for _ in range(60):
            if kind == "long_survive":
                d = [1] * (n - 1) + [-(n + 5)]
            elif kind == "multi":
                d = [rng.randint(0, S) for _ in range(n)]
            elif kind == "zeros":
                d = [0] * n
            elif kind == "n1":
                d = [rng.randint(-S, S)]
            else:
                if kind == "none":
                    tot = -rng.randint(1, S)
                elif kind in ("unique", "big"):
                    tot = rng.choice([0, 0, rng.randint(0, S)])
                else:  # "walk"
                    tot = rng.choice([-rng.randint(1, S), 0, rng.randint(0, S)])
                d = [rng.randint(-S, S) for _ in range(n)]
                d[-1] += tot - sum(d)
            if max(abs(x) for x in d) > 10**9:
                continue
            en, co = _from_d(rng, d)
            cnt = len(valid_starts(en, co))
            if unique_only and cnt > 1:
                continue
            if kind in ("unique", "big") and cnt != 1:
                continue
            if kind == "none" and cnt != 0:
                continue
            return [en, co]
        en, co = _from_d(rng, [1] * (n - 1) + [-(n + 5)])      # fallback: sem solução
        return [en, co]
    return gen


def q9_oracle(en, co):
    vs = valid_starts(en, co)
    return vs[0] if vs else -1


def q9_brute(en, co):
    for s in range(len(en)):
        if is_valid_start(en, co, s):
            return s
    return -1


def q9_check(args, out, expected):
    en, co = args
    if isinstance(out, bool) or not isinstance(out, int):
        return False, "a saída deve ser um inteiro (índice da estação ou -1)"
    if out == -1:
        return (expected == -1), ("" if expected == -1 else "retornou -1, mas existe estação de partida válida")
    if not (0 <= out < len(en)):
        return False, "índice fora do intervalo"
    return (is_valid_start(en, co, out)), ("" if is_valid_start(en, co, out) else f"partindo da estação {out} a bateria fica negativa")


_Q9_SAMPLES = [([[3, 1, 1], [1, 2, 2]], 0), ([[2, 3, 5], [3, 5, 4]], -1)]

reg(Problem(
    1, "q9_a", "question_9_a", "Autonomia Elétrica (a) — força bruta", "O(n²)", q9_gen_factory(False), q9_oracle,
    samples=_Q9_SAMPLES, max_size=3000, tl=5.0, small=(1, 10), medium=200,
    small_kinds=["walk", "unique", "none", "multi", "zeros", "n1"],
    stress=[("long_survive", 1.0), ("walk", 1.0), ("multi", 1.0), ("none", 1.0)],
    check=q9_check, brute=q9_brute, brute_range=(1, 10)))

reg(Problem(
    1, "q9_b", "question_9_b", "Autonomia Elétrica (b) — O(n)", "O(n)", q9_gen_factory(True), q9_oracle,
    samples=_Q9_SAMPLES, max_size=10**5, tl=3.0, small=(1, 10), medium=2000,
    small_kinds=["unique", "none", "walk", "n1", "big"],
    stress=[("unique", 1.0), ("none", 1.0), ("walk", 1.0), ("big", 1.0)],
    check=q9_check, brute=q9_brute, brute_range=(1, 10), slope=1.65, scale_kind="unique"))


# =============================================================================
# Q10 — Trilha de Picos de Montanha: LIS estritamente crescente
# =============================================================================
def q10_gen(rng, n, kind):
    n = max(1, n)
    big = 10**9
    if kind == "inc":
        v = sorted(rng.sample(range(-big, big), n))
    elif kind == "dec":
        v = sorted(rng.sample(range(-big, big), n), reverse=True)
    elif kind == "equal":
        v = [rng.randint(-big, big)] * n
    elif kind == "dups":
        v = [rng.randint(0, max(1, n // 10)) for _ in range(n)]
    elif kind == "saw":
        v = [i % 1000 for i in range(n)]
    else:
        v = [rng.randint(-big, big) for _ in range(n)]
    return [v]


def q10_oracle(alt):
    tails = []
    for x in alt:
        i = bisect.bisect_left(tails, x)
        if i == len(tails):
            tails.append(x)
        else:
            tails[i] = x
    return len(tails)


def q10_brute(alt):
    n = len(alt)
    dp = [1] * n
    for i in range(n):
        for j in range(i):
            if alt[j] < alt[i]:
                dp[i] = max(dp[i], dp[j] + 1)
    return max(dp) if dp else 0


reg(Problem(
    1, "q10", "question_10", "Trilha de Picos de Montanha", "O(n log n)", q10_gen, q10_oracle,
    samples=[([[3, 1, 4, 1, 5, 9, 2, 6]], 4), ([[5, 4, 3, 2, 1]], 1)],
    max_size=5 * 10**5, tl=4.0, small=(1, 14), medium=2000,
    small_kinds=["random", "inc", "dec", "equal", "dups", "saw"],
    stress=[("random", 1.0), ("inc", 0.5), ("dec", 0.5), ("dups", 0.5), ("equal", 0.5)],
    brute=q10_brute, brute_range=(1, 16), slope=1.65, scale_kind="random"))
