"""
Lista 2 — gabarito, geradores e verificadores.

⚠ SPOILER: este arquivo contém soluções de referência (necessárias para calcular a saída esperada
dos casos grandes). Se quiser estudar sem ver as respostas, não abra este arquivo.

As questões 8(b) e 8(c) são discursivas e não têm casos de teste.
"""
from __future__ import annotations

import heapq
import itertools
import math
import sys
from collections import deque

from ..core import Problem

PROBLEMS: list = []
MOD = 10**9 + 7
DIRS = ((1, 0), (-1, 0), (0, 1), (0, -1))
LETTERS = "abcdefghijklmnopqrstuvwxyz"


def reg(p: Problem) -> Problem:
    PROBLEMS.append(p)
    return p


# =============================================================================
# Q1 — Alfabeto Perdido (ordenação topológica das letras)
# =============================================================================
def _constraints(words):
    """(conjunto de pares (x,y): 'x vem antes de y', inconsistente_por_prefixo)."""
    pairs, bad = set(), False
    for a, b in zip(words, words[1:]):
        m = min(len(a), len(b))
        i = 0
        while i < m and a[i] == b[i]:
            i += 1
        if i == m:
            if len(a) > len(b):
                bad = True
        else:
            pairs.add((a[i], b[i]))
    return pairs, bad


def q1_oracle(words):
    letters = set("".join(words))
    pairs, bad = _constraints(words)
    if bad:
        return ""
    adj = {c: [] for c in letters}
    indeg = {c: 0 for c in letters}
    for x, y in pairs:
        adj[x].append(y)
        indeg[y] += 1
    stack = [c for c in sorted(letters) if indeg[c] == 0]
    order = []
    while stack:
        c = stack.pop()
        order.append(c)
        for y in adj[c]:
            indeg[y] -= 1
            if indeg[y] == 0:
                stack.append(y)
    return "".join(order) if len(order) == len(letters) else ""


def q1_brute(words):
    letters = sorted(set("".join(words)))
    if len(letters) > 8:
        return NotImplemented          # permutações demais: o selftest pula este caso
    for perm in itertools.permutations(letters):
        rank = {c: i for i, c in enumerate(perm)}
        keys = [tuple(rank[c] for c in w) for w in words]
        if all(keys[i] <= keys[i + 1] for i in range(len(keys) - 1)):
            return "".join(perm)
    return ""


def q1_check(args, out, expected):
    words = args[0]
    if not isinstance(out, str):
        return False, "a saída deve ser uma string"
    if expected == "":
        return (out == ""), ("" if out == "" else 'a lista é inconsistente: o esperado era ""')
    if out == "":
        return False, 'existe uma ordem válida, mas retornou ""'
    if len(out) != len(set(out)) or set(out) != set("".join(words)):
        return False, "deve conter cada letra distinta exatamente uma vez (e apenas as que aparecem)"
    rank = {c: i for i, c in enumerate(out)}
    pairs, _ = _constraints(words)
    for x, y in pairs:
        if rank[x] > rank[y]:
            return False, f"a ordem retornada põe '{y}' antes de '{x}', mas as palavras exigem '{x}' < '{y}'"
    return True, ""


def q1_gen(rng, size, kind):
    n = max(1, size)
    if kind == "prefix_violation" and n >= 10**5:
        n = 10**5 - 1                         # a inserção do prefixo não pode estourar o limite
    if kind == "single":
        k = rng.randint(1, 26)
        al = rng.sample(LETTERS, k)
        return [["".join(rng.sample(al, rng.randint(1, k)))]]
    if kind == "chain26":                      # ordem total forçada: uma letra por palavra
        return [rng.sample(LETTERS, 26)]
    if kind == "long_word":                    # uma única palavra muito longa: testa O(C)
        return [["".join(rng.choices(LETTERS, k=10**5))]]
    k = rng.randint(2, 3) if kind == "dups" else rng.randint(2, 26)
    alphabet = rng.sample(LETTERS, k)          # a ordem "escondida" é a ordem desta lista
    maxlen = 3 if kind == "dups" else rng.randint(1, 10)
    if kind == "prefix_heavy":
        base = rng.choices(alphabet, k=12)
        words = ["".join(base[:rng.randint(1, 12)]) + "".join(rng.choices(alphabet, k=rng.randint(0, 3)))
                 for _ in range(n)]
    else:
        words = ["".join(rng.choices(alphabet, k=rng.randint(1, maxlen))) for _ in range(n)]
    tab = str.maketrans({c: LETTERS[i] for i, c in enumerate(alphabet)})
    words.sort(key=lambda w: w.translate(tab))
    if kind == "swap" and n >= 2:
        i = rng.randrange(n - 1)
        words[i], words[i + 1] = words[i + 1], words[i]
    elif kind == "prefix_violation":
        cands = [i for i, w in enumerate(words) if len(w) >= 2]
        if cands:
            i = rng.choice(cands)
            words.insert(i + 1, words[i][:rng.randint(1, len(words[i]) - 1)])
    elif kind == "reverse_block" and n >= 3:
        a = rng.randrange(n - 2)
        b = min(n, a + 3 + rng.randint(0, n))
        words[a:b] = words[a:b][::-1]
    return [words]


_Q1_KINDS = ["valid", "prefix_heavy", "swap", "prefix_violation", "reverse_block", "dups", "single", "chain26", "valid"]
reg(Problem(
    2, "q1", "question_1", "Alfabeto Perdido", "O(C)", q1_gen, q1_oracle,
    samples=[([["zx", "zy", "yx"]], "zxy"), ([["cab", "cad", "bd", "bc"]], ""), ([["abc", "ab"]], ""),
             ([["abc"]], "abc")],
    max_size=10**5, tl=3.0, small=(1, 8), medium=2000,
    small_kinds=_Q1_KINDS, medium_kinds=_Q1_KINDS,
    stress=[("valid", 1.0), ("prefix_heavy", 1.0), ("dups", 1.0), ("swap", 1.0),
            ("prefix_violation", 1.0), ("long_word", 1.0)],
    check=q1_check, brute=q1_brute, brute_range=(1, 7), slope=1.65, scale_kind="valid",
    size_of=lambda args, kind, size: len(args[0]) if kind == "chain26" else size))


# =============================================================================
# Q2 — Ponte entre as Ilhas (BFS multi-fonte)
# =============================================================================
def _flood(g, n, m, start, seen):
    seen[start[0]][start[1]] = True
    st, cells = [start], [start]
    while st:
        r, c = st.pop()
        for dr, dc in DIRS:
            nr, nc = r + dr, c + dc
            if 0 <= nr < n and 0 <= nc < m and g[nr][nc] == 1 and not seen[nr][nc]:
                seen[nr][nc] = True
                st.append((nr, nc))
                cells.append((nr, nc))
    return cells


def q2_oracle(mapa):
    n, m = len(mapa), len(mapa[0])
    start = next((r, c) for r in range(n) for c in range(m) if mapa[r][c] == 1)
    island = _flood(mapa, n, m, start, [[False] * m for _ in range(n)])
    dist = [[-1] * m for _ in range(n)]
    dq = deque()
    for r, c in island:
        dist[r][c] = 0
        dq.append((r, c))
    while dq:
        r, c = dq.popleft()
        for dr, dc in DIRS:
            nr, nc = r + dr, c + dc
            if 0 <= nr < n and 0 <= nc < m and dist[nr][nc] < 0:
                if mapa[nr][nc] == 1:                 # alcançou a outra ilha
                    return dist[r][c]
                dist[nr][nc] = dist[r][c] + 1
                dq.append((nr, nc))
    return -1


def q2_brute(mapa):
    n, m = len(mapa), len(mapa[0])
    water = [(r, c) for r in range(n) for c in range(m) if mapa[r][c] == 0]

    def comps(g):
        seen = [[False] * m for _ in range(n)]
        k = 0
        for r in range(n):
            for c in range(m):
                if g[r][c] == 1 and not seen[r][c]:
                    _flood(g, n, m, (r, c), seen)
                    k += 1
        return k

    for k in range(len(water) + 1):
        for comb in itertools.combinations(water, k):
            g = [row[:] for row in mapa]
            for r, c in comb:
                g[r][c] = 1
            if comps(g) == 1:
                return k
    return -1


def _grow(rng, n, m, seed, size, blocked):
    cells, inset, frontier = [seed], {seed}, [seed]
    while len(cells) < size and frontier:
        i = rng.randrange(len(frontier))
        r, c = frontier[i]
        opts = [(r + dr, c + dc) for dr, dc in DIRS
                if 0 <= r + dr < n and 0 <= c + dc < m and (r + dr, c + dc) not in inset
                and not blocked[(r + dr) * m + c + dc]]
        if not opts:
            frontier[i] = frontier[-1]
            frontier.pop()
            continue
        nb = rng.choice(opts)
        inset.add(nb)
        cells.append(nb)
        frontier.append(nb)
    return cells


def q2_gen(rng, size, kind):
    n = max(2, size)
    if kind in ("thin", "thin_row", "thin_col"):   # grades finas: 2 x N ou N x 2
        if kind == "thin_row" or (kind == "thin" and rng.random() < 0.5):
            n, m = 2, max(2, size)
        else:
            n, m = max(2, size), 2
        g = [[0] * m for _ in range(n)]
        g[0][0] = g[n - 1][m - 1] = 1
        return [g]
    if kind == "far":
        m = n if rng.random() < 0.5 else rng.randint(2, n)
        g = [[0] * m for _ in range(n)]
        a, b = (0, 0), (n - 1, m - 1)
        if rng.random() < 0.5:
            a, b = (0, m - 1), (n - 1, 0)
        g[a[0]][a[1]] = g[b[0]][b[1]] = 1
        return [g]
    if kind == "bars":
        m = max(3, rng.randint(3, max(3, n)))
        w = rng.randint(1, max(1, (m - 1) // 3))
        g = [[1 if (c < w or c >= m - w) else 0 for c in range(m)] for _ in range(n)]
        if rng.random() < 0.5:
            g = [list(col) for col in zip(*g)]
        return [g]
    if kind == "diag":
        m = rng.randint(2, n)
        g = [[0] * m for _ in range(n)]
        r, c = rng.randrange(n - 1), rng.randrange(m - 1)
        g[r][c] = g[r + 1][c + 1] = 1
        return [g]
    # blobs: duas ilhas aleatórias (crescimento aleatório), sem nunca se tocar na vertical/horizontal
    m = n if rng.random() < 0.5 else rng.randint(2, n)
    cap = rng.choice([4, 20, 100, 400])           # ilhas de tamanhos variados (ilhas pequenas => ponte longa)
    sa = rng.randint(1, max(1, n * m // cap))
    for _ in range(60):
        blocked = bytearray(n * m)
        A = _grow(rng, n, m, (rng.randrange(n), rng.randrange(m)), sa, blocked)
        forbid = bytearray(n * m)
        for r, c in A:
            forbid[r * m + c] = 1
            for dr, dc in DIRS:
                if 0 <= r + dr < n and 0 <= c + dc < m:
                    forbid[(r + dr) * m + c + dc] = 1
        seed = next(((r, c) for r, c in ((rng.randrange(n), rng.randrange(m)) for _ in range(300))
                     if not forbid[r * m + c]), None)
        if seed is None:
            sa = max(1, sa // 2)
            continue
        B = _grow(rng, n, m, seed, rng.randint(1, max(1, n * m // cap)), forbid)
        g = [[0] * m for _ in range(n)]
        for r, c in A + B:
            g[r][c] = 1
        return [g]
    g = [[0] * 2 for _ in range(2)]
    g[0][0] = g[1][1] = 1
    return [g]


_Q2_KINDS = ["blobs", "far", "bars", "diag", "blobs"]
reg(Problem(
    2, "q2", "question_2", "Ponte entre as Ilhas", "O(n·m)", q2_gen, q2_oracle,
    samples=[([[[1, 1, 0, 0, 0], [1, 0, 0, 0, 0], [0, 0, 0, 0, 0], [0, 0, 0, 1, 1], [0, 0, 0, 1, 1]]], 4),
             ([[[1, 0, 0, 0, 1], [1, 0, 0, 0, 1], [1, 0, 0, 0, 1]]], 3),
             ([[[0, 1, 0], [0, 0, 0], [0, 0, 1]]], 2)],
    max_size=500, tl=3.0, small=(2, 4), medium=60,
    small_kinds=_Q2_KINDS, medium_kinds=_Q2_KINDS,
    stress=[("blobs", 1.0), ("far", 1.0), ("bars", 1.0), ("blobs", 1.0), ("diag", 1.0),
            ("thin_row", 1.0), ("thin_col", 1.0)],
    brute=q2_brute, brute_range=(2, 4), slope=2.65, scale_kind="blobs"))


# =============================================================================
# Q3 — Trilha de Menor Esforço: (esforço mínimo, menor nº de passos nesse esforço)
# =============================================================================
def _bfs_thr(alt, E):
    n, m = len(alt), len(alt[0])
    dist = [[-1] * m for _ in range(n)]
    dist[0][0] = 0
    dq = deque([(0, 0)])
    while dq:
        r, c = dq.popleft()
        if (r, c) == (n - 1, m - 1):
            return dist[r][c]
        for dr, dc in DIRS:
            nr, nc = r + dr, c + dc
            if 0 <= nr < n and 0 <= nc < m and dist[nr][nc] < 0 and abs(alt[nr][nc] - alt[r][c]) <= E:
                dist[nr][nc] = dist[r][c] + 1
                dq.append((nr, nc))
    return -1


def q3_oracle(alt):
    n, m = len(alt), len(alt[0])
    INF = float("inf")
    best = [[INF] * m for _ in range(n)]
    best[0][0] = 0
    h = [(0, 0, 0)]
    while h:
        e, r, c = heapq.heappop(h)
        if e > best[r][c]:
            continue
        if (r, c) == (n - 1, m - 1):
            break
        for dr, dc in DIRS:
            nr, nc = r + dr, c + dc
            if 0 <= nr < n and 0 <= nc < m:
                ne = max(e, abs(alt[nr][nc] - alt[r][c]))
                if ne < best[nr][nc]:
                    best[nr][nc] = ne
                    heapq.heappush(h, (ne, nr, nc))
    E = best[n - 1][m - 1]
    return [E, _bfs_thr(alt, E)]


def q3_brute(alt):
    n, m = len(alt), len(alt[0])
    cands = {0}
    for r in range(n):
        for c in range(m):
            if r + 1 < n:
                cands.add(abs(alt[r + 1][c] - alt[r][c]))
            if c + 1 < m:
                cands.add(abs(alt[r][c + 1] - alt[r][c]))
    for E in sorted(cands):
        s = _bfs_thr(alt, E)
        if s >= 0:
            return [E, s]


def q3_gen(rng, size, kind):
    n = max(1, size)
    m = n if kind in ("big", "smooth", "flat", "ridge") and rng.random() < 0.5 else rng.randint(1, n)
    if kind == "line":
        n, m = (1, n) if rng.random() < 0.5 else (n, 1)
        return [[[rng.randint(1, 10**6) for _ in range(m)] for _ in range(n)]]
    if kind == "row":                          # garante a orientação 1 x N no estresse
        return [[[rng.randint(1, 10**6) for _ in range(n)]]]
    if kind == "flat":
        v = rng.randint(1, 10**6)
        return [[[v] * m for _ in range(n)]]
    if kind == "ridge":                              # parede alta com uma única brecha -> caminho longo
        g = [[1] * m for _ in range(n)]
        col = m // 2
        gap = rng.randrange(n)
        for r in range(n):
            g[r][col] = 10**6 if r != gap else 1
        return [g]
    if kind == "smooth":
        return [[[max(1, min(10**6, (i + j) * 500 + rng.randint(-300, 300))) for j in range(m)] for i in range(n)]]
    hi = {"v2": 2, "v10": 10}.get(kind, 10**6)
    return [[[rng.randint(1, hi) for _ in range(m)] for _ in range(n)]]


_Q3_KINDS = ["v2", "v10", "big", "smooth", "flat", "line", "ridge"]
reg(Problem(
    2, "q3", "question_3", "Trilha de Menor Esforço", "O(n·m·log(n·m))", q3_gen, q3_oracle,
    samples=[([[[4, 3, 4], [3, 3, 3], [4, 3, 4]]], [1, 4]), ([[[1, 1, 1]]], [0, 2]), ([[[1], [5], [1]]], [4, 2])],
    max_size=300, tl=12.0, small=(1, 5), medium=40,
    small_kinds=_Q3_KINDS, medium_kinds=_Q3_KINDS,
    stress=[("big", 1.0), ("v10", 1.0), ("smooth", 1.0), ("ridge", 1.0), ("flat", 1.0),
            ("line", 1.0), ("row", 1.0)],
    brute=q3_brute, brute_range=(1, 5), slope=2.65, scale_kind="big"))


# =============================================================================
# Q4 — Câmbio Ineficiente (detecção de arbitragem = ciclo positivo; Bellman-Ford em log)
# =============================================================================
TOL = 1e-9


def _bf_cycle(n, edges, eps):
    w = [(a, b, -math.log(r)) for a, b, r in edges]
    d = [0.0] * n
    par = [-1] * n
    x = -1
    for _ in range(n):
        x = -1
        for a, b, wt in w:
            if d[a] + wt < d[b] - eps:
                d[b] = d[a] + wt
                par[b] = a
                x = b
        if x == -1:
            return []
    for _ in range(n):
        x = par[x]
    cyc, y = [x], par[x]
    while y != x:
        cyc.append(y)
        y = par[y]
    cyc.append(x)
    cyc.reverse()
    return cyc


def _cycle_product(edges, cyc):
    rate = {(a, b): r for a, b, r in edges}
    p = 1.0
    for a, b in zip(cyc, cyc[1:]):
        p *= rate[(a, b)]
    return p


def q4_oracle(n, edges):
    cyc = _bf_cycle(n, edges, 1e-12)
    if cyc and _cycle_product(edges, cyc) > 1 + TOL:
        return cyc
    return []


def q4_brute(n, edges):
    cur = [[1.0 if i == j else 0.0 for j in range(n)] for i in range(n)]
    for _ in range(n):
        nxt = [[0.0] * n for _ in range(n)]
        for i in range(n):
            ci = cur[i]
            for a, b, r in edges:
                if ci[a] > 0 and ci[a] * r > nxt[i][b]:
                    nxt[i][b] = ci[a] * r
        cur = nxt
        if any(cur[i][i] > 1 + TOL for i in range(n)):
            return [-1]          # sentinela: "existe arbitragem"
    return []


def q4_check(args, out, expected):
    n, edges = args
    if not isinstance(out, list):
        return False, "a saída deve ser uma lista"
    if expected == []:
        return (out == []), ("" if out == [] else "não existe arbitragem: o esperado era []")
    if out == []:
        return False, "existe um ciclo de arbitragem, mas retornou []"
    if len(out) < 3 or out[0] != out[-1]:
        return False, "o ciclo deve ter a forma [c0, c1, ..., ck] com ck == c0 (k >= 2)"
    rate = {(a, b): r for a, b, r in edges}
    prod = 1.0
    for a, b in zip(out, out[1:]):
        if (a, b) not in rate:
            return False, f"não existe cotação {a} -> {b}"
        prod *= rate[(a, b)]
    if not prod > 1 + TOL:
        return False, f"o produto do ciclo é {prod!r}, não é > 1 + 1e-9 (não é arbitragem)"
    return True, ""


def _unambiguous(n, edges):
    return bool(_bf_cycle(n, edges, 1e-12)) == bool(_bf_cycle(n, edges, 1e-6))


def _q4_try(rng, n, kind):
    maxm = n * (n - 1)
    if n <= 30:
        m_t = rng.randint(1, min(maxm, 60))
    else:
        m_t = min(5000, maxm, 16 * n + rng.randint(0, n))
    planted = kind.endswith("_arb") and not kind.startswith("long")
    m_t = min(m_t, 4900 if planted else 5000)
    edges = {}

    def rand_pairs(k):
        if k * 3 > maxm:
            allp = [(i, j) for i in range(n) for j in range(n) if i != j]
            return rng.sample(allp, min(k, len(allp)))
        s = set()
        while len(s) < k:
            a, b = rng.randrange(n), rng.randrange(n)
            if a != b:
                s.add((a, b))
        return list(s)

    pow2 = kind.startswith("pow2") or kind.startswith("long")
    if kind.startswith("long"):
        perm = rng.sample(range(n), n)
        ex = [0] * n
        if kind == "long_arb":
            ex[rng.randrange(n)] = 1
        for i in range(n):
            edges[(perm[i], perm[(i + 1) % n])] = 2.0 ** ex[i]
        for a, b in rand_pairs(min(m_t, 4000)):
            if (a, b) not in edges and len(edges) < 5000:
                edges[(a, b)] = 2.0 ** (-rng.choice([1, 2]))
        return [(a, b, r) for (a, b), r in edges.items()]
    if pow2:
        pot = [rng.randint(-3, 3) for _ in range(n)]
        for a, b in rand_pairs(m_t):
            edges[(a, b)] = 2.0 ** (pot[b] - pot[a] - rng.choice([0, 0, 1, 2]))
    else:
        pot = [rng.uniform(-3, 3) for _ in range(n)]
        for a, b in rand_pairs(m_t):
            edges[(a, b)] = float("%.9g" % math.exp(pot[b] - pot[a] - rng.uniform(0.02, 0.5)))
    if planted:
        L = rng.randint(2, min(n, 6))
        nodes = rng.sample(range(n), L)
        bump = rng.randrange(L)
        g = rng.uniform(0.01, 0.3)
        for i in range(L):
            u, v = nodes[i], nodes[(i + 1) % L]
            if pow2:
                edges[(u, v)] = 2.0 ** (pot[v] - pot[u] + (rng.choice([1, 2]) if i == bump else 0))
            else:
                edges[(u, v)] = float("%.9g" % math.exp(pot[v] - pot[u] + g / L))
    return [(a, b, r) for (a, b), r in edges.items()]


def q4_gen(rng, size, kind):
    n = max(2, size)
    if kind == "bounds_noarb":                 # taxas nos extremos permitidos, produto exatamente 1
        return [2, [[0, 1, 1000.0], [1, 0, 0.001]]]
    if kind == "bounds_arb":                   # taxas nos extremos, ciclo de arbitragem
        return [3, [[0, 1, 1000.0], [1, 2, 1000.0], [2, 0, 0.001]]]
    if kind.startswith("long") and n < 3:
        kind = "pow2_noarb"
    for _ in range(30):
        edges = _q4_try(rng, n, kind)
        rng.shuffle(edges)
        if edges and _unambiguous(n, edges):
            return [n, [list(e) for e in edges]]
    return [n, [[0, 1, 2.0], [1, 0, 0.25]]]


_Q4_KINDS = ["pow2_noarb", "pow2_arb", "dec_noarb", "dec_arb", "long_arb", "long_noarb"]
reg(Problem(
    2, "q4", "question_4", "Câmbio Ineficiente", "O(n·m)", q4_gen, q4_oracle,
    samples=[([3, [(0, 1, 2.0), (1, 2, 3.0), (2, 0, 0.2)]], [0, 1, 2, 0]),
             ([2, [(0, 1, 2.0), (1, 0, 0.5)]], []),
             ([4, [(0, 1, 1.5), (1, 2, 0.5), (2, 3, 2.0)]], [])],
    max_size=300, tl=8.0, small=(2, 6), medium=40,
    small_kinds=_Q4_KINDS, medium_kinds=_Q4_KINDS,
    stress=[("pow2_noarb", 1.0), ("dec_noarb", 1.0), ("long_noarb", 1.0), ("long_arb", 1.0),
            ("pow2_arb", 1.0), ("dec_arb", 1.0), ("bounds_noarb", 1.0), ("bounds_arb", 1.0)],
    check=q4_check, decode=lambda a: [a[0], [tuple(e) for e in a[1]]],
    brute=q4_brute, brute_range=(2, 6), slope=2.75, scale_kind="pow2_noarb",
    normalize_kind=lambda kind, size: "pow2_noarb" if kind.startswith("long") and max(2, size) < 3 else kind,
    size_of=lambda args, kind, size: args[0]))


# =============================================================================
# Q5 — Organograma da Empresa: ancestral (tin/tout) e primos (profundidade + pai), O(1) por consulta
# =============================================================================
def q5_oracle(n, lig, cons):
    adj = [[] for _ in range(n)]
    for u, v in lig:
        adj[u].append(v)
        adj[v].append(u)
    par, dep, tin, tout, it = [-1] * n, [0] * n, [0] * n, [0] * n, [0] * n
    st, t = [0], 1
    while st:
        u = st[-1]
        if it[u] < len(adj[u]):
            v = adj[u][it[u]]
            it[u] += 1
            if v != par[u]:
                par[v], dep[v], tin[v] = u, dep[u] + 1, t
                t += 1
                st.append(v)
        else:
            tout[u] = t
            st.pop()
    res = []
    for typ, u, v in cons:
        if u == v:
            res.append(False)
        elif typ == "A":
            res.append(tin[u] <= tin[v] < tout[u])
        else:
            res.append(dep[u] == dep[v] and par[u] != par[v])
    return res


def q5_brute(n, lig, cons):
    adj = [[] for _ in range(n)]
    for u, v in lig:
        adj[u].append(v)
        adj[v].append(u)
    par, dep, seen, dq = [-1] * n, [0] * n, [False] * n, deque([0])
    seen[0] = True
    while dq:
        u = dq.popleft()
        for v in adj[u]:
            if not seen[v]:
                seen[v], par[v], dep[v] = True, u, dep[u] + 1
                dq.append(v)
    res = []
    for typ, u, v in cons:
        if u == v:
            res.append(False)
        elif typ == "A":
            x, ok = par[v], False
            while x != -1:
                if x == u:
                    ok = True
                    break
                x = par[x]
            res.append(ok)
        else:
            res.append(dep[u] == dep[v] and par[u] != par[v])
    return res


def q5_check(args, out, expected):
    if not isinstance(out, list) or len(out) != len(expected):
        return False, f"a saída deve ser uma lista com {len(expected)} respostas"
    for i, (o, e) in enumerate(zip(out, expected)):
        if not isinstance(o, bool):
            return False, f"resposta #{i} não é bool ({o!r})"
        if o != e:
            return False, f"consulta #{i} {tuple(args[2][i])}: esperado {e}, obtido {o}"
    return True, ""


def q5_gen(rng, size, kind):
    n = max(2, size)
    parent = [0] * n
    for i in range(1, n):
        if kind == "chain":
            parent[i] = i - 1
        elif kind == "star":
            parent[i] = 0
        elif kind == "binary":
            parent[i] = (i - 1) // 2
        elif kind == "broom":
            parent[i] = i - 1 if i <= n // 2 else n // 2
        elif kind == "deep":
            parent[i] = rng.randrange(max(0, i - 4), i)
        else:
            parent[i] = rng.randrange(i)
    perm = list(range(1, n))
    rng.shuffle(perm)
    label = [0] + perm
    par, dep = [0] * n, [0] * n
    edges = []
    for i in range(1, n):
        par[label[i]] = label[parent[i]]
        dep[label[i]] = dep[label[parent[i]]] + 1
        u, v = label[parent[i]], label[i]
        edges.append([u, v] if rng.random() < 0.5 else [v, u])
    rng.shuffle(edges)
    by_depth = {}
    for v in range(n):
        by_depth.setdefault(dep[v], []).append(v)
    qs = []
    for _ in range(max(1, min(size, 2 * 10**5))):
        v = rng.randrange(n)
        if rng.random() < 0.5:
            r = rng.random()
            if r < 0.5:
                u = v
                for _ in range(rng.randint(1, 30)):
                    if u == 0:
                        break
                    u = par[u]
            elif r < 0.55:
                u = v
            else:
                u = rng.randrange(n)
            if rng.random() < 0.2:
                u, v = v, u
            qs.append(["A", u, v])
        else:
            r = rng.random()
            u = rng.choice(by_depth[dep[v]]) if r < 0.6 else (v if r < 0.65 else rng.randrange(n))
            qs.append(["P", u, v])
    return [n, edges, qs]


_Q5_KINDS = ["random", "chain", "star", "binary", "broom", "deep"]
reg(Problem(
    2, "q5", "question_5", "Organograma da Empresa", "O(n + q)", q5_gen, q5_oracle,
    samples=[([7, [(0, 1), (0, 2), (1, 3), (1, 4), (2, 5), (2, 6)],
               [("A", 0, 5), ("A", 1, 5), ("A", 3, 3), ("P", 3, 5), ("P", 3, 4), ("P", 1, 3)]],
              [True, False, False, True, False, False])],
    max_size=2 * 10**5, tl=5.0, small=(2, 10), medium=2000,
    small_kinds=_Q5_KINDS, medium_kinds=_Q5_KINDS,
    stress=[("chain", 1.0), ("random", 1.0), ("broom", 1.0), ("star", 1.0), ("deep", 1.0), ("binary", 1.0)],
    check=q5_check, decode=lambda a: [a[0], [tuple(e) for e in a[1]], [tuple(q) for q in a[2]]],
    brute=q5_brute, brute_range=(2, 10), slope=1.65, scale_kind="deep"))


# =============================================================================
# Q6 — Abastecimento de Água (AGM com nó virtual 'poço')
# =============================================================================
def q6_oracle(pocos, canos):
    n = len(pocos)
    edges = [(c, i, j) for i, j, c in canos] + [(w, i, n) for i, w in enumerate(pocos)]
    edges.sort()
    p = list(range(n + 1))

    def find(x):
        while p[x] != x:
            p[x] = p[p[x]]
            x = p[x]
        return x

    total = 0
    for c, a, b in edges:
        ra, rb = find(a), find(b)
        if ra != rb:
            p[ra] = rb
            total += c
    return total


def q6_brute(pocos, canos):
    n, m = len(pocos), len(canos)
    best = float("inf")
    for wm in range(1 << n):
        wc = sum(pocos[i] for i in range(n) if wm >> i & 1)
        for em in range(1 << m):
            cost = wc + sum(canos[j][2] for j in range(m) if em >> j & 1)
            if cost >= best:
                continue
            p = list(range(n))

            def find(x):
                while p[x] != x:
                    x = p[x]
                return x
            for j in range(m):
                if em >> j & 1:
                    a, b = find(canos[j][0]), find(canos[j][1])
                    if a != b:
                        p[a] = b
            has_well = {find(i) for i in range(n) if wm >> i & 1}
            if all(find(i) in has_well for i in range(n)):
                best = cost
    return best


def q6_gen(rng, size, kind):
    n = max(1, size)
    maxm = min(10**5, n * (n - 1) // 2)
    m = {"sparse": min(maxm, n), "dense": maxm, "dense_cheap": maxm,
         "empty": 0}.get(kind, min(maxm, rng.randint(0, 3 * n)))
    total = n * (n - 1) // 2
    if m * 3 > total:
        sel = rng.sample([(i, j) for i in range(n) for j in range(i + 1, n)], m)
    else:
        s = set()
        while len(s) < m:
            i, j = rng.randrange(n), rng.randrange(n)
            if i != j:
                s.add((min(i, j), max(i, j)))
        sel = list(s)
    wl, wh, pl, ph = {"cheap_wells": (1, 50, 50, 10**5), "expensive_wells": (5 * 10**4, 10**5, 1, 10**4),
                      "dense_cheap": (1, 50, 5 * 10**4, 10**5)
                      }.get(kind, (1, 10**5, 1, 10**5))
    pocos = [rng.randint(wl, wh) for _ in range(n)]
    canos = []
    for i, j in sel:
        canos.append([i, j, rng.randint(pl, ph)] if rng.random() < 0.5 else [j, i, rng.randint(pl, ph)])
    return [pocos, canos]


_Q6_KINDS = ["sparse", "dense", "cheap_wells", "expensive_wells", "random", "empty"]
reg(Problem(
    2, "q6", "question_6", "Abastecimento de Água", "O((n+m) log n)", q6_gen, q6_oracle,
    samples=[([[5, 4, 6, 10], [(0, 1, 1), (1, 2, 2), (2, 3, 3), (0, 3, 8)]], 10),
             ([[1, 2, 2], [(0, 1, 1), (1, 2, 1)]], 3)],
    max_size=10**4, tl=5.0, small=(1, 5), medium=500,
    small_kinds=_Q6_KINDS, medium_kinds=_Q6_KINDS,
    stress=[("dense", 1.0), ("random", 1.0), ("expensive_wells", 1.0), ("cheap_wells", 1.0),
            ("empty", 1.0), ("dense_cheap", 1.0)],
    decode=lambda a: [a[0], [tuple(e) for e in a[1]]],
    brute=q6_brute, brute_range=(1, 4), slope=1.65, scale_kind="dense"))


# =============================================================================
# Q7 — Trilha de Escalada (DP em DAG: maior caminho estritamente crescente e quantas)
# =============================================================================
def q7_oracle(relevo):
    n, m = len(relevo), len(relevo[0])
    cells = sorted(((relevo[r][c], r, c) for r in range(n) for c in range(m)), reverse=True)
    L = [[1] * m for _ in range(n)]
    C = [[1] * m for _ in range(n)]
    for v, r, c in cells:
        bl = bc = 0
        for dr, dc in DIRS:
            nr, nc = r + dr, c + dc
            if 0 <= nr < n and 0 <= nc < m and relevo[nr][nc] > v:
                l = L[nr][nc]
                if l > bl:
                    bl, bc = l, C[nr][nc]
                elif l == bl:
                    bc += C[nr][nc]
        if bl:
            L[r][c], C[r][c] = bl + 1, bc % MOD
    mx = max(max(row) for row in L)
    return [mx, sum(C[r][c] for r in range(n) for c in range(m) if L[r][c] == mx) % MOD]


def q7_brute(relevo):
    n, m = len(relevo), len(relevo[0])
    old = sys.getrecursionlimit()
    sys.setrecursionlimit(10000)
    memo = {}

    def go(r, c):                      # (maior nº de células, nº de caminhos) a partir de (r,c)
        if (r, c) in memo:
            return memo[(r, c)]
        best, cnt = 1, 1
        outs = [(go(r + dr, c + dc)) for dr, dc in DIRS
                if 0 <= r + dr < n and 0 <= c + dc < m and relevo[r + dr][c + dc] > relevo[r][c]]
        if outs:
            mx = max(l for l, _ in outs)
            best, cnt = mx + 1, sum(k for l, k in outs if l == mx)
        memo[(r, c)] = (best, cnt)
        return memo[(r, c)]
    res = [go(r, c) for r in range(n) for c in range(m)]
    sys.setrecursionlimit(old)
    mx = max(l for l, _ in res)
    return [mx, sum(k for l, k in res if l == mx) % MOD]


def q7_gen(rng, size, kind):
    n = max(1, size)
    m = n if kind in ("snake", "diag", "pyramid", "flat") else rng.randint(1, n)
    if kind == "small_range":
        return [[[rng.randint(0, 3) for _ in range(m)] for _ in range(n)]]
    if kind == "flat":
        v = rng.randint(0, 10**9)
        return [[[v] * m for _ in range(n)]]
    if kind == "rows":
        return [[[i * rng.randint(1, 3) if False else i for _ in range(m)] for i in range(n)]]
    if kind == "diag":
        return [[[i + j for j in range(m)] for i in range(n)]]
    if kind == "pyramid":
        return [[[min(i, j, n - 1 - i, m - 1 - j) for j in range(m)] for i in range(n)]]
    if kind == "snake":
        g = [[0] * m for _ in range(n)]
        t = 0
        for i in range(n):
            cols = range(m) if i % 2 == 0 else range(m - 1, -1, -1)
            for j in cols:
                g[i][j] = t * 3
                t += 1
        return [g]
    return [[[rng.randint(0, 10**9) for _ in range(m)] for _ in range(n)]]


_Q7_KINDS = ["random", "small_range", "diag", "snake", "flat", "rows", "pyramid"]
reg(Problem(
    2, "q7", "question_7", "Trilha de Escalada", "O(n·m)", q7_gen, q7_oracle,
    samples=[([[[1, 2, 3], [2, 3, 4], [3, 4, 5]]], [5, 6]), ([[[7, 7], [7, 7]]], [1, 4]),
             ([[[1, 3], [2, 1]]], [2, 4]), ([[[3, 4, 5], [3, 2, 6], [2, 2, 1]]], [4, 2])],
    max_size=300, tl=6.0, small=(1, 5), medium=40,
    small_kinds=_Q7_KINDS, medium_kinds=_Q7_KINDS,
    stress=[("random", 1.0), ("small_range", 1.0), ("diag", 1.0), ("snake", 1.0), ("pyramid", 1.0), ("flat", 1.0)],
    brute=q7_brute, brute_range=(1, 5), slope=2.65, scale_kind="small_range"))


# =============================================================================
# Q8 (a) — O Carteiro Preguiçoso: menor passeio que visita todos os vértices (n <= 12)
# =============================================================================
def q8a_oracle(n, estradas):
    adj = [[] for _ in range(n)]
    for u, v in estradas:
        adj[u].append(v)
        adj[v].append(u)
    full = (1 << n) - 1
    dist, dq = {}, deque()
    for v in range(n):
        dist[(v, 1 << v)] = 0
        dq.append((v, 1 << v))
    while dq:
        v, mask = dq.popleft()
        d = dist[(v, mask)]
        if mask == full:
            return d
        for u in adj[v]:
            s = (u, mask | (1 << u))
            if s not in dist:
                dist[s] = d + 1
                dq.append(s)
    return -1


def q8a_brute(n, estradas):          # TSP-caminho sobre o fecho métrico (Floyd-Warshall + DP em bitmask)
    INF = 10**9
    D = [[0 if i == j else INF for j in range(n)] for i in range(n)]
    for u, v in estradas:
        D[u][v] = D[v][u] = 1
    for k in range(n):
        for i in range(n):
            for j in range(n):
                if D[i][k] + D[k][j] < D[i][j]:
                    D[i][j] = D[i][k] + D[k][j]
    dp = [[INF] * n for _ in range(1 << n)]
    for v in range(n):
        dp[1 << v][v] = 0
    for mask in range(1 << n):
        for v in range(n):
            if dp[mask][v] >= INF:
                continue
            for u in range(n):
                if not mask >> u & 1:
                    nm = mask | (1 << u)
                    if dp[mask][v] + D[v][u] < dp[nm][u]:
                        dp[nm][u] = dp[mask][v] + D[v][u]
    return min(dp[(1 << n) - 1])


def q8a_gen(rng, size, kind):
    n = max(2, min(12, size))
    edges = set()

    def add(u, v):
        if u != v:
            edges.add((min(u, v), max(u, v)))
    perm = list(range(n))
    rng.shuffle(perm)
    if kind == "path":
        for i in range(n - 1):
            add(perm[i], perm[i + 1])
    elif kind == "star":
        for i in range(1, n):
            add(perm[0], perm[i])
    elif kind == "cycle":
        for i in range(n):
            add(perm[i], perm[(i + 1) % n])
    elif kind == "complete":
        for i in range(n):
            for j in range(i + 1, n):
                add(i, j)
    else:
        for i in range(1, n):
            add(perm[i], perm[rng.randrange(i)])
        if kind == "sparse":
            for _ in range(rng.randint(1, 3)):
                add(rng.randrange(n), rng.randrange(n))
        elif kind == "dense":
            for i in range(n):
                for j in range(i + 1, n):
                    if rng.random() < 0.4:
                        add(i, j)
    es = [[u, v] if rng.random() < 0.5 else [v, u] for u, v in sorted(edges)]
    rng.shuffle(es)
    return [n, es]


_Q8_KINDS = ["tree", "path", "star", "cycle", "sparse", "dense", "complete"]
reg(Problem(
    2, "q8_a", "question_8_a", "O Carteiro Preguiçoso (a)", "O(2^n · n²)", q8a_gen, q8a_oracle,
    samples=[([3, [(0, 1), (1, 2)]], 2), ([4, [(0, 1), (0, 2), (0, 3)]], 4),
             ([4, [(0, 1), (1, 2), (2, 3), (3, 0)]], 3), ([5, [(0, 1), (0, 2), (0, 3), (0, 4)]], 6)],
    max_size=12, tl=8.0, small=(2, 7), medium=10, fixed_size=True,
    small_kinds=_Q8_KINDS, medium_kinds=_Q8_KINDS,
    stress=[("path", 1.0), ("star", 1.0), ("tree", 1.0), ("sparse", 1.0), ("cycle", 1.0),
            ("dense", 1.0), ("complete", 1.0)],
    decode=lambda a: [a[0], [tuple(e) for e in a[1]]],
    brute=q8a_brute, brute_range=(2, 8)))
