import random
import matplotlib.pyplot as plt
import networkx as nx
from matplotlib.patches import FancyBboxPatch
import time

class FlujoMaximoGrafico:
    def __init__(self):
        self.n = 0
        self.capacidad = []
        self.flujo = []
        self.aristas = []
        self.grafo_nx = None
        self.pos = None
        
    def inicializar(self, n):
        """Inicializa las matrices con n nodos"""
        self.n = n
        self.capacidad = [[0] * n for _ in range(n)]
        self.flujo = [[0] * n for _ in range(n)]
        self.aristas = []
        self.crear_grafo_networkx()
        
    def agregar_arista(self, desde, hacia, capacidad):
        """Agrega una arista al grafo"""
        self.capacidad[desde][hacia] = capacidad
        self.aristas.append((desde, hacia, capacidad))
        self.grafo_nx.add_edge(desde, hacia, capacidad=capacidad, flujo=0)
        
    def crear_grafo_networkx(self):
        """Crea el grafo NetworkX para visualización"""
        self.grafo_nx = nx.DiGraph()
        self.grafo_nx.add_nodes_from(range(self.n))
        
        # Posicionar nodos en círculo para mejor visualización
        self.pos = nx.circular_layout(self.grafo_nx)
        
    def mostrar_grafo_inicial(self):
        """Muestra el grafo inicial con capacidades"""
        plt.figure(figsize=(12, 8))
        plt.title("GRAFO INICIAL - Capacidades", fontsize=16, fontweight='bold')
        
        # Dibujar nodos
        nx.draw_networkx_nodes(self.grafo_nx, self.pos, 
                              node_color='lightblue', 
                              node_size=800, 
                              alpha=0.9)
        
        # Dibujar etiquetas de nodos
        nx.draw_networkx_labels(self.grafo_nx, self.pos, 
                               font_size=12, 
                               font_weight='bold')
        
        # Dibujar aristas
        nx.draw_networkx_edges(self.grafo_nx, self.pos, 
                              edge_color='gray', 
                              arrows=True, 
                              arrowsize=20,
                              width=2)
        
        # Etiquetas de capacidades
        edge_labels = {}
        for desde, hacia, cap in self.aristas:
            edge_labels[(desde, hacia)] = f"{cap}"
            
        nx.draw_networkx_edge_labels(self.grafo_nx, self.pos, 
                                    edge_labels, 
                                    font_size=10,
                                    bbox=dict(boxstyle="round,pad=0.2", 
                                            facecolor="white", 
                                            alpha=0.8))
        
        plt.axis('off')
        plt.tight_layout()
        plt.show()
        
    def mostrar_grafo_con_flujo(self, fuente, sumidero, iteracion=None, camino_actual=None):
        """Muestra el grafo con flujo actual"""
        plt.figure(figsize=(14, 10))
        
        if iteracion is not None:
            plt.title(f"FORD-FULKERSON - Iteración {iteracion}", 
                     fontsize=16, fontweight='bold')
        else:
            plt.title("RESULTADO FINAL - Flujo Máximo", 
                     fontsize=16, fontweight='bold')
        
        # Colores de nodos
        node_colors = []
        for i in range(self.n):
            if i == fuente:
                node_colors.append('lightgreen')  # Fuente
            elif i == sumidero:
                node_colors.append('lightcoral')  # Sumidero
            elif camino_actual and i in [arista[0] for arista in camino_actual] + [arista[1] for arista in camino_actual]:
                node_colors.append('yellow')  # Nodos del camino actual
            else:
                node_colors.append('lightblue')  # Nodos normales
        
        # Dibujar nodos
        nx.draw_networkx_nodes(self.grafo_nx, self.pos, 
                              node_color=node_colors, 
                              node_size=1000, 
                              alpha=0.9)
        
        # Etiquetas de nodos
        nx.draw_networkx_labels(self.grafo_nx, self.pos, 
                               font_size=12, 
                               font_weight='bold')
        
        # Colores de aristas
        edge_colors = []
        edge_widths = []
        
        for desde, hacia, cap in self.aristas:
            flujo_actual = self.flujo[desde][hacia]
            
            # Si está en el camino actual, resaltarlo
            if camino_actual and (desde, hacia) in camino_actual:
                edge_colors.append('red')
                edge_widths.append(4)
            # Si tiene flujo, colorearlo según la saturación
            elif flujo_actual > 0:
                if flujo_actual == cap:
                    edge_colors.append('darkred')  # Saturada
                else:
                    edge_colors.append('blue')  # Con flujo
                edge_widths.append(3)
            else:
                edge_colors.append('gray')  # Sin flujo
                edge_widths.append(1)
        
        # Dibujar aristas
        edges = [(desde, hacia) for desde, hacia, _ in self.aristas]
        nx.draw_networkx_edges(self.grafo_nx, self.pos, 
                              edgelist=edges,
                              edge_color=edge_colors, 
                              width=edge_widths,
                              arrows=True, 
                              arrowsize=20)
        
        # Etiquetas de aristas: flujo/capacidad
        edge_labels = {}
        for desde, hacia, cap in self.aristas:
            flujo_actual = self.flujo[desde][hacia]
            edge_labels[(desde, hacia)] = f"{flujo_actual}/{cap}"
            
        nx.draw_networkx_edge_labels(self.grafo_nx, self.pos, 
                                    edge_labels, 
                                    font_size=9,
                                    bbox=dict(boxstyle="round,pad=0.3", 
                                            facecolor="white", 
                                            alpha=0.9))
        
        # Leyenda
        legend_elements = [
            plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='lightgreen', 
                      markersize=10, label='Fuente'),
            plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='lightcoral', 
                      markersize=10, label='Sumidero'),
            plt.Line2D([0], [0], color='red', linewidth=4, label='Camino actual'),
            plt.Line2D([0], [0], color='blue', linewidth=3, label='Con flujo'),
            plt.Line2D([0], [0], color='darkred', linewidth=3, label='Saturada'),
            plt.Line2D([0], [0], color='gray', linewidth=1, label='Sin flujo')
        ]
        
        plt.legend(handles=legend_elements, loc='upper left', bbox_to_anchor=(1, 1))
        
        plt.axis('off')
        plt.tight_layout()
        plt.show()
    
    def mostrar_corte_minimo(self, fuente, conjunto_s, conjunto_t, aristas_corte):
        """Visualiza el corte mínimo"""
        plt.figure(figsize=(14, 10))
        plt.title("CORTE MÍNIMO", fontsize=16, fontweight='bold')
        
        # Colores de nodos según el conjunto
        node_colors = []
        for i in range(self.n):
            if i in conjunto_s:
                node_colors.append('lightgreen')  # Conjunto S
            else:
                node_colors.append('lightcoral')  # Conjunto T
        
        # Dibujar nodos
        nx.draw_networkx_nodes(self.grafo_nx, self.pos, 
                              node_color=node_colors, 
                              node_size=1000, 
                              alpha=0.9)
        
        # Etiquetas de nodos con conjunto
        node_labels = {}
        for i in range(self.n):
            conjunto = "S" if i in conjunto_s else "T"
            node_labels[i] = f"{i}\n({conjunto})"
        
        nx.draw_networkx_labels(self.grafo_nx, self.pos, 
                               labels=node_labels,
                               font_size=10, 
                               font_weight='bold')
        
        # Colores de aristas
        edge_colors = []
        edge_widths = []
        
        for desde, hacia, cap in self.aristas:
            if (desde, hacia) in aristas_corte:
                edge_colors.append('red')  # Arista del corte
                edge_widths.append(5)
            else:
                edge_colors.append('gray')
                edge_widths.append(1)
        
        # Dibujar aristas
        edges = [(desde, hacia) for desde, hacia, _ in self.aristas]
        nx.draw_networkx_edges(self.grafo_nx, self.pos, 
                              edgelist=edges,
                              edge_color=edge_colors, 
                              width=edge_widths,
                              arrows=True, 
                              arrowsize=20)
        
        # Etiquetas de aristas del corte
        edge_labels = {}
        for desde, hacia in aristas_corte:
            cap = self.capacidad[desde][hacia]
            edge_labels[(desde, hacia)] = f"CAP:{cap}"
            
        nx.draw_networkx_edge_labels(self.grafo_nx, self.pos, 
                                    edge_labels, 
                                    font_size=10,
                                    bbox=dict(boxstyle="round,pad=0.3", 
                                            facecolor="yellow", 
                                            alpha=0.9))
        
        # Leyenda
        legend_elements = [
            plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='lightgreen', 
                      markersize=10, label='Conjunto S (alcanzable)'),
            plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='lightcoral', 
                      markersize=10, label='Conjunto T (no alcanzable)'),
            plt.Line2D([0], [0], color='red', linewidth=5, label='Aristas del corte')
        ]
        
        plt.legend(handles=legend_elements, loc='upper left', bbox_to_anchor=(1, 1))
        
        plt.axis('off')
        plt.tight_layout()
        plt.show()
    
    def dfs(self, nodo_actual, sumidero, padre):
        """DFS para buscar camino aumentante"""
        if nodo_actual == sumidero:
            return True
        
        for siguiente in range(self.n):
            if self.capacidad[nodo_actual][siguiente] == 0:
                continue
                
            if padre[siguiente] != -1:
                continue
            
            flujo_restante = self.flujo[nodo_actual][siguiente]
            if flujo_restante != self.capacidad[nodo_actual][siguiente]:
                padre[siguiente] = nodo_actual
                if self.dfs(siguiente, sumidero, padre):
                    return True
        
        return False
    
    def ford_fulkerson_visual(self, fuente, sumidero):
        """Ford-Fulkerson con visualización paso a paso"""
        print(f"\n=== ALGORITMO FORD-FULKERSON VISUAL ===")
        print(f"Fuente: {fuente}, Sumidero: {sumidero}")
        print("Presiona Enter para avanzar paso a paso...")
        
        # Mostrar grafo inicial
        self.mostrar_grafo_inicial()
        input("Presiona Enter para comenzar el algoritmo...")
        
        # Reiniciar flujo
        self.flujo = [[0] * self.n for _ in range(self.n)]
        
        total = 0
        iteracion = 1
        
        while True:
            padre = [-1] * self.n
            
            if not self.dfs(fuente, sumidero, padre):
                break
            
            print(f"\n--- Iteración {iteracion} ---")
            
            # Reconstruir camino
            minimo = float('inf')
            nodo_actual = sumidero
            camino = []
            
            while nodo_actual != fuente:
                padre_ahora = padre[nodo_actual]
                camino.insert(0, (padre_ahora, nodo_actual))
                nuevo = self.capacidad[padre_ahora][nodo_actual] - self.flujo[padre_ahora][nodo_actual]
                minimo = min(minimo, nuevo)
                nodo_actual = padre_ahora
            
            print(f"Camino encontrado: {' -> '.join([str(c[0]) for c in camino] + [str(camino[-1][1])])}")
            print(f"Flujo del camino: {minimo}")
            
            # Mostrar estado actual con camino resaltado
            self.mostrar_grafo_con_flujo(fuente, sumidero, iteracion, camino)
            input("Presiona Enter para aplicar el flujo...")
            
            # Actualizar flujo
            nodo_actual = sumidero
            while nodo_actual != fuente:
                padre_ahora = padre[nodo_actual]
                self.flujo[padre_ahora][nodo_actual] += minimo
                nodo_actual = padre_ahora
            
            total += minimo
            print(f"Flujo acumulado: {total}")
            
            # Mostrar estado después de aplicar flujo
            self.mostrar_grafo_con_flujo(fuente, sumidero, iteracion)
            if iteracion < 10:  # Evitar demasiadas iteraciones
                input("Presiona Enter para la siguiente iteración...")
            
            iteracion += 1
        
        print(f"\n¡Algoritmo terminado! Flujo máximo: {total}")
        
        # Mostrar resultado final
        self.mostrar_grafo_con_flujo(fuente, sumidero)
        
        # Mostrar corte mínimo
        self.mostrar_corte_minimo_visual(fuente)
        
        return total
    
    def mostrar_corte_minimo_visual(self, fuente):
        """Encuentra y visualiza el corte mínimo"""
        print("\n=== Calculando corte mínimo ===")
        
        # BFS en grafo residual
        visitado = [False] * self.n
        cola = [fuente]
        visitado[fuente] = True
        
        while cola:
            actual = cola.pop(0)
            for siguiente in range(self.n):
                capacidad_residual = self.capacidad[actual][siguiente] - self.flujo[actual][siguiente]
                if not visitado[siguiente] and capacidad_residual > 0:
                    visitado[siguiente] = True
                    cola.append(siguiente)
        
        conjunto_s = [i for i in range(self.n) if visitado[i]]
        conjunto_t = [i for i in range(self.n) if not visitado[i]]
        
        # Encontrar aristas del corte
        aristas_corte = []
        capacidad_corte = 0
        
        for desde in conjunto_s:
            for hacia in conjunto_t:
                if self.capacidad[desde][hacia] > 0:
                    aristas_corte.append((desde, hacia))
                    capacidad_corte += self.capacidad[desde][hacia]
        
        print(f"Conjunto S: {conjunto_s}")
        print(f"Conjunto T: {conjunto_t}")
        print(f"Aristas del corte: {aristas_corte}")
        print(f"Capacidad del corte: {capacidad_corte}")
        
        input("Presiona Enter para ver el corte mínimo...")
        self.mostrar_corte_minimo(fuente, conjunto_s, conjunto_t, aristas_corte)

# Funciones auxiliares (iguales a la versión anterior)
def generar_grafo_aleatorio(n):
    """Genera un grafo aleatorio con n nodos"""
    grafo = FlujoMaximoGrafico()
    grafo.inicializar(n)
    
    # Generar aristas aleatorias - asegurar rango válido
    min_aristas = n
    max_aristas = max(n + 2, min(15, n * (n-1) // 4))
    if max_aristas < min_aristas:
        max_aristas = min_aristas + 3
        
    num_aristas = random.randint(min_aristas, max_aristas)
    aristas_creadas = set()
    
    # Asegurar conectividad: crear un camino desde 0 hasta n-1
    for i in range(n-1):
        capacidad = random.randint(1, 10)
        grafo.agregar_arista(i, i+1, capacidad)
        aristas_creadas.add((i, i+1))
    
    # Agregar aristas adicionales aleatorias
    aristas_agregadas = n - 1
    intentos_totales = 0
    
    while aristas_agregadas < num_aristas and intentos_totales < 50:
        desde = random.randint(0, n-1)
        hacia = random.randint(0, n-1)
        
        if desde != hacia and (desde, hacia) not in aristas_creadas:
            capacidad = random.randint(1, 10)
            grafo.agregar_arista(desde, hacia, capacidad)
            aristas_creadas.add((desde, hacia))
            aristas_agregadas += 1
        
        intentos_totales += 1
    
    return grafo

def crear_grafo_manual(n):
    """Permite crear un grafo manualmente"""
    grafo = FlujoMaximoGrafico()
    grafo.inicializar(n)
    
    print(f"\nCreando grafo con {n} nodos (numerados del 0 al {n-1})")
    print("Ingresa las aristas en formato: origen destino capacidad")
    print("Ingresa -1 -1 -1 para terminar")
    
    while True:
        try:
            entrada = input("Arista: ").split()
            desde, hacia, cap = map(int, entrada)
            
            if desde == -1 and hacia == -1 and cap == -1:
                break
                
            if 0 <= desde < n and 0 <= hacia < n and desde != hacia and cap > 0:
                grafo.agregar_arista(desde, hacia, cap)
                print(f"Arista {desde} -> {hacia} con capacidad {cap} agregada")
            else:
                print("Error: verifica que los nodos estén en rango [0,n-1], sean diferentes y la capacidad > 0")
        except:
            print("Error: formato incorrecto. Use: origen destino capacidad")
    
    return grafo

def main():
    print("=== FORD-FULKERSON VISUAL ===\n")
    
    # Instalar dependencias si es necesario
    try:
        import matplotlib.pyplot as plt
        import networkx as nx
    except ImportError:
        print("Necesitas instalar las dependencias:")
        print("pip install matplotlib networkx")
        return
    
    # Solicitar número de nodos
    while True:
        try:
            n = int(input("Ingrese el número de nodos (entre 4 y 10 para mejor visualización): "))
            if 4 <= n <= 10:
                break
            else:
                print("El número debe estar entre 4 y 10 para una buena visualización")
        except:
            print("Por favor ingrese un número válido")
    
    # Opción de generación
    while True:
        opcion = input("\n¿Cómo desea crear el grafo? (1=Aleatorio, 2=Manual): ")
        if opcion == "1":
            grafo = generar_grafo_aleatorio(n)
            break
        elif opcion == "2":
            grafo = crear_grafo_manual(n)
            break
        else:
            print("Opción inválida. Ingrese 1 o 2")
    
    # Solicitar fuente y sumidero
    while True:
        try:
            fuente = int(input(f"Ingrese el nodo fuente (0 a {n-1}): "))
            if 0 <= fuente < n:
                break
            else:
                print(f"El nodo debe estar entre 0 y {n-1}")
        except:
            print("Por favor ingrese un número válido")
    
    while True:
        try:
            sumidero = int(input(f"Ingrese el nodo sumidero (0 a {n-1}): "))
            if 0 <= sumidero < n and sumidero != fuente:
                break
            elif sumidero == fuente:
                print("El sumidero debe ser diferente a la fuente")
            else:
                print(f"El nodo debe estar entre 0 y {n-1}")
        except:
            print("Por favor ingrese un número válido")
    
    # Ejecutar algoritmo visual
    flujo_maximo = grafo.ford_fulkerson_visual(fuente, sumidero)
    
    print(f"\n=== RESULTADO FINAL ===")
    print(f"Flujo máximo encontrado: {flujo_maximo}")

if __name__ == "__main__":
    main()