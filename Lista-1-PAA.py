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

    Resolução via teorema mestre
    Primeiramente, identificamos que a função solve tem caso base T(1) = 1
    Agora, deve-se colocar a análise de complexidade na forma T(n) = a * T(n / b) + g(n)

    Como a função divide o problema em dois subcasos (esquerda/direta), onde 
    cada um possui metade do vetor, temos a = 2 e b = 2, e log_b{a} = 1. 

    Além disso, a função possui um custo constante nas três primeiras linhas, 
    um loop for iterando pela metade esquerda do vetor e implementando uma busca
    O(log{n}) para cada elemento, finalizando por um merge de custo O(n). 
    Logo, temos que g(n) seja theta(n log{n}).

    Como g(n) é theta(n^{log_b{a}} * log^k{n}) para a = b = 2 e k = 1, temos, 
    pelo caso 2 do teorema mestre, que T(n) é theta(n^{log_b{a}} * log^{k+1}{n}), 
    ou seja, T(n) é theta(n * log^2{n}).
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
    def get_num_lesser(grade:list[tuple], val:int) -> int:
        n = len(grade)

        lesser_count = 0
        row = n-1
        col = 0
        # contagem de elementos menores que val
        # passa, no máximo, por 2n elementos
        while (col < n) and (row >= 0):
            if (grade[row][col] < val):
                lesser_count += row+1
                col += 1
            else:
                row -= 1

        return lesser_count
    
    def get_num_greater(grade:list[tuple], val:int) -> int:
        n = len(grade)

        greater_count = 0
        row = 0
        col = n-1
        # contagem de elementos maiores que val
        # passa, no máximo, por 2n elementos
        while (col >= 0) and (row < n):
            if (grade[row][col] > val):
                greater_count += n-row
                col -= 1
            else:
                row += 1

        return greater_count

    n2 = len(grade)**2
    low = grade[0][0]
    high = grade[-1][-1] 

    # busca binária na diferença D (loop roda log{D} vezes)
    while low < high:
        mid = low + (high - low) // 2

        # Buscar qtd de valores menores / maiores em O(n)
        # (ser crescnte nas linhas/colunas permite que olhemos
        # no máximo n elementos por linha / coluna)
        n_lesser = get_num_lesser(grade, mid)
        n_greater = get_num_greater(grade, mid)

        # lower / upper bound de k, dado pela quantidade de elementos 
        # menores / maiores que mid, dando um range de valores iguais
        if (n_lesser < k) and (n2 - n_greater >= k):
            return mid
        elif (n_lesser < k):
            low = mid+1
        else:
            high = mid

    return low


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
    # implementação com dois ponteiros que percorrem o array apenas uma vez
    if k <= 0:
        return 0

    n = len(categorias)
    if n == 0:
        return 0

    cat_map = {}
    cat_count = 0

    atual_left = 0
    atual_right = 0
    best_left = 0
    best_right = 0

    while atual_right < n:
        cat_atual = categorias[atual_right]

        try:
            count = cat_map[cat_atual]
        except KeyError as e:
            cat_map[cat_atual] = 0
            count = 0

        if count > 0:
            atual_right += 1
            cat_map[cat_atual] += 1

        elif cat_count < k:
            atual_right += 1
            cat_map[cat_atual] += 1
            cat_count += 1

        else: # count == 0 and cat_count == k
            first_cat = categorias[atual_left]
            cat_map[first_cat] -= 1
            atual_left += 1

            if cat_map[first_cat] == 0:
                cat_count -= 1

        if (atual_right - atual_left) > (best_right - best_left):
            best_right = atual_right
            best_left = atual_left

    return best_right - best_left


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
    # implementação via BFS
    idx = {p: i for i, p in enumerate(banco)}
    if (inicial not in idx) or (final not in idx):
        return -1

    ini_id, fin_id = idx[inicial], idx[final]
    if (ini_id == fin_id):
        return 0

    n, l = len(banco), len(inicial)
    base_10 = [10 ** (l - 1 - i) for i in range(l)]

    # construção de grafo bipartido entre ids de senhas e as chaves que elas geram
    grupos = dict() # mapa de chaves para ids de senhas que complartilham a classe
    chaves_por_id = [list() for _ in range(n)] # mapa de ids de senhas para chaves da senha

    for idx, senha in enumerate(banco):
        num = int(senha)
        chaves = []
        for i in range(l):
            chave = (i, num - int(senha[i])*base_10[i]) # zero na posição i, + indice que foi removido
            chaves.append(chave)
            try:
                grupos[chave].append(idx)
            except KeyError as e:
                grupos[chave] = [idx]
        chaves_por_id[idx] = chaves

    # BFS nas senhas, pior caso visita cada uma das N senhas
    # avaliando L chaves por senha, pior caso é O(N*L)
    dists = [-1 for _ in range(n)]
    dists[ini_id] = 0
    fila = [ini_id]
    atual = 0
    visitados = set()
    while atual < len(fila):
        atual_id = fila[atual]
        if (atual_id == fin_id):
            return dists[atual]

        for chave in chaves_por_id[atual_id]: # Avalia L chaves por senha
            if (chave not in visitados): # Entra em cada chave apenas uma vez
                visitados.add(chave)
                for vizinho in grupos[chave]: # Limitado em, no máximo, 10 vizinhos por construção 
                    if (dists[vizinho] == -1):
                        dists[vizinho] = dists[atual_id] + 1
                        fila.append(vizinho)
        atual += 1

    return -1


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

    class Node:
        def __init__(self, chave, valor) -> None:
            self.chave = chave
            self.valor = valor
            self.next = None
            self.prev = None

    class Lista:
        def __init__(self) -> None:
            self.head = None # mais recente
            self.tail = None # mais antigo

        def display_list(self):
            atual = self.tail
            while atual:
                print(f'Chave: {atual.chave} | Valor: {atual.valor}')
                atual = atual.next

    def __init__(self, capacidade: int):
        self.capacidade = capacidade
        self.size = 0

        self.lista = self.Lista()
        self.mapa = dict()

    def consultar(self, chave):
        try:
            node = self.mapa[chave]
            if node is None:
                return -1
            if self.lista.head is node:
                return node.valor
            
            next_node = node.next
            prev_node = node.prev

            if prev_node:
                prev_node.next = next_node
            elif self.lista.tail:
                self.lista.tail = next_node

            if next_node:
                next_node.prev = prev_node

            if self.lista.head:
                self.lista.head.next = node

            node.prev = self.lista.head
            node.next = None
            self.lista.head = node

            return node.valor

        except KeyError as e:
            return -1

    def atualizar(self, chave, valor) -> None:
        if chave in self.mapa:
            node = self.mapa[chave]
            self.consultar(chave) # já resolve ponteiros

            node.valor = valor

        else:
            node = self.Node(chave, valor)
            self.mapa[chave] = node

            if self.lista.head:
                self.lista.head.next = node
                
            node.prev = self.lista.head
            self.lista.head = node

            if self.lista.tail is None:
                self.lista.tail = node

            if self.size == self.capacidade:
                if self.lista.tail and self.lista.tail is not node:
                    old_tail = self.lista.tail
                    new_tail = old_tail.next
    
                    self.lista.tail.next = None
                    self.lista.tail = new_tail
                    new_tail.prev = None

                    del self.mapa[old_tail.chave]
                    del old_tail
            else:
                self.size += 1


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
    n = len(reproducoes)
    count_musicas = dict()

    # Exploração da lista de reproduções em O(n)
    for musica in reproducoes:
        try:
            count_musicas[musica] += 1
        except KeyError as e:
            count_musicas[musica] = 1

    # Passa por todas as músicas em O(n) classificando em bucket de reproduções ordenados
    order_count = [list() for _ in range(n)]
    for musica, count in count_musicas.items():
        order_count[count-1].append(musica)

    # Seleção sequencial inversa das primeiras k músicas que aparecem nos buckets ordenads 
    adicionadas = 0
    order_musica = list()
    for count in range(n):
        if len(order_count[n-count-1]) == 0:
            continue

        for musica in order_count[n-count-1]:
            order_musica.append(musica)
            adicionadas += 1
            if adicionadas == k:
                return order_musica

    return order_musica


def question_7_a(scores: list, k: int) -> int:
    """
    Análise de Crédito - item (a).

    scores: lista não ordenada de n inteiros.
    k: 1 <= k <= n.

    Retorna o k-ésimo menor score.
    Complexidade exigida: tempo esperado O(n) (caso médio).

    QuickSelect in-place com pivot arbitrário
    Em geral, separa bem a lista, sendo O(n)
    No pior caso (ex: lista já ordenada), remove apenas um a cada iteração O(n^2) 
    """

    def partition(v:list, low:int, high:int) -> int:
        """_summary_

        Parameters
        ----------
        v : list
            Lista orgininal 
        low : int
            Índice do limite inferior do intervalo que está sendo particionado
        high : int
            Índice do limite superior do intervalo que está sendo particionado

        Returns
        -------
        int
            Índice do pivot na posição certa (abaixo todos menores, acima todos maiores ou iguais)
        """
        if low == high:
            return low

        pivot = high
        high -= 1

        while low < high:
            # avança o ponteiro esquerdo ao máximo 
            while (v[low] < v[pivot]) and (low < high):
                low += 1

            # avança o ponteiro direito ao máximo
            while (v[high] >= v[pivot]) and (high > low):
                high -= 1

            # caso tenha saído do while devido à má ordenação, faz troca
            if (v[low] >= v[pivot]) and (v[high] < v[pivot]):
                v[low], v[high] = v[high], v[low]  

        # saída em high = low
        if (v[low] >= v[pivot]):
            v[low], v[pivot] = v[pivot], v[low] 
            return low
        else:
            # low nunca é o pivot, e caso seja pivot - 1, troca não faz nada
            v[low+1], v[pivot] = v[pivot], v[low+1]
            return low + 1

    def quick_select(v, low, high, k):
        # elementos à esquerda são menores e elementos à direita são maiores
        slice_point = partition(v, low, high)
        if slice_point == k - 1:
            # elemento de índice slice_point está na posição certá e é o k-ésimo
            return v[slice_point] 
        elif slice_point < k - 1:
            # k-ésimo à direita
            # k é atualizado removendo o número de elementos que foram excluídos
            return quick_select(v, slice_point+1, high, k)
        else:
            # k-ésimo à esquerda
            return quick_select(v, low, slice_point-1, k)

    return quick_select(scores, 0, len(scores)-1, k)


def question_7_b(scores: list, k: int) -> int:
    """
    Análise de Crédito - item (b).

    Mesmo problema do item (a), mas agora a complexidade deve ser O(n)
    também no pior caso.

    QuickSelect in-place com pivot escolhido via median of medians
    Median of Medians faz com que o pivot escolhido separe o 
    vetor em duas metades de tamanho relativamente parecido, de 
    modo que permita uma complexidade O(n)
    """
    def median_brute_force(v:list, low, high):
        for i in range(low, high):
            for j in range(low, high-i):
                if (v[j] > v[j+1]):
                    v[j+1], v[j] = v[j], v[j+1]

        return v[low + (high - low) // 2]

    def median_of_medians(v, low, high):
        if low == high:
            return v[low]

        n = high - low + 1
        medians = [0 for _ in range(int((n+4)/5))]
        pos = low
        i = 0
        while pos <= high:
            resto = high - pos
            medians[i] = median_brute_force(v, pos, pos + 4 if resto > 4 else pos + resto)

            pos += 5
            i += 1

        return medians[i-1] if (i == 1) else median_of_medians(medians, 0, i-1)

    def partition_MoM(v:list, low:int, high:int) -> int:
        """_summary_

        Parameters
        ----------
        v : list
            Lista orgininal 
        low : int
            Índice do limite inferior do intervalo que está sendo particionado
        high : int
            Índice do limite superior do intervalo que está sendo particionado

        Returns
        -------
        int
            Índice do primeiro elemento maior ou igual à mediana das medianas
        """
        if low == high:
            return low

        mom = median_of_medians(v, low, high)
        pivot = -1
        for idx in range(low, high + 1):
            if v[idx] == mom:
                v[idx], v[high] = v[high], v[idx]
                pivot = high
                high -= 1
                break

        if (pivot == -1):
            return -1

        while low < high:
            # avança o ponteiro esquerdo ao máximo 
            while (v[low] < v[pivot]) and (low < high):
                low += 1

            # avança o ponteiro direito ao máximo
            while (v[high] >= v[pivot]) and (high > low):
                high -= 1

            # caso tenha saído do while devido à má ordenação, faz troca
            if (v[low] >= v[pivot]) and (v[high] < v[pivot]):
                v[low], v[high] = v[high], v[low]  

        # saída em high = low
        if (v[low] >= v[pivot]):
            v[low], v[pivot] = v[pivot], v[low] 
            return low
        else:
            # low nunca é o pivot, e caso seja pivot - 1, troca não faz nada
            v[low+1], v[pivot] = v[pivot], v[low+1]
            return low + 1
    
    def quick_select_MoM(v, low, high, k):
        # elementos à esquerda são menores e elementos à direita são maiores
        slice_point = partition_MoM(v, low, high)
        if slice_point == k - 1:
            # elemento de índice slice_point está na posição certá e é o k-ésimo
            return v[slice_point] 
        elif slice_point < k - 1:
            # k-ésimo à direita
            # k é atualizado removendo o número de elementos que foram excluídos
            return quick_select_MoM(v, slice_point+1, high, k)
        else:
            # k-ésimo à esquerda
            return quick_select_MoM(v, low, slice_point-1, k)

    return quick_select_MoM(scores, 0, len(scores) - 1, k)


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

    # Mesclar as listas duas a duas sequencialmente não atinge esse limite pois
    # o acúmulo cresce de forma à soma dar O(n*k), entretanto, utilizar heaps 
    # de tamanho k com os primeiros elementos de cada comunidade permite um
    # colocar um novo elemento na posição certa em log k e, passando por todos 
    # os n elementos, podemos ordenar tudo em O(n*log{k})

    def heapfy_up(heap_arr: list, low, high):
        # nós compostos por tupla chave (timestamp) + valor (comunidade)
        atual_logico = high - low # último
        pai_logico = (atual_logico-1) // 2
        while pai_logico >= 0: 
            if heap_arr[atual_logico + low][0] < heap_arr[pai_logico + low][0]:
                heap_arr[atual_logico + low], heap_arr[pai_logico + low] = heap_arr[pai_logico + low], heap_arr[atual_logico + low]
                atual_logico = pai_logico
                pai_logico = (atual_logico-1) // 2
            else: # próximos pais serão menores, logo já subiu tudo que podia
                break

    def heapfy_down(heap_arr, low, high):
        atual = 0
        max_logico = high - low
        while (2*atual+1 <= max_logico):
            if (2*atual+2 > max_logico):
                if heap_arr[atual + low][0] > heap_arr[2*atual+1 + low][0]:
                    heap_arr[atual + low], heap_arr[2*atual+1 + low] = heap_arr[2*atual+1 + low], heap_arr[atual + low]
                else:
                    break
            else:
                if (heap_arr[atual + low][0] > heap_arr[2*atual+1 + low][0]) and (heap_arr[2*atual+1+low][0] <= heap_arr[2*atual+2+low][0]):
                    heap_arr[atual+low], heap_arr[2*atual+1+low] = heap_arr[2*atual+1+low], heap_arr[atual+low]
                    atual = 2*atual+1
                elif (heap_arr[atual+low][0] > heap_arr[2*atual+2+low][0]) and (heap_arr[2*atual+1+low][0] > heap_arr[2*atual+2+low][0]):
                    heap_arr[atual+low], heap_arr[2*atual+2+low] = heap_arr[2*atual+2+low], heap_arr[atual+low]
                    atual = 2*atual+2
                else:
                    break

    k = len(comunidades)
    n = sum([len(lista) for lista in comunidades])

    # inicialização da min heap com os primeiros elementos de cada lista O(k * log{k}) <= O(n * log{k})
    comunidades_heap = list()
    for c in range(k):
        comunidades_heap.append((comunidades[c][0], c))
        heapfy_up(comunidades_heap, 0, len(comunidades_heap) - 1)

    # remove o menor elemento da heap por um novo elemento 
    # da comunidade e reorganiza a heap em O(log{k})
    # repete para os n posts, totalizando O(n * log{k})
    atual_comunidade = [1 for _ in range(k)]
    comunidades_sorted = list()
    for _ in range(n):
        val, c = comunidades_heap[0]
        comunidades_sorted.append(val)
        if (len(comunidades[c]) > atual_comunidade[c]):
            comunidades_heap[0] = (comunidades[c][atual_comunidade[c]], c)
            atual_comunidade[c] += 1
            heapfy_down(comunidades_heap, 0, len(comunidades_heap)-1)
        elif (len(comunidades_heap) > 1):
            comunidades_heap[0] = comunidades_heap.pop()
            heapfy_down(comunidades_heap, 0, len(comunidades_heap)-1)

    # retorna a lista com os timestamps
    return comunidades_sorted


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
    # Busca exaustiva calculando o saldo em cada trajetória possível
    # no pior caso, tenta n trajetórias de tamanho O(n), totalizando O(n^2)

    n = len(energia)

    for start in range(n):
        bateria = 0
        for i in range(n):
            bateria += energia[(start + i) % n] - consumo[(start + i) % n]
            if (bateria < 0):
                break

        if (bateria >= 0):
            return start

    return -1


def question_9_b(energia: list, consumo: list) -> int:
    """
    Autonomia Elétrica — item (b).

    Mesmo problema do item (a), mas sabendo que a solução (quando existe)
    é única, resolva com complexidade O(n).
    """
    n = len(energia)

    # Se, começando em A, conseguimos chegar em B, mas o saldo de bateria fica negativo
    # ao tentar chegar em B+1, então nenhuma estação entre A e B pode ser a solução, 
    # pois começar em uma estação C em {A+1, A+2, ..., B} seria equivalente a refazer
    # a trajetória sem o saldo (necessáriamente não negativo) obtido no trajeto de A até C. 
    # Logo podemos resolver o problema com apenas uma travessia pelo array, ou seja, O(n)
    # (pois, se reiniciamos o ciclo e paramos no meio do caminho, caímos no caso citado)

    start = 0
    passos = 0
    while passos < n:
        # reinicia uma nova trajetória com saldo 0
        bateria = 0
        atual = start
        percorrido = 0
        while percorrido < n:
            # queremos percorrer o circuito inteiro com saldo não negativo a cada passo
            prox = (atual + 1) % n
            bateria += energia[atual] - consumo[atual]
            if (bateria < 0):
                start = (atual + 1) % n
                passos += percorrido + 1
                break
            else:
                percorrido += 1
                atual = prox

            if (percorrido >= n):
                return start

    # Se voltamos ao início, caímos no problema citado acima
    return -1


def question_10(altitudes: list) -> int:
    """
    Trilha de Picos de Montanha.

    altitudes: lista de n inteiros (podem se repetir), na ordem em que
               aparecem na trilha.

    Retorna o tamanho da maior subsequência estritamente crescente.
    Complexidade exigida: O(n log n).
    """

    n = len(altitudes)

    maior = 0
    finais = [-1 for _ in range(n+1)]
    anteriores = [-1 for _ in range(n)]
    for idx in range(n):
        low = 1
        high = maior + 1 
        while (low < high):
            mid = low + int((high - low) / 2)
            if (altitudes[finais[mid]] >= altitudes[idx]):
                high = mid
            else:
                low = mid+1

        tam_seq = low
        anteriores[idx] = finais[tam_seq-1]
        finais[tam_seq] = idx

        if (tam_seq > maior):
            maior = tam_seq

    return maior