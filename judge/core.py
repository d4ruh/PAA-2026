"""Estruturas centrais: Problem, formato dos casos de teste (json/txt) e utilitários."""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Optional

ROOT = Path(__file__).resolve().parent.parent

SOLUTION_FILES = {1: ("lista-01", "lista-1-paa.py"), 2: ("lista-02", "lista-2-paa.py")}


def find_solution(lista: int, root: Path = ROOT, override: Optional[str] = None) -> Path:
    """Localiza o .py do aluno (case-insensitive, por causa do Windows/nomes diferentes)."""
    if override:
        p = Path(override)
        if not p.is_absolute():
            p = Path.cwd() / p
        if not p.exists():
            raise FileNotFoundError(f"Arquivo de solução não encontrado: {p}")
        return p
    folder, name = SOLUTION_FILES[lista]
    d = root / folder
    if d.is_dir():
        for f in d.iterdir():
            if f.name.lower() == name:
                return f
    raise FileNotFoundError(f"Não achei {folder}/{name} dentro de {root}")


# ----------------------------------------------------------------------------
# Comparação padrão
# ----------------------------------------------------------------------------
def norm(x: Any) -> Any:
    """tuple -> list (o JSON não distingue os dois)."""
    if isinstance(x, (list, tuple)):
        return [norm(i) for i in x]
    return x


def default_check(args, out, expected):
    return (norm(out) == norm(expected)), ""


def _identity(args):
    return args


# ----------------------------------------------------------------------------
# Problem
# ----------------------------------------------------------------------------
@dataclass
class Problem:
    lista: int
    qid: str                      # "q2", "q7_a", ...
    func: str                     # nome da função/classe no .py do aluno
    title: str
    complexity: str               # texto, ex.: "O(n log D)"
    gen: Callable                 # (rng, size, kind) -> args (lista JSON-ável)
    oracle: Callable              # (*args_decodificados) -> saída esperada
    samples: list                 # [(args, saida_do_enunciado), ...]
    max_size: int                 # tamanho do caso de estresse (driver "size")
    tl: float                     # limite de tempo (s) dos casos médios/estresse
    small: tuple = (1, 6)         # faixa de tamanho dos casos pequenos
    medium: int = 100             # tamanho dos casos médios
    small_kinds: list = field(default_factory=lambda: ["random"])
    medium_kinds: Optional[list] = None
    stress: list = field(default_factory=lambda: [("random", 1.0)])   # (kind, fração de max_size)
    check: Callable = default_check
    decode: Callable = _identity
    call: Optional[Callable] = None   # (modulo, args_decodificados) -> saída
    brute: Optional[Callable] = None  # força bruta (apenas p/ validar o gabarito: `selftest`)
    brute_range: tuple = (1, 6)
    slope: Optional[float] = None     # expoente máximo tolerado no modo `scaling`
    scale_kind: str = "random"
    tl_small: float = 2.0
    fixed_size: bool = False          # True: tamanho do estresse não escala com --scale
    normalize_kind: Optional[Callable[[str, int], str]] = None   # ajusta o "kind" antes de gerar
    size_of: Optional[Callable[[Any, str, int], Any]] = None     # tamanho real p/ o meta.json

    @property
    def key(self) -> str:
        return f"{self.lista}:{self.qid}"

    def run(self, module, args):
        if self.call is not None:
            return self.call(module, args)
        return getattr(module, self.func)(*args)


# ----------------------------------------------------------------------------
# Formato dos casos
#   json: {"v":1, ..., "args":[...], "expected": ...}
#   txt : cabeçalho "# chave: json", um argumento (JSON) por linha, "--- expected", saída esperada
# ----------------------------------------------------------------------------
HEADER_KEYS = ["lista", "question", "id", "tier", "kind", "size", "time_limit"]


def write_case(path: Path, case: dict, fmt: str = "json") -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    if fmt == "json":
        path = path.with_suffix(".json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump(case, f, separators=(",", ":"))
    elif fmt == "txt":
        path = path.with_suffix(".txt")
        with open(path, "w", encoding="utf-8") as f:
            f.write("# judge-case v1\n")
            for k in HEADER_KEYS:
                f.write(f"# {k}: {json.dumps(case[k])}\n")
            for a in case["args"]:
                f.write(json.dumps(a, separators=(",", ":")) + "\n")
            f.write("--- expected\n")
            f.write(json.dumps(case["expected"], separators=(",", ":")) + "\n")
    else:
        raise ValueError(f"formato desconhecido: {fmt}")
    return path


def read_case(path: Path, with_expected: bool = True) -> dict:
    path = Path(path)
    if path.suffix == ".json":
        with open(path, encoding="utf-8") as f:
            case = json.load(f)
        if not with_expected:
            case.pop("expected", None)
        return case
    case: dict = {"args": []}
    with open(path, encoding="utf-8") as f:
        in_expected = False
        for line in f:
            line = line.rstrip("\n")
            if not in_expected and line.startswith("#"):
                if ":" in line:
                    k, v = line[1:].split(":", 1)
                    case[k.strip()] = json.loads(v)
                continue
            if line == "--- expected":
                in_expected = True
                if not with_expected:
                    break
                continue
            if not line.strip():
                continue
            if in_expected:
                case["expected"] = json.loads(line)
            else:
                case["args"].append(json.loads(line))
    return case


def case_files(folder: Path) -> list:
    return sorted(p for p in Path(folder).glob("*") if p.suffix in (".json", ".txt") and p.stem != "meta")


def trunc(x: Any, n: int = 300) -> str:
    s = repr(x)
    return s if len(s) <= n else s[: n - 3] + f"...<{len(s)} chars>"
