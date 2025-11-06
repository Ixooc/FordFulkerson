import copy
from collections import deque
import networkx as nx

class FlujoMaximoGrafico:

    def __init__(self): 
        self.n = 0
        self.capacidad = []
        self.aristas = []
        self.grafo_nx = None
        self.pos = None                           

        self.fuentes = []
        self.sumideros = []
        self.super_fuente = None
        self.super_sumidero = None
        self.cap_fuentes = {}
        self.cap_sumideros = {}

    def inicializar(self, n): 
        self.n = n
        self.capacidad = [[0] * n for _ in range(n)]
        self.aristas = []

    def cargar_desde_archivo(self, filepath):
        with open(filepath, 'r') as f:
            lines = f.readlines()

            n, m = map(int, lines[0].strip().split()) 
            self.inicializar(n)

            for i in range(1, m + 1):
                try:
                    u, v, p = map(int, lines[i].strip().split())
                    if p <= 0:
                        raise ValueError(f"Capacidad inválida en la línea {i+1}: {p}. La capacidad debe ser un entero positivo.")
                    self.agregar_arista(u, v, p)
                except Exception as e:
                    raise ValueError(f"Error en la línea {i+1} del archivo: {e}")


    def agregar_arista(self, desde, hacia, capacidad):
        if not (0 <= desde < self.n and 0 <= hacia < self.n):
            return
        
        if capacidad <= 0:
            return

        self.capacidad[desde][hacia] = capacidad
        
        arista_existente = False
        for i, (u, v, c) in enumerate(self.aristas):
            if u == desde and v == hacia:
                self.aristas[i] = (desde, hacia, capacidad)
                arista_existente = True
                break
        if not arista_existente:
            self.aristas.append((desde, hacia, capacidad))

        if self.grafo_nx is not None: 
            self.grafo_nx.add_edge(desde, hacia)

    def remover_arista(self, u, v):
        if self.grafo_nx.has_edge(u, v):
            self.grafo_nx.remove_edge(u, v)
            
            if u < self.n and v < self.n: 
                self.capacidad[u][v] = 0
                
            self.aristas = [a for a in self.aristas if a[:2] != (u,v)]

    def crear_grafo_networkx(self):
        self.grafo_nx = nx.DiGraph()
        self.grafo_nx.add_nodes_from(range(self.n))
        for desde, hacia, _ in self.aristas:
            self.grafo_nx.add_edge(desde, hacia)

    def remover_aristas_internas(self, fuentes, sumideros):
        aristas_a_eliminar = [
            (u, v) for u, v in list(self.grafo_nx.edges()) 
            if (u in fuentes and v in fuentes) or (u in sumideros and v in sumideros)
        ]
        
        if aristas_a_eliminar:
            self.grafo_nx.remove_edges_from(aristas_a_eliminar)
            
        for u, v in aristas_a_eliminar:
            if u < self.n and v < self.n: 
                self.capacidad[u][v] = 0
                self.aristas = [a for a in self.aristas if a[:2] != (u,v)]
        
        return aristas_a_eliminar

    def preparar_para_multifuente(self, fuentes, sumideros, cap_fuentes={}, cap_sumideros={}):
        self.fuentes, self.sumideros = fuentes, sumideros
        self.cap_fuentes, self.cap_sumideros = cap_fuentes, cap_sumideros
        self.super_fuente, self.super_sumidero = None, None
        
        self.crear_grafo_networkx() 

        if len(fuentes) > 1:
            self.super_fuente = self.n  
            self.grafo_nx.add_node(self.super_fuente)
            for f in fuentes: 
                self.grafo_nx.add_edge(self.super_fuente, f) 
        
        if len(sumideros) > 1:
            idx = self.n + (1 if self.super_fuente is not None else 0)
            self.super_sumidero = idx
            self.grafo_nx.add_node(self.super_sumidero)
            for s in sumideros: 
                self.grafo_nx.add_edge(s, self.super_sumidero) 

    def _dfs(self, u, sumidero, padre, visitado, flujo, capacidad):
        visitado[u] = True
        if u == sumidero:
            return True

        n_extendido = len(capacidad)
        
        for v in range(n_extendido):
            cap_residual = capacidad[u][v] - flujo[u][v]
            if not visitado[v] and cap_residual > 0:
                padre[v] = u  
                if self._dfs(v, sumidero, padre, visitado, flujo, capacidad):
                    return True
                    
        for v in range(n_extendido):
            cap_residual_atras = flujo[v][u]
            if not visitado[v] and cap_residual_atras > 0:
                padre[v] = -(u + 1) 
                if self._dfs(v, sumidero, padre, visitado, flujo, capacidad):
                    return True
                    
        return False
    
    def calcular_pasos_ford_fulkerson(self):
        fuente_calculo = self.super_fuente if self.super_fuente is not None else (self.fuentes[0] if self.fuentes else -1)
        sumidero_calculo = self.super_sumidero if self.super_sumidero is not None else (self.sumideros[0] if self.sumideros else -1)
        
        if fuente_calculo == -1 or sumidero_calculo == -1: 
            return [], 0
            
        n_actual = self.grafo_nx.number_of_nodes()
        
        cap_extendida = [[0] * n_actual for _ in range(n_actual)]
        for u, v in self.grafo_nx.edges():
            if u == self.super_fuente: 
                cap_extendida[u][v] = self.cap_fuentes.get(v, float('inf'))
            elif v == self.super_sumidero: 
                cap_extendida[u][v] = self.cap_sumideros.get(u, float('inf'))
            elif u < self.n and v < self.n: 
                cap_extendida[u][v] = self.capacidad[u][v]
                
        flujo_extendido = [[0] * n_actual for _ in range(n_actual)]
        total, pasos, iteracion = 0, [], 1
        
        def guardar_paso(titulo, camino=[], etiquetas=None):
            pasos.append({
                'tipo': 'flujo', 
                'titulo': titulo, 
                'flujo': [row[:self.n] for row in flujo_extendido[:self.n]],
                'flujo_extendido': copy.deepcopy(flujo_extendido), 
                'cap_extendida': copy.deepcopy(cap_extendida), 
                'camino': camino, 
                'etiquetas': etiquetas if etiquetas else {}
            })
            
        guardar_paso('Grafo Inicial')

        while True:
            padre = [-1] * n_actual
            visitado = [False] * n_actual
            
            if not self._dfs(fuente_calculo, sumidero_calculo, padre, visitado, flujo_extendido, cap_extendida):
                break 
            
            minimo_camino = float('inf')
            path_reconstruido, camino_visible, etiquetas_paso = [], [], {}
            nodo_actual = sumidero_calculo
            
            while nodo_actual != fuente_calculo:
                padre_val = padre[nodo_actual]
                
                padre_ahora = padre_val if padre_val >= 0 else -padre_val - 1
                direction = '+' if padre_val >= 0 else '-'
                
                path_reconstruido.insert(0, (padre_ahora, nodo_actual, direction))
                nodo_actual = padre_ahora

            for u, v, direction in path_reconstruido:
                
                etiqueta_padre = u
                if u == self.super_fuente:
                    etiqueta_padre = "S*"
                
                if direction == '+':
                    cap_res = cap_extendida[u][v] - flujo_extendido[u][v]
                    minimo_camino = min(minimo_camino, cap_res)
                    etiquetas_paso[v] = (f'{etiqueta_padre}+', int(round(minimo_camino)))
                    if (u < self.n and v < self.n) or u == self.super_fuente or v == self.super_sumidero:
                        camino_visible.append((u, v))
                else:
                    cap_res = flujo_extendido[v][u] 
                    minimo_camino = min(minimo_camino, cap_res)
                    etiquetas_paso[v] = (f'{etiqueta_padre}-', int(round(minimo_camino)))
                    if u < self.n and v < self.n:
                        camino_visible.append((v, u))

            guardar_paso(f'Iteración {iteracion} - Camino encontrado (Delta: {int(round(minimo_camino))})', camino_visible, etiquetas_paso)
            
            for u, v, direction in path_reconstruido:
                if direction == '+': 
                    flujo_extendido[u][v] += minimo_camino
                else: 
                    flujo_extendido[v][u] -= minimo_camino
            
            total += minimo_camino
            guardar_paso(f'Iteración {iteracion} - Flujo aplicado (Total: {int(round(total))})')
            iteracion += 1
            
        guardar_paso(f'RESULTADO FINAL - Flujo máximo: {int(round(total))}')
        
        visitado = [False] * n_actual
        cola = deque([fuente_calculo]) 
        visitado[fuente_calculo] = True
        
        while cola:
            u = cola.popleft()
            for v in range(n_actual):
                if not visitado[v] and cap_extendida[u][v] - flujo_extendido[u][v] > 0:
                    visitado[v] = True; cola.append(v)
                elif not visitado[v] and flujo_extendido[v][u] > 0:
                    visitado[v] = True; cola.append(v)
                    
        conjunto_s = {i for i, v in enumerate(visitado) if v}
        aristas_corte, capacidad_corte = [], 0
        
        for u in conjunto_s:
            for v in range(n_actual):
                cap_arista = cap_extendida[u][v]
                if v not in conjunto_s and self.grafo_nx.has_edge(u,v) and cap_arista > 0:
                    aristas_corte.append((u, v, cap_arista))
                    capacidad_corte += cap_arista
                    
        pasos.append({
            'tipo': 'corte_minimo', 
            'titulo': f'CORTE MÍNIMO ({int(round(capacidad_corte))}) = Flujo Máximo ({int(round(total))})', 
            'conjunto_s': conjunto_s, 
            'aristas_corte': aristas_corte,
            'flujo_maximo': total 
        })
        
        return pasos, total