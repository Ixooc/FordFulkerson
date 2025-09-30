import random
try:
    import matplotlib.pyplot as plt
    import networkx as nx
    GRAFICOS_DISPONIBLES = True
except ImportError:
    GRAFICOS_DISPONIBLES = False
    print("Nota: Para visualización gráfica instale: pip install matplotlib networkx")

class FlujoMaximo:
    def __init__(self):
        self.n = 0  # número de nodos
        self.capacidad = []  # matriz de capacidades
        self.flujo = []  # matriz de flujo actual
        self.aristas = []  # lista de aristas para mostrar
        self.grafo_nx = None  # grafo NetworkX para visualización
        self.pos = None  # posiciones de nodos
        
    def inicializar(self, n):
        """Inicializa las matrices con n nodos"""
        self.n = n
        self.capacidad = [[0] * n for _ in range(n)]
        self.flujo = [[0] * n for _ in range(n)]
        self.aristas = []
        if GRAFICOS_DISPONIBLES:
            self.crear_grafo_networkx()
        
    def agregar_arista(self, desde, hacia, capacidad):
        """Agrega una arista al grafo"""
        self.capacidad[desde][hacia] = capacidad
        self.aristas.append((desde, hacia, capacidad))
        if GRAFICOS_DISPONIBLES and self.grafo_nx is not None:
            self.grafo_nx.add_edge(desde, hacia, capacidad=capacidad, flujo=0)
        
    def mostrar_grafo(self):
        """Muestra el grafo actual"""
        print("\n=== GRAFO DIRIGIDO ===")
        print("Nodos: 0 a", self.n-1)
        print("Aristas (origen -> destino: capacidad):")
        for desde, hacia, cap in self.aristas:
            print(f"  {desde} -> {hacia}: {cap}")
        print()
        
    def dfs(self, nodo_actual, sumidero, padre):
        """DFS para buscar camino aumentante - versión fiel al C++"""
        if nodo_actual == sumidero:
            return True  # Se llegó al sumidero
        
        for siguiente in range(self.n):
            # Solo considerar nodos con aristas existentes
            if self.capacidad[nodo_actual][siguiente] == 0:
                continue
                
            if padre[siguiente] != -1:
                continue  # Ya visitado
            
            flujo_restante = self.flujo[nodo_actual][siguiente]
            if flujo_restante != self.capacidad[nodo_actual][siguiente]:  # Hay capacidad residual
                padre[siguiente] = nodo_actual
                if self.dfs(siguiente, sumidero, padre):
                    return True  # Se encontró ruta
        
        return False
    
    def ford_fulkerson(self, fuente, sumidero):
        """Implementa Ford-Fulkerson - versión fiel al C++"""
        print(f"\n=== ALGORITMO FORD-FULKERSON ===")
        print(f"Fuente: {fuente}, Sumidero: {sumidero}\n")
        
        # Reiniciar flujo
        self.flujo = [[0] * self.n for _ in range(self.n)]
        
        total = 0
        iteracion = 1
        
        while True:
            # Inicializar padre (equivale a padre.assign(n + 1, -1) en C++)
            padre = [-1] * self.n
            
            if not self.dfs(fuente, sumidero, padre):
                break  # Ya no hay más caminos
            
            print(f"--- Iteración {iteracion} ---")
            
            # Encontrar el mínimo (cuello de botella)
            minimo = 1000000001  # Equivale al valor grande en C++
            nodo_actual = sumidero
            camino = []
            
            while nodo_actual != fuente:
                padre_ahora = padre[nodo_actual]
                camino.insert(0, (padre_ahora, nodo_actual))
                
                # Calcular capacidad residual
                nuevo = self.capacidad[padre_ahora][nodo_actual] - self.flujo[padre_ahora][nodo_actual]
                if minimo > nuevo:
                    minimo = nuevo  # Escoge al menor
                
                nodo_actual = padre_ahora  # Cambia con su padre
            
            # Mostrar el camino encontrado
            print(f"Camino encontrado: ", end="")
            for i, (a, b) in enumerate(camino):
                if i > 0:
                    print(" -> ", end="")
                print(f"{a}", end="")
            print(f" -> {camino[-1][1]}")
            print(f"Flujo del camino: {minimo}")
            
            # Se repite el proceso para actualizar flujo
            nodo_actual = sumidero
            while nodo_actual != fuente:
                padre_ahora = padre[nodo_actual]
                self.flujo[padre_ahora][nodo_actual] += minimo
                nodo_actual = padre_ahora
            
            total += minimo
            print(f"Flujo acumulado: {total}\n")
            iteracion += 1
        
        return total
    
    def mostrar_asignacion_flujo(self):
        """Muestra la asignación final de flujo en cada arista"""
        print("=== ASIGNACIÓN DE FLUJO ===")
        for desde, hacia, cap in self.aristas:
            flujo_actual = self.flujo[desde][hacia]
            print(f"Arista {desde} -> {hacia}: {flujo_actual}/{cap}")
    
    def encontrar_corte_minimo(self, fuente):
        """Encuentra el corte mínimo"""
        print("\n=== CORTE MÍNIMO ===")
        
        # Encontrar nodos alcanzables desde la fuente en el grafo residual
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
        
        # El corte son las aristas que van de nodos visitados a no visitados
        conjunto_s = [i for i in range(self.n) if visitado[i]]
        conjunto_t = [i for i in range(self.n) if not visitado[i]]
        
        print(f"Conjunto S (alcanzable desde fuente): {conjunto_s}")
        print(f"Conjunto T (no alcanzable): {conjunto_t}")
        print("Aristas del corte:")
        
        capacidad_corte = 0
        for desde in conjunto_s:
            for hacia in conjunto_t:
                if self.capacidad[desde][hacia] > 0:
                    print(f"  {desde} -> {hacia}: capacidad {self.capacidad[desde][hacia]}")
                    capacidad_corte += self.capacidad[desde][hacia]
        
        print(f"Capacidad total del corte: {capacidad_corte}")
        
        # Verificar el teorema del corte mínimo-flujo máximo
        return capacidad_corte
    
    def verificar_teorema_corte_minimo(self, fuente, flujo_maximo):
        """Verifica que el flujo máximo = capacidad del corte mínimo"""
        print("\n=== VERIFICACIÓN DEL TEOREMA ===")
        capacidad_corte = self.encontrar_corte_minimo(fuente)
        
        print(f"\nFlujo máximo encontrado: {flujo_maximo}")
        print(f"Capacidad del corte mínimo: {capacidad_corte}")
        
        if flujo_maximo == capacidad_corte:
            print("✅ VERIFICADO: Flujo máximo = Capacidad del corte mínimo")
            print("   El teorema del corte mínimo-flujo máximo se cumple!")
        else:
            print("❌ ERROR: Los valores no coinciden. Revisar implementación.")
        
        return flujo_maximo == capacidad_corte
    
    # ==============================
    # MÉTODOS DE VISUALIZACIÓN GRÁFICA
    # ==============================
    
    def crear_grafo_networkx(self):
        """Crea el grafo NetworkX para visualización"""
        if not GRAFICOS_DISPONIBLES:
            return
        self.grafo_nx = nx.DiGraph()
        self.grafo_nx.add_nodes_from(range(self.n))
        # Posicionar nodos en círculo para mejor visualización
        self.pos = nx.circular_layout(self.grafo_nx)
    
    def mostrar_grafo_visual(self, titulo="GRAFO DIRIGIDO", resaltar_camino=None, 
                            fuente=None, sumidero=None, mostrar_flujo=False):
        """Muestra el grafo de forma visual usando matplotlib"""
        if not GRAFICOS_DISPONIBLES:
            print("Visualización gráfica no disponible. Instale: pip install matplotlib networkx")
            return
            
        plt.figure(figsize=(12, 8))
        plt.title(titulo, fontsize=16, fontweight='bold')
        
        # Colores de nodos
        node_colors = []
        for i in range(self.n):
            if i == fuente:
                node_colors.append('lightgreen')  # Fuente
            elif i == sumidero:
                node_colors.append('lightcoral')  # Sumidero
            elif resaltar_camino and i in [arista[0] for arista in resaltar_camino] + [arista[1] for arista in resaltar_camino]:
                node_colors.append('yellow')  # Nodos del camino
            else:
                node_colors.append('lightblue')  # Nodos normales
        
        # Dibujar nodos
        nx.draw_networkx_nodes(self.grafo_nx, self.pos, 
                              node_color=node_colors, 
                              node_size=800, 
                              alpha=0.9)
        
        # Etiquetas de nodos
        nx.draw_networkx_labels(self.grafo_nx, self.pos, 
                               font_size=12, 
                               font_weight='bold')
        
        # Colores y anchos de aristas
        edge_colors = []
        edge_widths = []
        
        for desde, hacia, cap in self.aristas:
            flujo_actual = self.flujo[desde][hacia] if mostrar_flujo else 0
            
            # Si está en el camino resaltado
            if resaltar_camino and (desde, hacia) in resaltar_camino:
                edge_colors.append('red')
                edge_widths.append(4)
            # Si tiene flujo
            elif mostrar_flujo and flujo_actual > 0:
                if flujo_actual == cap:
                    edge_colors.append('darkred')  # Saturada
                else:
                    edge_colors.append('blue')  # Con flujo
                edge_widths.append(3)
            else:
                edge_colors.append('gray')  # Sin flujo o modo inicial
                edge_widths.append(2)
        
        # Dibujar aristas
        edges = [(desde, hacia) for desde, hacia, _ in self.aristas]
        nx.draw_networkx_edges(self.grafo_nx, self.pos, 
                              edgelist=edges,
                              edge_color=edge_colors, 
                              width=edge_widths,
                              arrows=True, 
                              arrowsize=20)
        
        # Etiquetas de aristas
        edge_labels = {}
        for desde, hacia, cap in self.aristas:
            if mostrar_flujo:
                flujo_actual = self.flujo[desde][hacia]
                edge_labels[(desde, hacia)] = f"{flujo_actual}/{cap}"
            else:
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
    
    def ford_fulkerson_visual(self, fuente, sumidero):
        """Ford-Fulkerson con visualización paso a paso"""
        if not GRAFICOS_DISPONIBLES:
            print("Ejecutando versión texto del algoritmo...")
            return self.ford_fulkerson(fuente, sumidero)
        
        print(f"\n=== FORD-FULKERSON VISUAL ===")
        print(f"Fuente: {fuente}, Sumidero: {sumidero}")
        print("Cerrando las ventanas gráficas avanzarás al siguiente paso...")
        
        # Mostrar grafo inicial
        self.mostrar_grafo_visual("GRAFO INICIAL - Capacidades", 
                                 fuente=fuente, sumidero=sumidero)
        
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
            
            # Mostrar camino resaltado
            self.mostrar_grafo_visual(f"Iteración {iteracion} - Camino Encontrado", 
                                     resaltar_camino=camino, fuente=fuente, sumidero=sumidero, 
                                     mostrar_flujo=True)
            
            # Actualizar flujo
            nodo_actual = sumidero
            while nodo_actual != fuente:
                padre_ahora = padre[nodo_actual]
                self.flujo[padre_ahora][nodo_actual] += minimo
                nodo_actual = padre_ahora
            
            total += minimo
            print(f"Flujo acumulado: {total}")
            
            # Mostrar estado después de aplicar flujo
            self.mostrar_grafo_visual(f"Iteración {iteracion} - Después de Aplicar Flujo", 
                                     fuente=fuente, sumidero=sumidero, mostrar_flujo=True)
            
            iteracion += 1
        
        print(f"\n¡Algoritmo terminado! Flujo máximo: {total}")
        
        # Mostrar resultado final
        self.mostrar_grafo_visual("RESULTADO FINAL - Flujo Máximo", 
                                 fuente=fuente, sumidero=sumidero, mostrar_flujo=True)
        
        return total

def generar_grafo_aleatorio(n):
    """Genera un grafo aleatorio con n nodos"""
    grafo = FlujoMaximo()
    grafo.inicializar(n)
    
    # Generar aristas aleatorias - asegurar rango válido
    min_aristas = n
    max_aristas = max(n + 3, min(20, n * (n-1) // 3))
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
    
    while aristas_agregadas < num_aristas and intentos_totales < 100:
        desde = random.randint(0, n-1)
        hacia = random.randint(0, n-1)
        
        if desde != hacia and (desde, hacia) not in aristas_creadas:
            capacidad = random.randint(1, 15)
            grafo.agregar_arista(desde, hacia, capacidad)
            aristas_creadas.add((desde, hacia))
            aristas_agregadas += 1
        
        intentos_totales += 1
    
    return grafo

def crear_grafo_manual(n):
    """Permite crear un grafo manualmente"""
    grafo = FlujoMaximo()
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
    print("=== PROBLEMA DEL FLUJO MÁXIMO ===\n")
    
    # Solicitar número de nodos
    while True:
        try:
            n = int(input("Ingrese el número de nodos (entre 8 y 16): "))
            if 8 <= n <= 16:
                break
            else:
                print("El número debe estar entre 8 y 16")
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
    
    # Mostrar el grafo
    grafo.mostrar_grafo()
    
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
    
    # Opción de visualización
    if GRAFICOS_DISPONIBLES:
        while True:
            modo = input("\n¿Cómo desea ejecutar el algoritmo? (1=Texto, 2=Visual): ")
            if modo == "1":
                flujo_maximo = grafo.ford_fulkerson(fuente, sumidero)
                break
            elif modo == "2":
                flujo_maximo = grafo.ford_fulkerson_visual(fuente, sumidero)
                break
            else:
                print("Opción inválida. Ingrese 1 o 2")
    else:
        # Solo modo texto disponible
        flujo_maximo = grafo.ford_fulkerson(fuente, sumidero)
    
    print(f"\n=== RESULTADOS ===")
    print(f"Flujo máximo encontrado: {flujo_maximo}")
    
    grafo.mostrar_asignacion_flujo()
    
    # Verificar el teorema del corte mínimo-flujo máximo
    grafo.verificar_teorema_corte_minimo(fuente, flujo_maximo)
    
    # Mostrar grafo final si está disponible
    if GRAFICOS_DISPONIBLES:
        mostrar_final = input("\n¿Desea ver el grafo final? (s/n): ").lower()
        if mostrar_final == 's':
            grafo.mostrar_grafo_visual("GRAFO FINAL CON FLUJO MÁXIMO", 
                                      fuente=fuente, sumidero=sumidero, mostrar_flujo=True)

if __name__ == "__main__":
    main()
