"""
Projeto e Análise de Algoritmos — Lista 2 (Extra) — Grafos e Classes de Complexidade
FGV - EMAp — 2026

Preencha o corpo de cada função abaixo.
NÃO altere nomes de arquivo, assinaturas de funções ou nomes de métodos.
Código auxiliar (classes, funções) deve ser definido DENTRO do escopo da função
da questão correspondente.

Atenção: o limite de recursão padrão do Python é pequeno (~1000) e várias
entradas são grandes o bastante para estourá-lo.
Nas questões de análise de complexidade, justifique o custo do que você implementou.
"""


def question_1(palavras: list) -> str:
    """
    Alfabeto Perdido.

    palavras: lista de palavras (letras 'a'..'z', não vazias) em ordem
              lexicográfica segundo uma ordem de letras DESCONHECIDA.
              1 <= len(palavras) <= 10^5; o alfabeto tem no máximo 26 letras;
              a lista pode conter palavras repetidas.

    Retorna uma string com cada letra distinta que aparece nas palavras
    exatamente uma vez, em uma ordem consistente com a ordenação observada
    (qualquer ordem válida é aceita). Se a lista for inconsistente, retorna "".
    Uma palavra nunca pode vir antes de um prefixo próprio seu
    (ex: "abc" antes de "ab" é inconsistente).

    Complexidade exigida: O(C), C = total de caracteres da lista.
    """
    pass


def question_2(mapa: list) -> int:
    """
    Ponte entre as Ilhas.

    mapa: matriz n x m (lista de listas) de 0 (água) e 1 (terra), com
          2 <= n, m <= 500. Há exatamente duas ilhas (conjuntos maximais de
          células de terra conectadas na vertical/horizontal).

    Retorna o menor número de células de água que precisam ser convertidas
    em terra para que as duas ilhas formem uma só.

    Complexidade exigida: O(n · m).
    """
    pass


def question_3(altitudes: list) -> tuple:
    """
    Trilha de Menor Esforço.

    altitudes: matriz n x m (lista de listas) de inteiros,
               1 <= n, m <= 300, 1 <= altitude <= 10^6.
    A caminhante parte de (0, 0) e chega em (n-1, m-1), movendo-se para uma das
    4 células vizinhas a cada passo. O esforço de uma trilha é a maior
    diferença absoluta de altitude entre duas células consecutivas dela.

    Retorna (esforco, passos): o menor esforço possível entre todas as trilhas
    e, entre as trilhas que atingem esse esforço, o menor número de passos.

    Complexidade exigida: O(n · m · log(n · m)) ou melhor.
    """
    pass


def question_4(n: int, cotacoes: list) -> list:
    """
    Câmbio Ineficiente.

    n: número de moedas (0..n-1), 2 <= n <= 300.
    cotacoes: lista de tuplas (a, b, r), com a != b: 1 unidade da moeda a vale r
              unidades da moeda b (só nesse sentido). No máximo uma cotação por
              par ordenado.
              1 <= len(cotacoes) <= 5000, 10^-3 <= r <= 10^3.

    Arbitragem: sequência de trocas que começa e termina na mesma moeda com
    estritamente mais do que se começou (produto das cotações do ciclo > 1,
    com tolerância de 1e-9: ciclos de produto 1 NÃO são arbitragem).

    Retorna uma lista [c0, c1, ..., ck] com ck == c0 descrevendo UM ciclo de
    arbitragem, ou [] se não existir nenhum.

    Complexidade exigida: O(n · m), m = len(cotacoes).
    """
    pass


def question_5(n: int, ligacoes: list, consultas: list) -> list:
    """
    Organograma da Empresa.

    n: número de funcionários (0..n-1), raiz da hierarquia é o 0.
       2 <= n <= 2 * 10^5. A hierarquia pode ser uma "cadeia".
    ligacoes: n-1 pares (u, v) que indicam que u e v estão diretamente ligados
              (não indicam quem é o chefe de quem).
    consultas: lista de q tuplas (tipo, u, v), 1 <= q <= 2 * 10^5:
        ("A", u, v): u é chefe (direto ou indireto) de v?
        ("P", u, v): u e v são primos (mesmo nível, chefes diretos diferentes)?
    Em ambas as consultas, se u == v a resposta é False.

    Retorna a lista de respostas (bool) na ordem das consultas.

    Complexidade exigida: O(n + q) no total (cada consulta O(1) após o
    pré-processamento).
    """
    pass


def question_6(pocos: list, canos: list) -> int:
    """
    Abastecimento de Água.

    pocos: lista de n custos; pocos[i] é o custo de cavar um poço na casa i.
    canos: lista de tuplas (i, j, custo), com i != j e no máximo um cano por par
           de casas: cano possível entre as casas i e j (funciona nos dois
           sentidos; a água é transmitida por toda sequência de canos ligados).
    1 <= n <= 10^4, 0 <= len(canos) <= 10^5, 1 <= custos <= 10^5.

    Retorna o menor custo total para abastecer todas as casas.

    Complexidade exigida: O((n + m) log n), m = len(canos).
    """
    pass


def question_7(relevo: list) -> tuple:
    """
    Trilha de Escalada.

    relevo: matriz n x m (lista de listas) de altitudes,
            1 <= n, m <= 300, 0 <= altitude <= 10^9 (valores podem se repetir).
    Uma escalada começa em qualquer célula e a cada passo move-se para uma das
    4 vizinhas de altitude ESTRITAMENTE maior. Pode ter uma única célula.

    Retorna (L, c): L é o maior número de células de uma escalada e c é a
    quantidade de escaladas distintas com exatamente L células, módulo 10^9 + 7.
    (Duas escaladas são distintas se diferem na sequência de células visitadas.)

    Complexidade exigida: O(n · m) ou O(n · m · log(n · m)).
    """
    pass


def question_8_a(n: int, estradas: list) -> int:
    """
    O Carteiro Preguiçoso — item (a).

    n: número de povoados (0..n-1), 2 <= n <= 12.
    estradas: lista de pares (u, v) (mão dupla); o grafo é conexo.
    O carteiro passa por todos os povoados pelo menos uma vez, começa e termina
    onde quiser e pode repetir povoados e estradas.

    Retorna o menor número de estradas percorridas (contando repetições).

    RESPONDA AQUI (substitua este texto):
    Complexidade do seu algoritmo em função de n e do número de estradas: ...
    """
    pass


def question_8_b():
    """
    O Carteiro Preguiçoso — item (b) (discursivo, não é corrigido
    automaticamente).

    RESPONDA AQUI (substitua este texto):
    (1) Prova de que existe trajeto com exatamente n-1 estradas se e somente se
        existe caminho hamiltoniano: ...
    (2) O que isso diz sobre um algoritmo polinomial para o item (a) com n
        grande (classes de complexidade e redução polinomial): ...
    """
    pass


def question_8_c():
    """
    O Carteiro Preguiçoso — item (c) (discursivo, não é corrigido
    automaticamente).

    RESPONDA AQUI (substitua este texto):
    (1) Se a região fosse uma árvore, o problema teria algoritmo polinomial?
        Descreva um algoritmo O(n): ...
    (2) Por que isso não contradiz o item (b)? ...
    """
    pass
