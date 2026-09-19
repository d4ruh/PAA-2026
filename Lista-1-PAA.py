"""
Projeto e Análise de Algoritmos — Lista 1
FGV - EMAp — 2026

Preencha o corpo de cada função/classe abaixo.
NÃO altere nomes de arquivo, assinaturas de funções/classes ou nomes de métodos.
Código auxiliar (classes, funções) deve ser definido DENTRO do escopo da questão
correspondente (ex: dentro de question_2, ou dentro do __init__ da classe, etc).
"""


def question_1():
    """
    Recorrência com Busca Embutida.

    int solve(int v[], int left, int right) {
        int n = right - left + 1;
        if (n <= 1) return 0;
        int mid = (left + right) / 2;
        int count = solve(v, left, mid) + solve(v, mid + 1, right);
        for (int i = left; i <= mid; i++) {
            count += binarySearchCount(v, mid + 1, right, v[i]);
        }
        merge(v, left, mid, right);
        return count;
    }

    binarySearchCount roda em O(log n) e merge roda em O(n).

    RESPONDA AQUI:
    """
    pass


def question_2(grade: list, k: int) -> int:
    """
    Painel de Sensores.

    grade: matriz n x n (lista de listas/tuplas) com linhas e colunas
           ordenadas de forma crescente.
    k: inteiro, 1 <= k <= n^2.

    Retorna a k-ésima menor leitura da grade.
    Complexidade exigida: O(n log D), onde D = max(grade) - min(grade).
    """
    pass


def question_3(categorias: list, k: int) -> int:
    """
    Maratona de Podcasts.

    categorias: lista de n inteiros (categoria de cada episódio, em ordem
                de publicação).
    k: número máximo de categorias distintas permitidas no trecho.

    Retorna o tamanho do maior trecho contínuo com no máximo k categorias
    distintas.
    Complexidade exigida: O(n).
    """
    pass


def question_4(inicial: str, final: str, banco: list) -> int:
    """
    Central de Senhas.

    inicial, final: strings de tamanho L, compostas por dígitos '0'-'9'.
    banco: lista de N strings (todas de tamanho L) representando senhas
           seguras cadastradas. inicial e final estão garantidamente em banco.

    Retorna o menor número de trocas de um único caractere por vez, passando
    sempre por senhas do banco, para transformar inicial em final.
    Retorna -1 se não for possível.
    Complexidade exigida: O(N * L).
    """
    pass


class Cache:
    """
    Cache Inteligente (Q5).

    Cache(capacidade): cria um cache com capacidade fixa `capacidade`.
    consultar(chave): retorna o valor associado à chave (e marca como mais
                       recentemente usada) ou -1 se a chave não existir.
    atualizar(chave, valor): insere/atualiza o valor associado à chave,
                              marcando-a como mais recentemente usada.
                              Se o cache estiver cheio e a chave for nova,
                              remove antes a entrada menos recentemente usada.

    Ambas as operações devem custar O(1) no caso médio.
    """

    def __init__(self, capacidade: int):
        pass

    def consultar(self, chave):
        pass

    def atualizar(self, chave, valor) -> None:
        pass


def question_6(reproducoes: list, k: int) -> list:
    """
    Rádio Digital.

    reproducoes: lista com n identificadores de música (podem se repetir
                 livremente), representando o histórico de reproduções do dia.
    k: número de músicas mais tocadas a retornar.

    Retorna uma lista com as k músicas mais tocadas, em ordem DECRESCENTE
    de número de reproduções (em caso de empate na frequência, qualquer
    ordem entre elas é aceita).

    Caso o número de músicas distintas tocadas seja menor que k, retorne
    todas as músicas distintas (nesse caso a lista de retorno terá menos
    de k elementos).

    Complexidade exigida: O(n) no total — não é permitido ordenar por
    frequência com um algoritmo O(n log n) ou O(n log k) (nem sequer usar
    uma heap para isso). Pense em como o fato de a frequência de qualquer
    música estar sempre entre 0 e n pode ser explorado.
    """
    pass


def question_7_a(scores: list, k: int) -> int:
    """
    Análise de Crédito - item (a).

    scores: lista não ordenada de n inteiros.
    k: 1 <= k <= n.

    Retorna o k-ésimo menor score.
    Complexidade exigida: tempo esperado O(n) (caso médio).
    """
    pass


def question_7_b(scores: list, k: int) -> int:
    """
    Análise de Crédito - item (b).

    Mesmo problema do item (a), mas agora a complexidade deve ser O(n)
    também no pior caso.
    """
    pass


def question_8(comunidades: list) -> list:
    """
    Feed Consolidado.

    comunidades: lista com k listas de inteiros, cada uma já ordenada de
                 forma crescente. O total de elementos somando todas as
                 listas é n.

    Retorna uma única lista com todos os elementos, ordenada de forma
    crescente.
    Complexidade exigida: O(n log k).
    """
    pass


def question_9_a(energia: list, consumo: list) -> int:
    """
    Autonomia Elétrica — item (a).

    energia[i]: energia recarregada na estação i.
    consumo[i]: energia gasta para ir da estação i até a estação (i+1) mod n.

    Retorna o índice de uma estação de partida a partir da qual é possível
    completar o circuito inteiro sem a bateria ficar negativa em nenhum
    trecho, ou -1 se não existir tal estação.

    Descreva (em comentário) uma solução por froça bruta que teste, para
    cada possível estação de partida, se o circuito completo é viável.
    Qual a complexidade dessa abordagem?
    """
    pass


def question_9_b(energia: list, consumo: list) -> int:
    """
    Autonomia Elétrica — item (b).

    Mesmo problema do item (a), mas sabendo que a solução (quando existe)
    é única, resolva com complexidade O(n).
    """
    pass


def question_10(altitudes: list) -> int:
    """
    Trilha de Picos de Montanha.

    altitudes: lista de n inteiros (podem se repetir), na ordem em que
               aparecem na trilha.

    Retorna o tamanho da maior subsequência estritamente crescente.
    Complexidade exigida: O(n log n).
    """
    pass
