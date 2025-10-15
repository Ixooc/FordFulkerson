import tkinter as tk
from tkinter import ttk, messagebox
import random
import copy
from collections import deque
import matplotlib
matplotlib.use('TkAgg') 
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import networkx as nx

# --- FUNCIÓN DE LAYOUT FINAL Y DEFINITIVA ---
def layout_final_por_capas(grafo_nx, fuentes, sumideros, super_fuente=None, super_sumidero=None):
    if not grafo_nx.nodes(): return {}
    
    pos = {}
    
    # 1. Determinar los nodos de inicio para el layout
    inicios_bfs = fuentes if fuentes else [n for n, d in grafo_nx.in_degree() if d == 0]
    if not inicios_bfs and list(grafo_nx.nodes()):
        inicios_bfs = [list(grafo_nx.nodes())[0]] # Fallback
    if not inicios_bfs: return nx.spring_layout(grafo_nx) # Grafo vacío o sin nodos claros

    # 2. Calcular capas para todos los nodos alcanzables
    try:
        capas = list(nx.bfs_layers(grafo_nx, inicios_bfs))
    except Exception:
        return nx.spring_layout(grafo_nx) # Fallback si BFS falla

    for i, capa in enumerate(capas):
        y_start = (len(capa) - 1) / 2.0
        for j, nodo in enumerate(sorted(list(capa))):
            pos[nodo] = (i, y_start - j)
            
    # 3. Forzar fuentes a la capa 0 (si alguna fue movida por el BFS)
    y_start_fuentes = (len(fuentes) - 1) / 2.0
    for i, nodo in enumerate(sorted(fuentes)):
        pos[nodo] = (0, y_start_fuentes - i)

    # 4. Mover los sumideros a una nueva capa final
    max_x = max([x for x, y in pos.values()] + [0])
    y_start_sumideros = (len(sumideros) - 1) / 2.0
    for i, nodo in enumerate(sorted(list(sumideros))):
        pos[nodo] = (max_x + 1, y_start_sumideros - i)
        
    # 5. Ajustar para nodos ficticios
    if super_fuente is not None:
        # Desplazar todo el grafo a la derecha para hacer espacio
        for node in grafo_nx.nodes():
            if node != super_fuente:
                pos[node] = (pos.get(node, (0,0))[0] + 1, pos.get(node, (0,0))[1])
        pos[super_fuente] = (0, 0)

    if super_sumidero is not None:
        max_x = max([x for x, y in pos.values()] + [0])
        pos[super_sumidero] = (max_x + 1, 0)

    # 6. Manejar nodos no posicionados (inalcanzables)
    min_x = min([x for x, y in pos.values()] + [0])
    nodos_sin_posicion = [n for n in grafo_nx.nodes() if n not in pos]
    if nodos_sin_posicion:
        y_start = (len(nodos_sin_posicion) - 1) / 2.0
        for i, nodo in enumerate(sorted(nodos_sin_posicion)):
            pos[nodo] = (min_x - 1, y_start - i)
            
    return pos

# --- CLASE PRINCIPAL DE LA APLICACIÓN GUI ---
class FordFulkersonGUI:
    def __init__(self, master):
        self.master = master; self.master.title("Visualizador Interactivo de Ford-Fulkerson"); self.master.geometry("1200x800")
        self.grafo_obj = None; self.pasos, self.current_step_index = [], 0
        self.fuentes, self.sumideros, self.modo_seleccion = [], [], None
        self.crear_controles(); self.crear_lienzo_grafico(); self.dibujar_grafo()

    def crear_controles(self):
        # (Sin cambios)
        control_frame = ttk.Frame(self.master, padding="10"); control_frame.pack(side=tk.TOP, fill=tk.X)
        ttk.Label(control_frame, text="Nodos:").pack(side=tk.LEFT, padx=5)
        self.n_nodos = tk.IntVar(value=12)
        self.slider_nodos = ttk.Scale(control_frame, from_=8, to=20, orient=tk.HORIZONTAL, variable=self.n_nodos, length=150, command=lambda s: self.n_nodos.set(int(float(s)))); self.slider_nodos.pack(side=tk.LEFT, padx=5)
        ttk.Label(control_frame, textvariable=self.n_nodos).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="1. Generar Grafo", command=self.generar_grafo_aleatorio).pack(side=tk.LEFT, padx=10)
        ttk.Button(control_frame, text="2. Sel. Fuentes", command=self.activar_modo_fuente).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="3. Sel. Sumideros", command=self.activar_modo_sumidero).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="4. Ejecutar Algoritmo", command=self.ejecutar_algoritmo).pack(side=tk.LEFT, padx=10)
        self.status_label = ttk.Label(control_frame, text="Bienvenido. Genere un grafo para comenzar."); self.status_label.pack(side=tk.RIGHT, padx=10)

    def crear_lienzo_grafico(self):
        # (Sin cambios)
        self.fig, self.ax = plt.subplots(figsize=(12, 8)); plt.tight_layout()
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.master); self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        self.fig.canvas.mpl_connect('button_press_event', self.on_click)
        self.fig.canvas.mpl_connect('key_press_event', self.on_key_press)

    def generar_grafo_aleatorio(self):
        # (Sin cambios)
        self.status_label.config(text="Generando grafo..."); self.fuentes, self.sumideros, self.pasos, self.current_step_index = [], [], [], 0
        n = self.n_nodos.get(); self.grafo_obj = FlujoMaximoGrafico(); self.grafo_obj.inicializar(n)
        nodos = list(range(n)); random.shuffle(nodos)
        for i in range(n - 1):
            u, v = nodos[i], nodos[i+1]
            if random.random() > 0.5: u, v = v, u
            self.grafo_obj.agregar_arista(u, v, random.randint(10, 30))
        num_aristas_extra = int(n * 1.5)
        for _ in range(num_aristas_extra):
            u, v = random.sample(nodos, 2)
            if not any(a[0] == u and a[1] == v for a in self.grafo_obj.aristas): self.grafo_obj.agregar_arista(u, v, random.randint(5, 20))
        self.actualizar_layout_y_dibujar(); self.status_label.config(text="Grafo generado. Selecciona fuentes y sumideros.")

    def actualizar_layout_y_dibujar(self):
        if not self.grafo_obj: return
        self.grafo_obj.preparar_para_multifuente(self.fuentes, self.sumideros)
        self.grafo_obj.pos = layout_final_por_capas(self.grafo_obj.grafo_nx, self.fuentes, self.sumideros, self.grafo_obj.super_fuente, self.grafo_obj.super_sumidero)
        self.dibujar_grafo()

    def activar_modo_fuente(self): self.modo_seleccion = 'fuente'; self.status_label.config(text="MODO SELECCIÓN DE FUENTES: Haz clic en los nodos.")
    def activar_modo_sumidero(self): self.modo_seleccion = 'sumidero'; self.status_label.config(text="MODO SELECCIÓN DE SUMIDEROS: Haz clic en los nodos.")
    
    def on_click(self, event):
        # (Sin cambios)
        if not event.inaxes or not self.grafo_obj or not self.modo_seleccion or not self.grafo_obj.pos: return
        pos_vals, node_keys = list(self.grafo_obj.pos.values()), list(self.grafo_obj.pos.keys())
        if not pos_vals: return
        click_coord = (event.xdata, event.ydata)
        distances = [((c[0]-click_coord[0])**2 + (c[1]-click_coord[1])**2) for c in pos_vals]
        nodo_cercano = node_keys[distances.index(min(distances))]
        if nodo_cercano < self.grafo_obj.n:
            if self.modo_seleccion == 'fuente':
                if nodo_cercano in self.sumideros: return
                if nodo_cercano not in self.fuentes: self.fuentes.append(nodo_cercano)
                else: self.fuentes.remove(nodo_cercano)
            elif self.modo_seleccion == 'sumidero':
                if nodo_cercano in self.fuentes: return
                if nodo_cercano not in self.sumideros: self.sumideros.append(nodo_cercano)
                else: self.sumideros.remove(nodo_cercano)
            self.actualizar_layout_y_dibujar()

    def on_key_press(self, event):
        # (Sin cambios)
        if not self.pasos: return
        if event.key == 'right': self.current_step_index = min(self.current_step_index + 1, len(self.pasos) - 1)
        elif event.key == 'left': self.current_step_index = max(self.current_step_index - 1, 0)
        self.dibujar_grafo(paso_idx=self.current_step_index)
        
    def ejecutar_algoritmo(self):
        # (Sin cambios)
        if not self.fuentes or not self.sumideros: self.status_label.config(text="Error: Debes seleccionar al menos una fuente y un sumidero."); return
        self.modo_seleccion = None
        if len(self.fuentes) > 1 or len(self.sumideros) > 1: self.abrir_dialogo_capacidades()
        else: self.ejecutar_con_capacidades()

    def abrir_dialogo_capacidades(self):
        # (Sin cambios)
        self.dialog = tk.Toplevel(self.master); self.dialog.title("Verificación de Capacidades")
        frame = ttk.Frame(self.dialog, padding="20"); frame.pack(expand=True, fill="both")
        self.entry_capacidades = {}
        if len(self.fuentes) > 1:
            ttk.Label(frame, text="Capacidad de Oferta (Fuentes):", font="-weight bold").pack(pady=5, anchor='w')
            for f in self.fuentes:
                row = ttk.Frame(frame); row.pack(fill='x', pady=2); ttk.Label(row, text=f"Nodo {f}:").pack(side='left', padx=5)
                entry = ttk.Entry(row); entry.pack(side='right', expand=True, fill='x'); self.entry_capacidades[f] = entry
        if len(self.sumideros) > 1:
            ttk.Label(frame, text="Capacidad de Demanda (Sumideros):", font="-weight bold").pack(pady=(15, 5), anchor='w')
            for s in self.sumideros:
                row = ttk.Frame(frame); row.pack(fill='x', pady=2); ttk.Label(row, text=f"Nodo {s}:").pack(side='left', padx=5)
                entry = ttk.Entry(row); entry.pack(side='right', expand=True, fill='x'); self.entry_capacidades[s] = entry
        ttk.Button(frame, text="Confirmar y Ejecutar", command=self.ejecutar_con_capacidades).pack(pady=20)
        self.dialog.transient(self.master); self.dialog.grab_set(); self.master.wait_window(self.dialog)

    def ejecutar_con_capacidades(self):
        # (Sin cambios)
        cap_fuentes, cap_sumideros = {}, {}
        try:
            if hasattr(self, 'dialog') and self.dialog.winfo_exists():
                for f in self.fuentes:
                    if f in self.entry_capacidades: cap_fuentes[f] = int(self.entry_capacidades[f].get())
                for s in self.sumideros:
                    if s in self.entry_capacidades: cap_sumideros[s] = int(self.entry_capacidades[s].get())
                self.dialog.destroy()
        except ValueError: messagebox.showerror("Error de Entrada", "Por favor, ingrese solo números enteros.", parent=self.dialog); return
        self.status_label.config(text="Calculando..."); self.grafo_obj.remover_aristas_internas(self.fuentes, self.sumideros)
        self.grafo_obj.remover_aristas_de_retroceso(); self.grafo_obj.preparar_para_multifuente(self.fuentes, self.sumideros, cap_fuentes, cap_sumideros)
        self.actualizar_layout_y_dibujar(); self.pasos, flujo_maximo = self.grafo_obj.calcular_pasos_ford_fulkerson(); self.current_step_index = 0
        self.dibujar_grafo(paso_idx=0); self.status_label.config(text=f"¡Cálculo completo! Flujo Máximo: {flujo_maximo}. Usa las flechas.")
        
    def dibujar_grafo(self, paso_idx=None):
        # (La lógica de dibujo es la misma, está completa)
        self.ax.clear()
        if not self.grafo_obj or not self.grafo_obj.pos: self.ax.text(0.5, 0.5, "Genera un grafo para comenzar", ha='center', va='center'); self.ax.set_title("Visualizador Ford-Fulkerson"); self.canvas.draw(); return
        node_colors, node_sizes, labels = [], [], {}
        paso_actual = self.pasos[paso_idx] if paso_idx is not None else {}
        camino = paso_actual.get('camino', [])
        nodos_camino = {n for a in camino for n in a}
        for nodo in self.grafo_obj.grafo_nx.nodes():
            labels[nodo] = str(nodo)
            if nodo == self.grafo_obj.super_fuente: node_colors.append('gold'); node_sizes.append(1200); labels[nodo] = 'S*'
            elif nodo == self.grafo_obj.super_sumidero: node_colors.append('dimgray'); node_sizes.append(1200); labels[nodo] = 'T*'
            elif nodo in self.fuentes: node_colors.append('lightgreen'); node_sizes.append(1000)
            elif nodo in self.sumideros: node_colors.append('lightcoral'); node_sizes.append(1000)
            elif nodo in nodos_camino: node_colors.append('yellow'); node_sizes.append(800)
            else: node_colors.append('lightblue'); node_sizes.append(800)
        nx.draw_networkx_nodes(self.grafo_obj.grafo_nx, self.grafo_obj.pos, ax=self.ax, node_color=node_colors, node_size=node_sizes)
        nx.draw_networkx_labels(self.grafo_obj.grafo_nx, self.grafo_obj.pos, ax=self.ax, labels=labels, font_size=10, font_weight='bold', font_color='black')
        edge_labels, edge_colors, edge_widths = {}, [], []
        flujo = paso_actual.get('flujo', [[0]*self.grafo_obj.n for _ in range(self.grafo_obj.n)])
        for u, v in self.grafo_obj.grafo_nx.edges():
            if u == self.grafo_obj.super_fuente: edge_labels[(u,v)] = self.grafo_obj.cap_fuentes.get(v, r'$\infty$'); edge_colors.append('gray'); edge_widths.append(2)
            elif v == self.grafo_obj.super_sumidero: edge_labels[(u,v)] = self.grafo_obj.cap_sumideros.get(u, r'$\infty$'); edge_colors.append('gray'); edge_widths.append(2)
            else:
                c, f = self.grafo_obj.capacidad[u][v], flujo[u][v]
                edge_labels[(u,v)] = f"{f}/{c}"
                if (u,v) in camino: edge_colors.append('red'); edge_widths.append(4)
                elif (v,u) in camino: edge_colors.append('orange'); edge_widths.append(4)
                elif f > 0:
                    if f == c: edge_colors.append('darkred')
                    else: edge_colors.append('blue')
                    edge_widths.append(3)
                else: edge_colors.append('gray'); edge_widths.append(1)
        nx.draw_networkx_edges(self.grafo_obj.grafo_nx, self.grafo_obj.pos, ax=self.ax, edgelist=list(self.grafo_obj.grafo_nx.edges()), edge_color=edge_colors, width=edge_widths, arrows=True, arrowsize=20, node_size=node_sizes)
        nx.draw_networkx_edge_labels(self.grafo_obj.grafo_nx, self.grafo_obj.pos, edge_labels=edge_labels, ax=self.ax, font_size=9, bbox=dict(facecolor="white", alpha=0.7, edgecolor='none', pad=0.1))
        titulo = paso_actual.get('titulo', "Selecciona Fuentes (Verde) y Sumideros (Rojo)")
        self.ax.set_title(titulo, fontsize=16)
        self.canvas.draw()


# --- CLASE DE LÓGICA DEL GRAFO (SIN CAMBIOS) ---
class FlujoMaximoGrafico:
    # (El código de esta clase no cambia)
    def __init__(self): self.n = 0; self.capacidad, self.aristas = [], []; self.grafo_nx, self.pos = None, None; self.fuentes, self.sumideros, self.super_fuente, self.super_sumidero = [], [], None, None; self.cap_fuentes, self.cap_sumideros = {}, {}
    def inicializar(self, n): self.n = n; self.capacidad = [[0] * n for _ in range(n)]; self.aristas = []
    def agregar_arista(self, desde, hacia, capacidad):
        if 0 <= desde < self.n and 0 <= hacia < self.n: self.capacidad[desde][hacia] = capacidad; self.aristas.append((desde, hacia, capacidad))
    def crear_grafo_networkx(self):
        self.grafo_nx = nx.DiGraph(); self.grafo_nx.add_nodes_from(range(self.n))
        for desde, hacia, _ in self.aristas: self.grafo_nx.add_edge(desde, hacia)
    def remover_aristas_internas(self, fuentes, sumideros):
        aristas_a_eliminar = [(u, v) for u, v in list(self.grafo_nx.edges()) if (u in fuentes and v in fuentes) or (u in sumideros and v in sumideros)]
        if aristas_a_eliminar: print(f"Eliminando aristas internas: {aristas_a_eliminar}"); self.grafo_nx.remove_edges_from(aristas_a_eliminar)
        for u, v in aristas_a_eliminar:
            if u<self.n and v<self.n: self.capacidad[u][v] = 0; self.aristas = [a for a in self.aristas if a[:2] != (u,v)]
    def remover_aristas_de_retroceso(self):
        if not self.pos: return
        aristas_a_revertir = [(u, v) for u, v in list(self.grafo_nx.edges()) if self.pos.get(u, (0,))[0] >= self.pos.get(v, (0,))[0]]
        if aristas_a_revertir: print(f"Revirtiendo aristas de retroceso: {aristas_a_revertir}")
        for u, v in aristas_a_revertir:
            cap = 0
            if u < self.n and v < self.n: cap = self.capacidad[u][v]
            self.grafo_nx.remove_edge(u, v)
            if u < self.n and v < self.n: self.capacidad[u][v] = 0
            self.aristas = [a for a in self.aristas if a[:2] != (u,v)]
            if not self.grafo_nx.has_edge(v, u) and v < self.n and u < self.n:
                self.agregar_arista(v, u, cap); self.grafo_nx.add_edge(v, u)
    def preparar_para_multifuente(self, fuentes, sumideros, cap_fuentes={}, cap_sumideros={}):
        self.fuentes, self.sumideros, self.cap_fuentes, self.cap_sumideros = fuentes, sumideros, cap_fuentes, cap_sumideros
        self.super_fuente, self.super_sumidero = None, None; self.crear_grafo_networkx()
        if len(fuentes) > 1:
            self.super_fuente = self.n; self.grafo_nx.add_node(self.super_fuente)
            for f in fuentes: self.grafo_nx.add_edge(self.super_fuente, f)
        if len(sumideros) > 1:
            idx = self.n + (1 if self.super_fuente is not None else 0)
            self.super_sumidero = idx; self.grafo_nx.add_node(self.super_sumidero)
            for s in sumideros: self.grafo_nx.add_edge(s, self.super_sumidero)
    def _dfs(self, u, sumidero, padre, visitado, flujo, capacidad):
        visitado[u] = True
        if u == sumidero: return True
        n_extendido = len(capacidad)
        for v in range(n_extendido):
            if not visitado[v] and capacidad[u][v] - flujo[u][v] > 0:
                padre[v] = u
                if self._dfs(v, sumidero, padre, visitado, flujo, capacidad): return True
        for v in range(n_extendido):
            if not visitado[v] and flujo[v][u] > 0:
                padre[v] = u
                if self._dfs(v, sumidero, padre, visitado, flujo, capacidad): return True
        return False
    def calcular_pasos_ford_fulkerson(self):
        fuente_calculo = self.super_fuente if self.super_fuente is not None else (self.fuentes[0] if self.fuentes else -1)
        sumidero_calculo = self.super_sumidero if self.super_sumidero is not None else (self.sumideros[0] if self.sumideros else -1)
        if fuente_calculo == -1 or sumidero_calculo == -1: return [], 0
        n_actual = self.grafo_nx.number_of_nodes()
        cap_extendida = [[0] * n_actual for _ in range(n_actual)]
        for u, v in self.grafo_nx.edges():
            if u == self.super_fuente: cap_extendida[u][v] = self.cap_fuentes.get(v, float('inf'))
            elif v == self.super_sumidero: cap_extendida[u][v] = self.cap_sumideros.get(u, float('inf'))
            elif u < self.n and v < self.n: cap_extendida[u][v] = self.capacidad[u][v]
        flujo_extendido = [[0] * n_actual for _ in range(n_actual)]
        total, pasos, iteracion = 0, [], 1
        flujo_visible = [row[:self.n] for row in flujo_extendido[:self.n]]
        pasos.append({'tipo': 'flujo', 'titulo': 'Grafo Inicial', 'flujo': copy.deepcopy(flujo_visible), 'camino': []})
        while True:
            padre, visitado = [-1] * n_actual, [False] * n_actual
            if not self._dfs(fuente_calculo, sumidero_calculo, padre, visitado, flujo_extendido, cap_extendida): break
            minimo, nodo_actual = float('inf'), sumidero_calculo
            camino, camino_visible = [], []
            while nodo_actual != fuente_calculo:
                padre_ahora = padre[nodo_actual]
                camino.insert(0, (padre_ahora, nodo_actual))
                if padre_ahora < self.n and nodo_actual < self.n: camino_visible.insert(0, (padre_ahora, nodo_actual))
                cap_res = cap_extendida[padre_ahora][nodo_actual] - flujo_extendido[padre_ahora][nodo_actual]
                if cap_res > 0: minimo = min(minimo, cap_res)
                else: minimo = min(minimo, flujo_extendido[nodo_actual][padre_ahora])
                nodo_actual = padre_ahora
            flujo_visible = [row[:self.n] for row in flujo_extendido[:self.n]]
            pasos.append({'tipo': 'flujo', 'titulo': f'Iteración {iteracion} - Camino Encontrado', 'flujo': copy.deepcopy(flujo_visible), 'camino': camino_visible})
            for u, v in camino:
                if cap_extendida[u][v] - flujo_extendido[u][v] > 0: flujo_extendido[u][v] += minimo
                else: flujo_extendido[v][u] -= minimo
            total += minimo
            flujo_visible = [row[:self.n] for row in flujo_extendido[:self.n]]
            pasos.append({'tipo': 'flujo', 'titulo': f'Iteración {iteracion} - Flujo Aplicado (Total: {total})', 'flujo': copy.deepcopy(flujo_visible), 'camino': []})
            iteracion += 1
        pasos.append({'tipo': 'flujo', 'titulo': f'RESULTADO FINAL - Flujo Máximo: {total}', 'flujo': [row[:self.n] for row in flujo_extendido[:self.n]], 'camino': []})
        return pasos, total

# --- PUNTO DE ENTRADA DE LA APLICACIÓN ---
if __name__ == "__main__":
    root = tk.Tk()
    app = FordFulkersonGUI(root)
    root.mainloop()
