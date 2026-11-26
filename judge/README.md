# judge — gerador de casos + juiz (corretude e tempo) para as listas de PAA

Coloque a pasta `judge/` na **raiz do repositório**:

```
root/
|   judge/            <- este pacote
|   lista-01/Lista-1-PAA.py
|   lista-02/lista-2-paa.py
|   tests/            <- criada por `gen` (pode ir para o .gitignore; ~260 MB com os padrões)
```

Requer apenas Python 3.9+ (biblioteca padrão). Rode **sempre a partir da raiz**.

## Uso rápido (Windows: `py -m judge ...` também funciona)

```
python -m judge gen                      # gera os casos (listas 1 e 2)
python -m judge run                      # julga tudo
python -m judge run -l 2 -q q3 q4 -v     # só lista 2, questões 3 e 4, detalhando todas as falhas
python -m judge run -q q5 --fail-fast    # para no 1º erro (como o LeetCode)
python -m judge run --tier sample small  # só exemplos + casos pequenos (rápido, bom p/ depurar)
python -m judge scaling -l 1 -q q10      # estima a complexidade empírica
python -m judge selftest                 # confere o gabarito do juiz contra força bruta
python -m judge list
```

## Veredictos
`AC` correto · `WA` resposta errada (mostra input / esperado / obtido) · `TLE` estourou o limite ·
`RE` exceção, `RecursionError`, crash ou processo morto (mostra o traceback).
Retornar `None` aparece como `WA` com o aviso "ainda não implementada".

## Como os testes são montados
Cada questão tem 4 grupos (`--tier`): **sample** (exemplos do PDF), **small** (aleatórios pequenos, vários
"kinds"), **medium** e **stress** (no tamanho máximo das restrições, com formas adversariais: ordenado, todos
iguais, cadeia de 2·10⁵ nós, grafo sem arbitragem etc.). Os de estresse são o que separa O(n) de O(n²)
e pegam recursão profunda.

* Cada caso roda em **subprocesso isolado** (prints do seu código são descartados; o gabarito nunca é
  carregado nele). O tempo medido é só o da chamada da função. Um *watchdog* mata o processo ao estourar
  o limite.
* Questões com **mais de uma resposta válida** usam verificador próprio: Q6 (L1, desempate), Q9 (L1,
  qualquer partida válida), Q1 e Q4 (L2: ordem do alfabeto / ciclo de arbitragem válidos).
* Q1 (L1) e Q8(b)/(c) (L2) são discursivas: não têm testes.

## Opções do `gen`
`--seed N` (reprodutível) · `--format json|txt` · `--small N` / `--medium N` (quantidade) ·
`--scale 0.2` (encolhe os casos médios/estresse: geração e execução bem mais rápidas) · `--out DIR`.
`txt`: cabeçalho `# chave: valor`, um argumento por linha (JSON), `--- expected`, saída esperada.
Casos extras seus: coloque arquivos no mesmo formato em `tests/lista-0X/qY/`.

## Limites de tempo
Calibrados para CPython e para uma solução correta e *razoavelmente* otimizada. Máquina lenta?
use `--tl-scale 2`. Como O(n log n) vs O(n²) pode caber no limite em tamanhos moderados, use
`scaling`: mede 4 tamanhos, ajusta t ≈ n^p e avisa se p passa do tolerado para a complexidade exigida.
É uma estimativa (ruído de máquina/GC): trate como alerta. Memória **não** é limitada.

## ⚠ Spoiler
`judge/problems/lista01.py` e `lista02.py` contêm as soluções de referência (o juiz precisa delas para
calcular as saídas esperadas dos casos grandes). Para estudar sem ver respostas, não abra esses arquivos —
depois do `gen` você não precisa deles.
