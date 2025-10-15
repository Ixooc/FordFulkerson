import tkinter as tk
from tkinter import ttk, messagebox
from tkinter.simpledialog import askinteger
import random
import copy
from collections import deque
import matplotlib
matplotlib.use('TkAgg') 
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import networkx as nx

# --- FUNCIÓN DE LAYOUT (SIN CAMBIOS) ---
def layout_final_por_zonas(grafo_nx, fuentes, sumideros, super_fuente=None, super_sumidero=None):
    if not grafo_nx.nodes(): return {}
    pos = {}
    fuentes_reales = fuentes if fuentes else [n for n, d in grafo_nx.in_degree() if d == 0] or (list(grafo_nx.nodes())[:1] if grafo_nx.nodes() else [])
    nodos_intermedios = [n for n in grafo_nx.nodes() if n not in fuentes_reales and n not in sumideros and n != super_fuente and n != super_sumidero]
    offset_x = 1 if super_fuente is not None else 0
    y_start_fuentes = (len(fuentes_reales) - 1) / 2.0
    for i, nodo in enumerate(sorted(fuentes_reales)):
        pos[nodo] = (offset_x, y_start_fuentes - i)
    max_x_intermedio = 0
    if nodos_intermedios:
        subgrafo = nx.DiGraph(grafo_nx.subgraph(nodos_intermedios))
        inicios_subgrafo = {n for n in nodos_intermedios if any(grafo_nx.has_edge(f, n) for f in fuentes_reales)}
        if not inicios_subgrafo: inicios_subgrafo = {n for n, d in subgrafo.in_degree() if d == 0}
        if not inicios_subgrafo and nodos_intermedios: inicios_subgrafo = {sorted(nodos_intermedios)[0]}
        try:
            nodos_posicionados_en_subgrafo = set()
            if inicios_subgrafo:
                capas = list(nx.bfs_layers(subgrafo, list(inicios_subgrafo)))
                for i, capa in enumerate(capas):
                    x = i + 1 + offset_x; max_x_intermedio = max(max_x_intermedio, x)
                    nodos_en_capa = [n for n in capa if n not in nodos_posicionados_en_subgrafo]
                    y_start_capa = (len(nodos_en_capa) - 1) / 2.0
                    for j, nodo in enumerate(sorted(nodos_en_capa)):
                        pos[nodo] = (x, y_start_capa - j); nodos_posicionados_en_subgrafo.add(nodo)
            nodos_restantes = [n for n in nodos_intermedios if n not in nodos_posicionados_en_subgrafo]
            if nodos_restantes:
                max_x_intermedio += 1
                y_start_restantes = (len(nodos_restantes) - 1) / 2.0
                for i, nodo in enumerate(sorted(nodos_restantes)): pos[nodo] = (max_x_intermedio, y_start_restantes - i)
        except Exception:
            max_x_intermedio = 1 + offset_x
            y_start_intermedio = (len(nodos_intermedios) - 1) / 2.0
            for i, nodo in enumerate(sorted(nodos_intermedios)): pos[nodo] = (1 + offset_x, y_start_intermedio - i)
    x_sumidero = max(max_x_intermedio, offset_x) + 1
    y_start_sumideros = (len(sumideros) - 1) / 2.0 if sumideros else 0
    for i, nodo in enumerate(sorted(sumideros)): pos[nodo] = (x_sumidero, y_start_sumideros - i)
    if super_fuente is not None: pos[super_fuente] = (0, 0)
    if super_sumidero is not None: pos[super_sumidero] = (x_sumidero + 1, 0)
    for nodo in grafo_nx.nodes():
        if nodo not in pos: pos[nodo] = (-1, 0)
    return pos

# --- CLASE PRINCIPAL DE LA APLICACIÓN GUI ---
class FordFulkersonGUI:
    def __init__(self, master):
        self.master = master; self.master.title("Visualizador Interactivo de Ford-Fulkerson"); self.master.geometry("1200x800")
        self.grafo_obj = None; self.pasos, self.current_step_index = [], 0
        self.fuentes, self.sumideros, self.modo_seleccion = [], [], None
        self.primer_nodo_arista = None
        self.crear_controles(); self.crear_lienzo_grafico(); self.dibujar_grafo()

    def crear_controles(self):
        control_frame = ttk.Frame(self.master, padding="10"); control_frame.pack(side=tk.TOP, fill=tk.X)
        creacion_frame = ttk.LabelFrame(control_frame, text="1. Creación de Grafo", padding=5); creacion_frame.pack(side=tk.LEFT, padx=10, fill='y')
        ttk.Label(creacion_frame, text="Nodos:").pack(side=tk.LEFT, padx=5)
        self.n_nodos = tk.IntVar(value=8)
        self.slider_nodos = ttk.Scale(creacion_frame, from_=8, to=16, orient=tk.HORIZONTAL, variable=self.n_nodos, length=100, command=lambda s: self.n_nodos.set(int(float(s)))); self.slider_nodos.pack(side=tk.LEFT, padx=5)
        ttk.Label(creacion_frame, textvariable=self.n_nodos).pack(side=tk.LEFT, padx=5)
        self.btn_gen_aleatorio = ttk.Button(creacion_frame, text="Generar Aleatorio", command=self.generar_grafo_aleatorio); self.btn_gen_aleatorio.pack(side=tk.LEFT, padx=(10,5), pady=2)
        self.btn_crear_manual = ttk.Button(creacion_frame, text="Crear Lienzo Manual", command=self.iniciar_modo_manual); self.btn_crear_manual.pack(side=tk.LEFT, padx=5, pady=2)
        edicion_frame = ttk.LabelFrame(control_frame, text="2. Edición Manual", padding=5); edicion_frame.pack(side=tk.LEFT, padx=10, fill='y')
        self.btn_add_arista = ttk.Button(edicion_frame, text="Añadir Arista", command=self.activar_modo_add_arista, state='disabled'); self.btn_add_arista.pack(side=tk.LEFT, padx=5, pady=2)
        self.btn_del_arista = ttk.Button(edicion_frame, text="Eliminar Arista", command=self.activar_modo_del_arista, state='disabled'); self.btn_del_arista.pack(side=tk.LEFT, padx=5, pady=2)
        algo_frame = ttk.LabelFrame(control_frame, text="3. Algoritmo", padding=5); algo_frame.pack(side=tk.LEFT, padx=10, fill='y')
        self.btn_sel_fuentes = ttk.Button(algo_frame, text="Sel. Fuentes", command=self.activar_modo_fuente, state='disabled'); self.btn_sel_fuentes.pack(side=tk.LEFT, padx=5, pady=2)
        self.btn_sel_sumideros = ttk.Button(algo_frame, text="Sel. Sumideros", command=self.activar_modo_sumidero, state='disabled'); self.btn_sel_sumideros.pack(side=tk.LEFT, padx=5, pady=2)
        self.btn_ejecutar = ttk.Button(algo_frame, text="Ejecutar", command=self.ejecutar_algoritmo, state='disabled'); self.btn_ejecutar.pack(side=tk.LEFT, padx=5, pady=2)
        self.btn_reiniciar = ttk.Button(control_frame, text="Reiniciar", command=self.reiniciar_aplicacion, state='disabled'); self.btn_reiniciar.pack(side=tk.RIGHT, padx=10)
        self.status_label = ttk.Label(control_frame, text="Bienvenido.", anchor="e"); self.status_label.pack(side=tk.RIGHT, padx=10)

    def crear_lienzo_grafico(self):
        self.fig, self.ax = plt.subplots(figsize=(12, 8)); plt.tight_layout()
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.master); self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        self.fig.canvas.mpl_connect('button_press_event', self.on_click)
        self.fig.canvas.mpl_connect('key_press_event', self.on_key_press)

    def _reset_estado(self, modo_manual=False):
        self.fuentes, self.sumideros, self.pasos, self.current_step_index = [], [], [], 0
        self.modo_seleccion, self.primer_nodo_arista = None, None
        is_ready = self.grafo_obj is not None and self.grafo_obj.n > 0
        self.btn_gen_aleatorio.config(state='normal'); self.btn_crear_manual.config(state='normal')
        self.btn_sel_fuentes.config(state='normal' if is_ready else 'disabled')
        self.btn_sel_sumideros.config(state='normal' if is_ready else 'disabled')
        self.btn_ejecutar.config(state='normal' if is_ready else 'disabled')
        self.btn_add_arista.config(state='normal' if modo_manual else 'disabled')
        self.btn_del_arista.config(state='normal' if modo_manual else 'disabled')
        self.btn_reiniciar.config(state='disabled')

    def generar_grafo_aleatorio(self):
        n = self.n_nodos.get(); self.grafo_obj = FlujoMaximoGrafico(); self.grafo_obj.inicializar(n)
        self._reset_estado()
        self.status_label.config(text="Generando grafo conectado...")
        nodos = list(range(n)); random.shuffle(nodos)
        for i in range(n - 1):
            u, v = nodos[i], nodos[i+1]
            if random.random() > 0.5: u, v = v, u
            self.grafo_obj.agregar_arista(u, v, random.randint(10, 30))
        num_aristas_extra = int(n * 1.5)
        for _ in range(num_aristas_extra):
            u, v = random.sample(nodos, 2)
            if not any(a[0] == u and a[1] == v for a in self.grafo_obj.aristas): self.grafo_obj.agregar_arista(u, v, random.randint(5, 20))
        self.grafo_obj.crear_grafo_networkx(); self.actualizar_layout_y_dibujar()
        self.btn_sel_fuentes.config(state='normal'); self.btn_sel_sumideros.config(state='normal'); self.btn_ejecutar.config(state='normal')
        self.status_label.config(text="Grafo generado. Selecciona fuentes y sumideros.")

    def iniciar_modo_manual(self):
        n = self.n_nodos.get(); self.grafo_obj = FlujoMaximoGrafico(); self.grafo_obj.inicializar(n)
        self._reset_estado(modo_manual=True)
        self.status_label.config(text="Modo Manual: Añade o elimina aristas.")
        self.grafo_obj.crear_grafo_networkx()
        self.grafo_obj.pos = nx.circular_layout(self.grafo_obj.grafo_nx)
        self.dibujar_grafo()

    def actualizar_layout_y_dibujar(self):
        if not self.grafo_obj: return
        self.grafo_obj.preparar_para_multifuente(self.fuentes, self.sumideros)
        self.grafo_obj.pos = layout_final_por_zonas(self.grafo_obj.grafo_nx, self.fuentes, self.sumideros, self.grafo_obj.super_fuente, self.grafo_obj.super_sumidero)
        self.dibujar_grafo()

    def _bloquear_edicion(self):
        self.btn_gen_aleatorio.config(state='disabled'); self.btn_crear_manual.config(state='disabled')
        self.btn_add_arista.config(state='disabled'); self.btn_del_arista.config(state='disabled')
        self.modo_seleccion = None; self.primer_nodo_arista = None

    def activar_modo_fuente(self): self._bloquear_edicion(); self.modo_seleccion = 'fuente'; self.status_label.config(text="MODO SELECCIÓN DE FUENTES: Haz clic en los nodos.")
    def activar_modo_sumidero(self): self._bloquear_edicion(); self.modo_seleccion = 'sumidero'; self.status_label.config(text="MODO SELECCIÓN DE SUMIDEROS: Haz clic en los nodos.")
    def activar_modo_add_arista(self): self.modo_seleccion = 'add_edge_1'; self.primer_nodo_arista = None; self.status_label.config(text="AÑADIR ARISTA: Haz clic en el nodo de INICIO.")
    def activar_modo_del_arista(self): self.modo_seleccion = 'del_edge_1'; self.primer_nodo_arista = None; self.status_label.config(text="ELIMINAR ARISTA: Haz clic en el nodo de INICIO.")

    def on_click(self, event):
        if not event.inaxes or not self.grafo_obj or not self.grafo_obj.pos: return
        pos_vals, node_keys = list(self.grafo_obj.pos.values()), list(self.grafo_obj.pos.keys())
        if not pos_vals: return
        click_coord = (event.xdata, event.ydata); distances = [((c[0]-click_coord[0])**2 + (c[1]-click_coord[1])**2) for c in pos_vals]
        nodo_cercano = node_keys[distances.index(min(distances))]
        if self.modo_seleccion in ['fuente', 'sumidero']:
            if nodo_cercano >= self.grafo_obj.n: return
            if self.modo_seleccion == 'fuente':
                if nodo_cercano in self.sumideros: return
                if nodo_cercano not in self.fuentes: self.fuentes.append(nodo_cercano)
                else: self.fuentes.remove(nodo_cercano)
            elif self.modo_seleccion == 'sumidero':
                if nodo_cercano in self.fuentes: return
                if nodo_cercano not in self.sumideros: self.sumideros.append(nodo_cercano)
                else: self.sumideros.remove(nodo_cercano)
            self.actualizar_layout_y_dibujar()
        elif self.modo_seleccion in ['add_edge_1', 'del_edge_1']:
            if nodo_cercano >= self.grafo_obj.n: return
            self.primer_nodo_arista = nodo_cercano
            if self.modo_seleccion == 'add_edge_1': self.modo_seleccion = 'add_edge_2'; self.status_label.config(text=f"AÑADIR ARISTA: Inicio en {nodo_cercano}. Clic en FIN.")
            else: self.modo_seleccion = 'del_edge_2'; self.status_label.config(text=f"ELIMINAR ARISTA: Inicio en {nodo_cercano}. Clic en FIN.")
        elif self.modo_seleccion in ['add_edge_2', 'del_edge_2']:
            if nodo_cercano >= self.grafo_obj.n: return
            u, v = self.primer_nodo_arista, nodo_cercano
            if u != v:
                if self.modo_seleccion == 'add_edge_2':
                    cap = askinteger("Capacidad", f"Capacidad para arista {u}->{v}:", parent=self.master, minvalue=1)
                    if cap is not None: self.grafo_obj.agregar_arista(u, v, cap); self.dibujar_grafo()
                elif self.modo_seleccion == 'del_edge_2':
                    if self.grafo_obj.grafo_nx.has_edge(u,v): self.grafo_obj.remover_arista(u,v); self.dibujar_grafo()
                    else: self.status_label.config(text=f"ERROR: No existe arista de {u} a {v}.")
            if self.modo_seleccion == 'add_edge_2': self.activar_modo_add_arista()
            else: self.activar_modo_del_arista()

    def on_key_press(self, event):
        if not self.pasos: return
        if event.key == 'right': self.current_step_index = min(self.current_step_index + 1, len(self.pasos) - 1)
        elif event.key == 'left': self.current_step_index = max(self.current_step_index - 1, 0)
        self.dibujar_grafo(paso_idx=self.current_step_index)
        
    def ejecutar_algoritmo(self):
        if not self.grafo_obj or not self.grafo_obj.grafo_nx.nodes():
            messagebox.showerror("Error", "Primero debe generar un grafo."); return

        # --- LÓGICA DE VALIDACIÓN Y RESETEO CORREGIDA ---
        if not nx.is_weakly_connected(self.grafo_obj.grafo_nx):
            messagebox.showerror("Error de Grafo", "El grafo no está conectado. Por favor, añada aristas para conectar todos los nodos.")
            self.fuentes, self.sumideros = [], []
            self._reset_estado(modo_manual=True) 
            # Recalcula el layout circular y redibuja
            self.grafo_obj.pos = nx.circular_layout(self.grafo_obj.grafo_nx)
            self.dibujar_grafo()
            self.status_label.config(text="Error: Grafo no conectado. Se reinició la selección.")
            return

        if not self.fuentes or not self.sumideros:
            messagebox.showerror("Error de Selección", "Debes seleccionar al menos una fuente y un sumidero."); return
            
        self._bloquear_edicion()
        if len(self.fuentes) > 1 or len(self.sumideros) > 1: self.abrir_dialogo_capacidades()
        else: self.ejecutar_con_capacidades()

    def abrir_dialogo_capacidades(self):
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
        cap_fuentes, cap_sumideros = {}, {}
        try:
            if hasattr(self, 'dialog') and self.dialog.winfo_exists():
                for f in self.fuentes:
                    if f in self.entry_capacidades: cap_fuentes[f] = int(self.entry_capacidades[f].get())
                for s in self.sumideros:
                    if s in self.entry_capacidades: cap_sumideros[s] = int(self.entry_capacidades[s].get())
                self.dialog.destroy()
        except ValueError: messagebox.showerror("Error de Entrada", "Por favor, ingrese solo números enteros.", parent=self.dialog); return
        self.status_label.config(text="Limpiando y calculando..."); 
        self.actualizar_layout_y_dibujar()
        self.grafo_obj.remover_aristas_internas(self.fuentes, self.sumideros)
        self.grafo_obj.remover_aristas_de_retroceso()
        self.grafo_obj.preparar_para_multifuente(self.fuentes, self.sumideros, cap_fuentes, cap_sumideros)
        self.actualizar_layout_y_dibujar()
        self.pasos, flujo_maximo = self.grafo_obj.calcular_pasos_ford_fulkerson(); self.current_step_index = 0
        self.dibujar_grafo(paso_idx=0); self.status_label.config(text=f"¡Cálculo completo! Flujo Máximo: {flujo_maximo}. Usa las flechas.")
        self.btn_reiniciar.config(state='normal')
        
    def dibujar_grafo(self, paso_idx=None):
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
        
    def reiniciar_aplicacion(self):
        self.grafo_obj = None
        self._reset_estado()
        self.status_label.config(text="Bienvenido. Genere un grafo para comenzar.")
        self.dibujar_grafo()

# --- CLASE DE LÓGICA DEL GRAFO (SIN CAMBIOS) ---
class FlujoMaximoGrafico:
    # (El código de esta clase no cambia)
    def __init__(self): self.n = 0; self.capacidad, self.aristas = [], []; self.grafo_nx, self.pos = None, None; self.fuentes, self.sumideros, self.super_fuente, self.super_sumidero = [], [], None, None; self.cap_fuentes, self.cap_sumideros = {}, {}
    def inicializar(self, n): self.n = n; self.capacidad = [[0] * n for _ in range(n)]; self.aristas = []
    def agregar_arista(self, desde, hacia, capacidad):
        if 0 <= desde < self.n and 0 <= hacia < self.n:
            self.capacidad[desde][hacia] = capacidad; self.aristas.append((desde, hacia, capacidad))
            if self.grafo_nx is not None: self.grafo_nx.add_edge(desde, hacia)
    def remover_arista(self, u, v):
        if self.grafo_nx.has_edge(u, v):
            self.grafo_nx.remove_edge(u, v)
            if u < self.n and v < self.n: self.capacidad[u][v] = 0
            self.aristas = [a for a in self.aristas if a[:2] != (u,v)]
            print(f"Arista {u}->{v} eliminada.")
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
        aristas_a_revertir = [(u, v) for u, v in list(self.grafo_nx.edges()) if u < self.n and v < self.n and self.pos.get(u, (0,))[0] >= self.pos.get(v, (0,))[0]]
        if aristas_a_revertir: print(f"Revirtiendo aristas de retroceso: {aristas_a_revertir}")
        for u, v in aristas_a_revertir:
            cap = self.capacidad[u][v]
            self.remover_arista(u, v)
            if not self.grafo_nx.has_edge(v, u): self.agregar_arista(v, u, cap)
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
