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

	Implementado com ordenação topológica sobre um grafo de letras:
	cada par de palavras consecutivas gera no máximo uma aresta, então o
	grafo tem no máximo 26 vértices e 26^2 arestas; percorrer palavras e
	arestas uma vez custa O(C).
	"""

	class CharNode:
		def __init__(self, label:str) -> None:
			self.label = label
			self.in_edges = list()
			self.out_edges = list()

		def add_in_edge(self, edge:CharEdge) -> None:
			self.in_edges.append(edge)
			
		def add_out_edge(self, edge:CharEdge) -> None:
			self.out_edges.append(edge)

	class CharEdge:
		def __init__(self, origem:CharNode, destino:CharNode) -> None:
			self.origem = origem
			self.destino = destino

			origem.add_out_edge(self)
			destino.add_in_edge(self)

	def ordem_topologica(letras: list[CharNode]) -> list[CharNode]:
		n = len(letras)
		in_deg = {l: len(l.in_edges) for l in letras}

		fila = [l for l, d in in_deg.items() if d == 0]
		atual = 0
		while atual < n:
			if atual == len(fila):
				return list()

			for e in fila[atual].out_edges:
				in_deg[e.destino] -= 1
				if in_deg[e.destino] == 0:
					fila.append(e.destino)

			atual += 1

		return fila

	n = len(palavras)
	if n == 0:
		return ''
	
	vertices = dict()
	for c in palavras[0]:
		if c not in vertices:
			vertices[c] = CharNode(c)

	tam_atual = len(palavras[0])
	tam_anterior = tam_atual
	for i in range(1, n):
		tam_atual = len(palavras[i])
		relation_found = False
		
		for j in range(tam_atual):
			letra_atual = palavras[i][j]
			if letra_atual not in vertices:
				vertices[letra_atual] = CharNode(letra_atual)
				
			if j < tam_anterior and not relation_found:
				if letra_atual != palavras[i-1][j]:
					CharEdge(vertices[palavras[i-1][j]], vertices[letra_atual]) 
					relation_found = True

			if j == tam_atual-1 and tam_atual < tam_anterior and not relation_found:
				return ''

		tam_anterior = tam_atual

	ordem = ordem_topologica([v for v in vertices.values()])
	ordem_str = ''
	for v in ordem:
		ordem_str += v.label
	return ordem_str


def question_2(mapa: list) -> int:
	"""
	Ponte entre as Ilhas.

	mapa: matriz n x m (lista de listas) de 0 (água) e 1 (terra), com
		  2 <= n, m <= 500. Há exatamente duas ilhas (conjuntos maximais de
		  células de terra conectadas na vertical/horizontal).

	Retorna o menor número de células de água que precisam ser convertidas
	em terra para que as duas ilhas formem uma só.

	Complexidade exigida: O(n · m).

	Implementado com duas BFS: a primeira marca a ilha de partida e enfileira
	sua fronteira de água; a segunda avança camada a camada até a outra ilha.
	Cada célula entra na fila O(1) vezes, total O(n · m).
	"""
	def validar_coord(x, y, n, m):
		if x<0 or y<0:
			return False
		if x>=n or y>=m: 
			return False

		return True 

	n, m = len(mapa), len(mapa[0])

	start = None
	visitados = set()
	# busca pelo começo da primeira ilha O(n*m)
	for i in range(n):
		for j in range(m):
			if mapa[i][j] == 1:
				start = (i, j)
				break

		if start is not None:
			break
	
	if start is None:
		return -1 # não tem ilhas

	# BFS para identificar todos os ponto da primeira ilha O(n*m) pois o grau máximo é fixo
	# e identificar os vértices adjacentes a primeira lista para iniciar o BFS completo
	fila = list()
	ilha_fila = [start]
	atual = 0
	while atual < len(ilha_fila):
		i,j = ilha_fila[atual]
		atual+=1
		if (i, j) in visitados or not validar_coord(i, j, n, m):
			continue

		if mapa[i][j] == 0:
			fila.append((i, j, 1))
			continue

		visitados.add((i,j))
		ilha_fila.append((i+1, j))
		ilha_fila.append((i-1, j))
		ilha_fila.append((i, j+1))
		ilha_fila.append((i, j-1))

	# BFS para mapear o caminho até a segunda ilha
	fim = None
	atual = 0
	while atual < len(fila):
		i,j, dist = fila[atual]  # estrutua <x, y, dist da ilha 1>
		atual+=1
		if (i, j) in visitados or not validar_coord(i, j, n, m):
			continue

		if mapa[i][j] == 1:
			fim = fila[atual]
			break

		visitados.add((i,j))
		fila.append((i+1, j, dist+1))
		fila.append((i-1, j, dist+1))
		fila.append((i, j+1, dist+1))
		fila.append((i, j-1, dist+1))

	if fim is None:
		return -1 # só tem uma ilha

	return fim[2] - 1 # fim já é da ilha 2, não precisa de mais terra


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

	Implementado em duas fases: (1) Dijkstra de gargalo com heap mínimo acha
	o menor esforço E em O(n · m · log(n · m)); (2) BFS no subgrafo das
	arestas com diferença <= E acha o menor número de passos em O(n · m).
	"""
	import heapq
	from collections import deque

	def validar_coord(x, y, n, m):
		return 0 <= x < n and 0 <= y < m

	def get_vizinhos(x, y, n, m):
		candidatos = [(x+1, y), (x-1, y), (x, y+1), (x, y-1)]
		return [(i, j) for i, j in candidatos if validar_coord(i, j, n, m)]

	def step_diff(x1, y1, x2, y2, alt):
		return abs(alt[x1][y1] - alt[x2][y2])

	n, m = len(altitudes), len(altitudes[0])

	# busca menor esforço possvel
	INF = float("inf")
	melhor = [[INF] * m for _ in range(n)]
	melhor[0][0] = 0
	heap = [(0, 0, 0)]
	while len(heap) > 0:
		esforco, x, y = heapq.heappop(heap)
		if esforco > melhor[x][y]:
			continue
		if (x, y) == (n-1, m-1):
			break
		for i, j in get_vizinhos(x, y, n, m):
			novo = max(esforco, step_diff(x, y, i, j, altitudes))
			if novo < melhor[i][j]:
				melhor[i][j] = novo
				heapq.heappush(heap, (novo, i, j))

	E = melhor[n-1][m-1]

	# melhor dentre as diferenças <= que o menor esforço possivel
	dist = [[-1] * m for _ in range(n)]
	dist[0][0] = 0
	fila = deque([(0, 0)])
	while len(fila) > 0:
		x, y = fila.popleft()
		if (x, y) == (n-1, m-1):
			break
		for i, j in get_vizinhos(x, y, n, m):
			if dist[i][j] == -1 and step_diff(x, y, i, j, altitudes) <= E:
				dist[i][j] = dist[x][y] + 1
				fila.append((i, j))

	return E, dist[n-1][m-1]


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

	Implementado com Bellman-Ford em produtos sobre as m cotações: são n
	iterações de O(m), total O(n · m). Todas as moedas começam com 1.0 (o
	que equivale a uma super-fonte) e a reconstrução do ciclo custa O(n).
	"""
	class MoedaNode:
		def __init__(self, id: int) -> None:
			self.id = id
			self.parent: None | MoedaNode = None

		def __repr__(self) -> str:
			return f"{self.id}"

	class CambioEdge:
		def __init__(self, origem: MoedaNode, destino: MoedaNode, cambio: float) -> None:
			self.origem = origem
			self.destino = destino
			self.cambio = cambio

		def __repr__(self) -> str:
			return f"({self.origem.id}, {self.destino.id}, {self.cambio})"

	def bellman_ford_cambio(n: int, edges: list[CambioEdge]) -> None | MoedaNode:
		cotacoes_totais = [1.0 for _ in range(n)]

		for _ in range(1, n+1):
			for e in edges:
				if cotacoes_totais[e.destino.id] < cotacoes_totais[e.origem.id] * e.cambio:
					cotacoes_totais[e.destino.id] = cotacoes_totais[e.origem.id] * e.cambio
					e.destino.parent = e.origem

		arbitragem_node = None
		for e in edges:
			if cotacoes_totais[e.destino.id] < cotacoes_totais[e.origem.id] * e.cambio:
				arbitragem_node = e.destino
				e.destino.parent = e.origem

		return arbitragem_node

	nodes = [MoedaNode(i) for i in range(n)]
	edges = [CambioEdge(nodes[u], nodes[v], r) for u, v, r in cotacoes]
	cotacoes_por_par = {(u, v): r for u, v, r in cotacoes}

	cicle_node = bellman_ford_cambio(n, edges)
	if cicle_node is None:
		return list()

	# verifica se cicle_node está no ciclo 
	x = cicle_node
	for _ in range(n):
		if x.parent is None:
			return list()
		x = x.parent

	ciclo = [x.id]
	node = x.parent
	while node != x:
		ciclo.append(node.id)
		node = node.parent
	ciclo.append(x.id)

	ciclo.reverse()

	# Confere tolerância de 1e-9
	produto = 1.0
	for a, b in zip(ciclo, ciclo[1:]):
		if (a, b) not in cotacoes_por_par:
			return list()
		produto *= cotacoes_por_par[(a, b)]

	if produto <= 1 + 1e-9:
		return list()

	return ciclo


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

	Pré-processamento com DFS iterativa (pilha explícita) que calcula
	pre_order, pos_order, nível e pai em O(n); depois cada consulta é
	respondida em O(1), total O(n + q).
	"""
	class OrgNode:
		def __init__(self, id: int) -> None:
			self.id = id
			self.vizinhos = list()
			self.nivel = -1

		def __repr__(self) -> str:
			return f"{self.id}"

	class Organograma:
		def __init__(self, num_func: int, ligacoes: list[tuple[int, int]]) -> None:
			self.n = num_func
			self.funcs = [OrgNode(i) for i in range(self.n)]
			self.parents = [-1 for _ in range(self.n)]

			self.raiz = self.funcs[0]

			self._set_ligacoes(ligacoes)
			self._pre_proc()

		def _set_ligacoes(self, ligacoes: list[tuple[int, int]]) -> None:
			for u, v in ligacoes:
				self.funcs[u].vizinhos.append(self.funcs[v])
				self.funcs[v].vizinhos.append(self.funcs[u])

		def _labeling(self, raiz: OrgNode) -> None:
			# DFS iterativa com pilha
			# proximo[i] guarda o próximo vizinho de i a examinar
			proximo = [0 for _ in range(self.n)]
			pilha = [raiz]

			self.pre_order[raiz.id] = self.pre_id
			self.pre_id += 1

			while len(pilha) > 0:
				atual = pilha[-1]

				avancou = False
				while proximo[atual.id] < len(atual.vizinhos):
					v = atual.vizinhos[proximo[atual.id]]
					proximo[atual.id] += 1

					if v.id == self.parents[atual.id]:
						continue
					if self.pre_order[v.id] != -1:
						continue

					self.parents[v.id] = atual.id
					v.nivel = atual.nivel + 1
					self.pre_order[v.id] = self.pre_id
					self.pre_id += 1

					pilha.append(v)
					avancou = True
					break

				if not avancou:
					self.pos_order[atual.id] = self.pos_id
					self.pos_id += 1
					pilha.pop()

		def _pre_proc(self) -> None:
			self.pre_order = [-1 for _ in range(self.n)]
			self.pos_order = [-1 for _ in range(self.n)]

			self.pre_id = 0
			self.pos_id = 0

			self.raiz.nivel = 0
			self._labeling(self.raiz)

		def consultar(self, tipo: str, func1: int, func2: int) -> bool:
			if func1 == func2:
				return False

			if (tipo == 'A' and
				self.pre_order[func1] < self.pre_order[func2] and
				self.pos_order[func1] > self.pos_order[func2]):
				return True

			if (tipo == 'P' and
				self.funcs[func1].nivel == self.funcs[func2].nivel and
				self.parents[func1] != self.parents[func2]):
				return True

			return False

	org = Organograma(n, ligacoes)
	respostas = list()
	for c in consultas:
		respostas.append(org.consultar(*c))

	return respostas


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

	Implementado com Prim adaptado sobre um heap mínimo com decrease-key: as
	m arestas passam pelo heap no máximo uma vez, cada operação em O(log n),
	total O((n + m) log n).
	"""

	class HeapMin:
		def __init__(self) -> None:
			self.len = 0
			self.__node_arr = list()
			self.__label_map = dict() 

		def __heapfy_up(self, pos:int) -> None:
			atual = pos
			parent = int((atual-1)/2)

			while parent >= 0:
				if (self.__node_arr[atual][1] < self.__node_arr[parent][1]):
					self.__label_map[self.__node_arr[atual][0]] = parent
					self.__label_map[self.__node_arr[parent][0]] = atual
					self.__node_arr[atual], self.__node_arr[parent] = self.__node_arr[parent], self.__node_arr[atual]
					atual = parent
					parent = int((atual-1)/2)
				else:
					break

		def __heapfy_down(self, pos:int) -> None:
			atual = pos
			child1 = 2*atual+1

			while child1 < self.len:
				if child1+1 < self.len:
					min_child = child1 if (self.__node_arr[child1][1] < self.__node_arr[child1+1][1]) else child1+1
				else:
					min_child = child1

				if (self.__node_arr[atual][1] > self.__node_arr[min_child][1]):
					self.__label_map[self.__node_arr[atual][0]] = min_child
					self.__label_map[self.__node_arr[min_child][0]] = atual
					self.__node_arr[atual], self.__node_arr[min_child] = self.__node_arr[min_child], self.__node_arr[atual]
					atual = min_child
					child1 = 2*atual+1
				else:
					break

		def insert_or_update(self, label, value) -> None:
			if (label in self.__label_map):
				pos = self.__label_map[label]
				self.__node_arr[pos] = label, value
				self.__heapfy_down(pos)
				self.__heapfy_up(pos)
			else:
				self.__node_arr.append((label, value))
				self.__label_map[label] = self.len
				self.len += 1
				self.__heapfy_up(self.len-1)

		def peek(self, label=None):
			if label is not None:
				if (self.len > self.__label_map[label]):
					return self.__node_arr[self.__label_map[label]]
			elif (self.len > 0):
				return self.__node_arr[0] 

			return None, None

		def pop(self):
			if (self.len <= 0):
				return None, None

			self.len -= 1
			self.__label_map[self.__node_arr[0][0]] = self.len
			self.__label_map[self.__node_arr[self.len][0]] = 0
			self.__node_arr[0], self.__node_arr[self.len] = self.__node_arr[self.len], self.__node_arr[0]
			self.__heapfy_down(0)

			return self.__node_arr.pop()

	class HouseNode:
		def __init__(self, label, base_cost) -> None:
			self.label = label
			self.base_cost = base_cost
			self.edges = list()

		def __repr__(self) -> str:
			return f"({self.label}: {self.base_cost})"

		def add_edge(self, neighbor:HouseNode, reach_cost:int):
			self.edges.append((neighbor, reach_cost))

	def adapted_prim(nodes: list[HouseNode]) -> int:
		cost_heap = HeapMin()
		for v in nodes:
			cost_heap.insert_or_update(v.label, v.base_cost)

		total_cost = 0
		visited = set()
		while cost_heap.len > 0:
			v_label, cost = cost_heap.pop()
			if ((v_label is None) or (cost is None)):
				continue

			total_cost += cost
			visited.add(v_label)
			for u_label, reach_cost in nodes[v_label].edges:
				if u_label in visited:
					continue
				if reach_cost >= cost_heap.peek(u_label)[1]:
					continue
				cost_heap.insert_or_update(u_label, reach_cost)

		return total_cost

	nodes = [HouseNode(label, cost) for label, cost in enumerate(pocos)]
	for e in canos:
		nodes[e[0]].add_edge(e[1], e[2])
		nodes[e[1]].add_edge(e[0], e[2])

	return adapted_prim(nodes)


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

	Implementado com programação dinâmica sobre o DAG implícito (arestas vão
	sempre para altitude maior) e memoização: cada célula é processada uma
	vez e olha no máximo 4 vizinhos, total O(n · m).
	"""
	def validar_coord(x,y,n,m)->bool: # O(1)
		if x<0 or y<0:
			return False
		if x>=n or y>=m:
			return False

		return True

	def get_vizinhos_up(x,y,n,m,relevo): # O(1)
		candidatos = [(x+1,y), (x-1,y), (x,y+1), (x,y-1)]
		viz = list()
		for i, j in candidatos:
			if not validar_coord(i,j,n,m):
				continue
			if relevo[i][j] > relevo[x][y]:
				viz.append((i,j))

		return viz
	
	def get_vizinhos_down(x,y,n,m,relevo): # O(1)
		candidatos = [(x+1,y), (x-1,y), (x,y+1), (x,y-1)]
		viz = list()
		for i, j in candidatos:
			if not validar_coord(i,j,n,m):
				continue
			if relevo[i][j] < relevo[x][y]:
				viz.append((i,j))

		return viz

	def busca_maior_escalada_rec(x,y,n,m,relevo,memo_table) -> tuple[int,int]: # O(v'), onde v' é o tamanho da comp. conexa
		if not validar_coord(x,y,n,m):
			return -1,-1

		if memo_table[x][y] != (-1, -1):
			return memo_table[x][y]

		viz = get_vizinhos_up(x,y,n,m,relevo)

		if len(viz) == 0: # nenhum ponto com relevo maior em volta
			memo_table[x][y] = 1,1
			return 1, 1

		max_L, max_count = -1,-1
		for i,j in viz:
			l,c = busca_maior_escalada_rec(i,j,n,m,relevo,memo_table)
			l += 1
			if l > max_L:
				max_L, max_count = l,c
			elif l == max_L:
				max_count = (max_count + c) % (10**9 + 7)

		memo_table[x][y] = max_L, max_count
		return max_L, max_count

	def busca_maior_escalada_iter(x,y,n,m,relevo,memo_table) -> tuple[int,int]:
		stack = [(x,y)]
		while len(stack) > 0:
			i,j = stack[-1]
			if not validar_coord(i,j,n,m):
				stack.pop()
				continue
	
			if memo_table[i][j] != (-1, -1):
				# redundante, é processado direto e não entra na stack
				stack.pop()
				continue
	
			viz = get_vizinhos_up(i,j,n,m,relevo)
			if len(viz) == 0: # nenhum ponto com relevo maior em volta
				memo_table[i][j] = 1,1
				stack.pop()
				continue

			recursao = False
			l_temp,c_temp = -1,-1
			for u,v in viz: # número de vizinhos é superirormente limitado em 4
				l,c = memo_table[u][v]
				if (l,c) == (-1,-1):
					stack.append((u,v))
					recursao = True
					break

				l+=1
				if l > l_temp:
					l_temp,c_temp = l,c
				elif l==l_temp:
					c_temp = (c_temp + c) % (10**9 + 7)

			if not recursao:
				memo_table[i][j] = l_temp,c_temp
				stack.pop()

		return memo_table[x][y]

	n,m = len(relevo), len(relevo[0])

	# minimos locais são 'fontes' das comp. conexas
	minimos = [(i,j) for j in range(m) for i in range(n) if len(get_vizinhos_down(i,j,n,m,relevo)) == 0]
	memo_table = [[(-1, -1) for j in range(m)] for i in range(n)]

	max_L, max_count = -1,-1
	for x, y in minimos:
		l,c = busca_maior_escalada_iter(x,y,n,m,relevo,memo_table)
		if l > max_L:
			max_L, max_count = l,c
		elif l == max_L:
			max_count = (max_count + c) % (10**9 + 7)

	return max_L, max_count


def question_8_a(n: int, estradas: list) -> int:
	"""
	O Carteiro Preguiçoso — item (a).

	n: número de povoados (0..n-1), 2 <= n <= 12.
	estradas: lista de pares (u, v) (mão dupla); o grafo é conexo.
	O carteiro passa por todos os povoados pelo menos uma vez, começa e termina
	onde quiser e pode repetir povoados e estradas.

	Retorna o menor número de estradas percorridas (contando repetições).

	Complexidade: O(n^3 + 2^n · n^2 + m) no tempo e O(2^n · n + n^2) no
	espaço, onde m = len(estradas). O Floyd-Warshall custa O(n^3) e calcula as
	distâncias mínimas entre todos os pares de povoados; como repetir estradas
	é permitido, ir de um povoado a outro custa sempre o caminho mais curto.
	A DP de Held-Karp percorre as 2^n máscaras de povoados visitados e, para
	cada uma, testa n vértices finais e n próximos destinos, totalizando
	O(2^n · n^2). Com n <= 12 o termo exponencial domina (~6 · 10^5
	transições), e m só pesa na montagem da matriz inicial, em O(n^2 + m).
	"""
	def floyd_warshall(n, arestas):
		INF = float('inf')
		dist = [[INF for _ in range(n)] for _ in range(n)]
		for u, v in arestas:
			dist[u][v] = 1
			dist[v][u] = 1
		for i in range(n):
			dist[i][i] = 0

		for k in range(n):
			for i in range(n):
				for j in range(n):
					if dist[i][j] > dist[i][k] + dist[k][j]:
						dist[i][j] = dist[i][k] + dist[k][j]

		return dist

	def caixeiro_viajante(dist):
		n = len(dist)
		INF = float('inf')

		# matriz do tamanho dos caminhos visitandoos vértices dados pela máscara e terminando em v
		tamanho = [[INF for _ in range(n)] for _ in range(1 << n)]

		# caminhos que visitaram apenas um vértice e estão nele tem tamanho 0
		for i in range(n):
			tamanho[(1<<i)][i] = 0

		for mask in range(1, 1<<n):
			for u in range(n):
				if not (mask & (1<<u)) or (tamanho[mask][u] == INF):
					continue # u não foi visitado ou é inalcansavel

				for v in range(n):
					if (mask & (1<<v)):
						continue # v já foi visitado

					v_mask = mask | (1<<v)
					v_cost = tamanho[mask][u] + dist[u][v]

					if v_cost < tamanho[v_mask][v]:
						tamanho[v_mask][v] = v_cost

		full_mask = (1<<n) -1
		melhor_tam = INF
		for i in range(n):
			if melhor_tam > tamanho[full_mask][i]:
				melhor_tam = tamanho[full_mask][i]

		return melhor_tam

	dists = floyd_warshall(n, estradas)
	return caixeiro_viajante(dists)


def question_8_b():
	"""
	O Carteiro Preguiçoso — item (b) (discursivo, não é corrigido
	automaticamente).

	(1) Se um trajeto visita os n povoados usando exatamente n-1 estradas, ele
	tem n-1 arestas para n vértices, como cada estrada liga dois povoados, isso
	só é possível se nenhum povoado se repetir, ou seja, o trajeto é um caminho
	simples que passa por todos os vértices: um caminho hamiltoniano.
	Reciprocamente, um caminho hamiltoniano usa exatamente n-1 estradas e
	visita todos os povoados, logo é um trajeto válido.
	(2) Assim, decidir se a resposta do item (a) é n-1 resolve o Problema do
	Caminho Hamiltoniano, que é NP-completo (Karp); como Caminho Hamiltoniano
	<=p Carteiro, a versão de otimização é NP-difícil. Portanto, salvo se
	P = NP, não existe algoritmo polinomial para o item (a) com n grande — e
	um algoritmo assim provaria P = NP.
	"""
	pass


def question_8_c():
	"""
	O Carteiro Preguiçoso — item (c) (discursivo, não é corrigido
	automaticamente).

	(1) Sim. Em uma árvore, o menor passeio que visita todos os vértices
	(podendo começar e terminar em qualquer lugar) custa 2(n-1) - d, sendo d o
	diâmetro em arestas: percorrer cada aresta duas vezes dá um passeio de
	2(n-1) estradas, e escolher início e fim nos extremos do caminho mais longo
	economiza as d arestas desse caminho. O algoritmo é O(n): uma BFS/DFS a
	partir de qualquer vértice acha o mais distante u; outra a partir de u acha
	o mais distante v, e d = dist(u,v).
	(2) Não contradiz (b) porque a NP-dificuldade é um enunciado de pior caso
	sobre todos os grafos: restringir a entrada a árvores torna o problema
	tratável, e nelas o caminho hamiltoniano é trivial (só existe se a árvore
	for um caminho, isto é, grau máximo <= 2).
	"""
	pass
