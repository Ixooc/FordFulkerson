# Archivo encargado de la interfaz para el usuario (Graphical User Interface)
import tkinter as tk
from tkinter import messagebox, filedialog
from tkinter.simpledialog import askinteger
import customtkinter as ctk  # Importamos customtkinter
import random
import matplotlib
matplotlib.use('TkAgg') 
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import networkx as nx
import math
from PIL import Image
import io
import base64

# Importaciones de nuestros módulos locales
from logic import FlujoMaximoGrafico
from layout import layout_final_por_zonas


class FordFulkersonGUI:
    # Clase principal para la interfaz gráfica
    def __init__(self, master):
        self.master = master
        self.master.title("Aplicación del teorema de Flujo Máximo - Ford Fulkerson")
        self.master.geometry("1200x950")
        
        self.grafo_obj = None                 
        self.pasos, self.current_step_index = [], 0 
        self.fuentes, self.sumideros = [], [] 
        
        self.modo_seleccion = None            
        self.primer_nodo_arista = None        

        # --- Ícono de Reinicio ---
        RESET_ICON_BASE64 = "R0lGODlhEAAQAPcAAHx+f4SFhnp+f4uNjpucnOnp6e3t7fT09I2QkJicnNPT0+rq6vHx8fLy8vX19fDw8Pb29vj4+ISEhI6OjpSUlJycnKWlpbe3t7+/v8HBwcjIyM/Pz9fX19ra2t/f3+np6erq6u7u7vLy8vX19ff39/j4+Pn5+f39/f///wAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACH5BAEAAIAALAAAAAAQABAAAAjUACEJHEiwoMGDCBMqXMiwocOHECNKnEixosWLGDNq3Mixo8ePIEOKHEmypMmTKFOqXMmypcuXMGPKnEmzps2bOHPq3Mmzp8+fQIMKHUq0qNGjSJMqXcq0qtWrWLNq3cq0q9evYMOKHUu2rNmzaNOqXcu2rdu3cOPKnUu3rt27ePPq3cu3r9+/gAMLHky4sOHDiBMrXsy4sePHkCNLnky5suXLmDNr3sy5s+fPoEOLHk26tOnTqFOrXs26tevXsGPLnk27tu3buHPr3s27t+/fwIMLH068uPHjyJMrX868ufPn0KNLn069uvXr2LNr3869u/fv4MOLH0++vPnz6NOrX8++vfv38OPLn0+/vv37+PPr38+/v///wAYo5IAE9kBACH5BAEAAIAALAAAAAAQABAAAAjdAB5IsKDBgwgTKlzIsKHDhxAjSpxIsaLFixgzatzIsaPHjyBDihxJsqTJkyhTqlzJsqXLlzBjypxJs6bNmzhz6tzJs6fPn0CDCh1KidQBAQAh+QQBAACAAAAsAAAAABAAEAAACP0AECRIsKDBgwgTKlzIsKHDhxAjSpxIsaLFixgzatzIsaPHjyBDihxJsqTJkyhTqlzJsqXLlzBjypxJs6bNmzhz6tzJs6fPn0CDCh1KtKjRo0iTKl3KtKnVq1izat3KtavXr2DDih1LtqzZs2jTql3Ltq3bt3Djyp1Lt67du3jz6t3Lt6/fv4ADCx5MuLDhw4gTK17MuLHjx5AjS55MubLly5gza97MubPnz6BDix5NurTp06hTq17NurXr17Bjy55Nu7bt27hz697Nu7fv38CDCx9OvLjx48iTK1/OvLnz59CjS59Ovbr169iza9/Ovbv37+DDix9Pvrz58+jTq1/Pvr379/Djy59Pvz78AADs="
        image_data = base64.b64decode(RESET_ICON_BASE64)
        pil_image = Image.open(io.BytesIO(image_data))
        
        # Crea una CTkImage (esto elimina el UserWarning)
        self.reset_icon_image = ctk.CTkImage(light_image=pil_image, dark_image=pil_image, size=(16, 16))
        
        self.crear_layout_principal()
    
    def crear_layout_principal(self):
        # Información superior
        # Usamos CTkFrame en lugar de ttk.Frame
        info_frame = ctk.CTkFrame(self.master, fg_color="transparent")
        info_frame.pack(side=tk.TOP, fill=tk.X, padx=20, pady=(10, 5))
        
        titulo_label = ctk.CTkLabel(info_frame, text="Diseño incremental de Redes Logísticas", font=ctk.CTkFont(size=20, weight="bold"))
        titulo_label.pack()
        
        descripcion_text = (
            "El diseño incremental de redes es un método de planificación donde una red crece en períodos, "
            "agregando arcos o aumentando capacidades. El objetivo es maximizar el flujo total acumulado, "
            "determinando qué mejoras implementar primero. Un caso concreto es la expansión de redes "
            "logísticas de paquetería, donde se debe decidir qué enlaces reforzar para maximizar el flujo de "
            "paquetes en cada etapa, considerando limitaciones de presupuesto e infraestructura. Esto requiere "
            "modelar la red como un grafo y aplicar algoritmos de máximo flujo en cada período."
        )
        descripcion_label = ctk.CTkLabel(info_frame, text=descripcion_text, wraplength=1100, justify="center")
        descripcion_label.pack(pady=(5, 10))

        # Marco principal de simulación
        # Usamos CTkFrame. 'fg_color="transparent"' lo hace ver como un LabelFrame
        simulacion_frame = ctk.CTkFrame(self.master) 
        simulacion_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=20, pady=(5, 20))
        
        # Etiqueta para el título del marco
        simulacion_titulo = ctk.CTkLabel(simulacion_frame, text="Simulación", font=ctk.CTkFont(size=14, weight="bold"))
        simulacion_titulo.pack(side=tk.TOP, fill=tk.X, padx=10, pady=(5,0), anchor="w")

        self.crear_controles(simulacion_frame)
        self.crear_lienzo_grafico(simulacion_frame)
        self.dibujar_grafo()

    def crear_controles(self, parent):
        # Botones de control
        control_frame = ctk.CTkFrame(parent, fg_color="transparent")
        control_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=5)
        
        # --- Grupo 1: Creación ---
        creacion_frame = ctk.CTkFrame(control_frame)
        creacion_frame.pack(side=tk.LEFT, padx=(0, 10), fill='y')
        
        ctk.CTkLabel(creacion_frame, text="1. Creación de Grafo", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=10, pady=(5,5))

        creacion_grid = ctk.CTkFrame(creacion_frame, fg_color="transparent")
        creacion_grid.pack(fill="x", padx=10, pady=(0,10))

        ctk.CTkLabel(creacion_grid, text="Nodos:").grid(row=0, column=0, padx=5)
        self.n_nodos = tk.IntVar(value=8)
        
        # CTkSlider reemplaza a ttk.Scale
        self.slider_nodos = ctk.CTkSlider(creacion_grid, from_=8, to=16, variable=self.n_nodos, number_of_steps=8, command=lambda s: self.n_nodos.set(int(s)))
        self.slider_nodos.grid(row=0, column=1, padx=5)
        ctk.CTkLabel(creacion_grid, textvariable=self.n_nodos).grid(row=0, column=2, padx=5)
        
        self.btn_gen_aleatorio = ctk.CTkButton(creacion_grid, text="Generar Aleatorio", command=self.generar_grafo_aleatorio)
        self.btn_gen_aleatorio.grid(row=1, column=0, padx=5, pady=5)
        self.btn_crear_manual = ctk.CTkButton(creacion_grid, text="Crear Lienzo Manual", command=self.iniciar_modo_manual)
        self.btn_crear_manual.grid(row=1, column=1, padx=5, pady=5)
        self.btn_cargar_archivo = ctk.CTkButton(creacion_grid, text="Cargar Archivo...", command=self.cargar_desde_archivo)
        self.btn_cargar_archivo.grid(row=1, column=2, padx=5, pady=5)
        
        # --- Grupo 2: Edición ---
        edicion_frame = ctk.CTkFrame(control_frame)
        edicion_frame.pack(side=tk.LEFT, padx=10, fill='y')
        
        ctk.CTkLabel(edicion_frame, text="2. Edición Manual", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=10, pady=(5,5))
        
        edicion_grid = ctk.CTkFrame(edicion_frame, fg_color="transparent")
        edicion_grid.pack(fill="x", padx=10, pady=(0,10))
        
        self.btn_add_arista = ctk.CTkButton(edicion_grid, text="Añadir Arista", command=self.activar_modo_add_arista, state='disabled')
        self.btn_add_arista.pack(side=tk.LEFT, padx=5, pady=5)
        self.btn_del_arista = ctk.CTkButton(edicion_grid, text="Eliminar Arista", command=self.activar_modo_del_arista, state='disabled')
        self.btn_del_arista.pack(side=tk.LEFT, padx=5, pady=5)
        
        # --- Grupo 3: Algoritmo ---
        algo_frame = ctk.CTkFrame(control_frame)
        algo_frame.pack(side=tk.LEFT, padx=10, fill='y')

        ctk.CTkLabel(algo_frame, text="3. Algoritmo", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=10, pady=(5,5))

        algo_grid = ctk.CTkFrame(algo_frame, fg_color="transparent")
        algo_grid.pack(fill="x", padx=10, pady=(0,10))
        
        self.btn_sel_fuentes = ctk.CTkButton(algo_grid, text="Sel. Fuentes", command=self.activar_modo_fuente, state='disabled')
        self.btn_sel_fuentes.pack(side=tk.LEFT, padx=5, pady=5)
        self.btn_sel_sumideros = ctk.CTkButton(algo_grid, text="Sel. Sumideros", command=self.activar_modo_sumidero, state='disabled')
        self.btn_sel_sumideros.pack(side=tk.LEFT, padx=5, pady=5)
        self.btn_ejecutar = ctk.CTkButton(algo_grid, text="Ejecutar", command=self.ejecutar_algoritmo, state='disabled', fg_color="green", hover_color="darkgreen")
        self.btn_ejecutar.pack(side=tk.LEFT, padx=5, pady=5)
        
        # --- Reinicio y Status (a la derecha) ---
        status_frame = ctk.CTkFrame(control_frame, fg_color="transparent")
        status_frame.pack(side=tk.RIGHT, padx=(10, 0), fill='y')

        self.btn_reiniciar = ctk.CTkButton(status_frame, image=self.reset_icon_image, text="", command=self.reiniciar_aplicacion, state='disabled', width=40)
        self.btn_reiniciar.pack(side=tk.RIGHT, padx=5, pady=10)
        
        self.status_label = ctk.CTkLabel(status_frame, text="Bienvenido.", anchor="e")
        self.status_label.pack(side=tk.RIGHT, padx=10, pady=10)


    def crear_lienzo_grafico(self, parent):
        # matplotlib para gráfico
        self.fig, self.ax = plt.subplots(figsize=(12, 8))
        self.fig.subplots_adjust(top=0.95, bottom=0.02, left=0.02, right=0.98) 
        
        appearance_mode = ctk.get_appearance_mode()
        if appearance_mode == "Dark":
            bg_color = "#242424" # Color oscuro estándar de CTk
        else: # "Light"
            bg_color = "#EBEBEB" # Color claro estándar de CTk

        self.fig.patch.set_facecolor(bg_color)
        self.ax.set_facecolor(bg_color)
        
        self.canvas = FigureCanvasTkAgg(self.fig, master=parent)
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True, pady=(10, 10), padx=10)
        
        self.fig.canvas.mpl_connect('button_press_event', self.on_click)
        self.fig.canvas.mpl_connect('key_press_event', self.on_key_press)
    
    # Estado y grafo
    def _reset_estado(self, modo_manual=False):
        # Visibilidad y selección de botones
        self.fuentes, self.sumideros, self.pasos, self.current_step_index = [], [], [], 0
        self.modo_seleccion, self.primer_nodo_arista = None, None
        
        is_ready = self.grafo_obj is not None and self.grafo_obj.n > 0
        
        self.btn_gen_aleatorio.configure(state='normal')
        self.btn_crear_manual.configure(state='normal')
        self.btn_cargar_archivo.configure(state='normal')
        
        self.btn_sel_fuentes.configure(state='normal' if is_ready else 'disabled')
        self.btn_sel_sumideros.configure(state='normal' if is_ready else 'disabled')
        self.btn_ejecutar.configure(state='normal' if is_ready else 'disabled')
        
        self.btn_add_arista.configure(state='normal' if modo_manual else 'disabled')
        self.btn_del_arista.configure(state='normal' if modo_manual else 'disabled')
        
        self.btn_reiniciar.configure(state='disabled')

    def generar_grafo_aleatorio(self):
        """Genera un Grafo Acíclico Dirigido (DAG) aleatorio, asegurando conectividad."""
        self.slider_nodos.configure(from_=8, to=16)
        if not (8 <= self.n_nodos.get() <= 16):
            self.n_nodos.set(8)
            
        n = self.n_nodos.get()
        self.grafo_obj = FlujoMaximoGrafico()
        self.grafo_obj.inicializar(n)
        self._reset_estado()
        
        self.status_label.configure(text="Generando grafo DAG...")
        
        # 1. Crear un orden topológico aleatorio para los nodos.
        # Esto es la clave para garantizar que sea un DAG.
        nodos_ordenados = list(range(n))
        random.shuffle(nodos_ordenados)
        
        # 2. Asegurar conectividad básica creando un camino a través del orden topológico.
        # Esto garantiza que el grafo no esté desconectado.
        for i in range(n - 1):
            u, v = nodos_ordenados[i], nodos_ordenados[i+1]
            self.grafo_obj.agregar_arista(u, v, random.randint(10, 30))
            
        # 3. Añade aristas extra aleatorias respetando el orden topológico.
        # Una arista (u, v) solo se crea si u aparece antes que v en nodos_ordenados.
        num_aristas_extra = int(n * 1.5)
        pos_nodos = {nodo: i for i, nodo in enumerate(nodos_ordenados)} # Para búsquedas rápidas

        for _ in range(num_aristas_extra):
            u, v = random.sample(range(n), 2)
            
            # Solo añadir arista si va "hacia adelante" en el orden y no existe ya.
            if pos_nodos[u] < pos_nodos[v] and not any(a[0] == u and a[1] == v for a in self.grafo_obj.aristas): 
                self.grafo_obj.agregar_arista(u, v, random.randint(5, 20))
                
        self.grafo_obj.crear_grafo_networkx()
        self.actualizar_layout_y_dibujar()
        
        self.status_label.configure(text="Grafo DAG generado. Selecciona fuentes y sumideros.")

    def validar_y_corregir_direccion_flujo(self):
        """
        Antes de ejecutar, revisa las aristas de fuentes/sumideros.
        - Invierte aristas que entran a una fuente.
        - Invierte aristas que salen de un sumidero.
        Esto se hace para cumplir la lógica de flujo.
        """
        if not self.grafo_obj: return

        aristas_a_revisar = list(self.grafo_obj.grafo_nx.edges())
        aristas_invertidas = 0
        n_original = self.grafo_obj.n

        for u, v in aristas_a_revisar:
            if u >= n_original or v >= n_original:
                continue

            capacidad = self.grafo_obj.capacidad[u][v]

            # Caso 1: Arista entrando a una fuente (debe salir)
            if v in self.fuentes and u not in self.fuentes:
                self.grafo_obj.remover_arista(u, v)
                self.grafo_obj.agregar_arista(v, u, capacidad)
                aristas_invertidas += 1

            # Caso 2: Arista saliendo de un sumidero (debe entrar)
            if u in self.sumideros and v not in self.sumideros:
                self.grafo_obj.remover_arista(u, v)
                self.grafo_obj.agregar_arista(v, u, capacidad)
                aristas_invertidas += 1
        
        if aristas_invertidas > 0:
            messagebox.showinfo(
                "Ajuste Automático",
                f"Se invirtieron {aristas_invertidas} arista(s) para asegurar la dirección correcta del flujo desde las fuentes hacia los sumideros."
            )

    def iniciar_modo_manual(self):
        # Lienzo vacío para modo manual
        self.slider_nodos.configure(from_=8, to=16)
        if not (8 <= self.n_nodos.get() <= 16):
            self.n_nodos.set(8)
            
        n = self.n_nodos.get()
        self.grafo_obj = FlujoMaximoGrafico()
        self.grafo_obj.inicializar(n)
        self._reset_estado(modo_manual=True)
        
        self.status_label.configure(text="Modo Manual: Añade o elimina aristas.")
        self.grafo_obj.crear_grafo_networkx()
        self.grafo_obj.pos = nx.circular_layout(self.grafo_obj.grafo_nx) # Layout inicial
        self.dibujar_grafo()

    def cargar_desde_archivo(self):
        # Abre el diálogo de archivo para buscar uno
        filepath = filedialog.askopenfilename(title="Seleccionar archivo de grafo", filetypes=[("Archivos de Texto", "*.txt"), ("Todos los archivos", "*.*")])
        if not filepath: 
            return

        # Validación
        try:
            with open(filepath, 'r') as f:
                primera_linea = f.readline()
                if not primera_linea:
                    messagebox.showerror("Error de Archivo", "El archivo está vacío.")
                    return
                n, m = map(int, primera_linea.strip().split())
            
            if not (8 <= n <= 16):
                messagebox.showerror("Error de Rango de Nodos", f"El número de nodos debe estar entre 8 y 16.\n\nEl archivo seleccionado tiene {n} nodos.")
                return
        except Exception as e:
            messagebox.showerror("Error de Formato", f"No se pudo leer el número de nodos del archivo.\n\nError: {e}")
            return

        #Carga, reinicio de estado y dibujo
        try:
            self.slider_nodos.configure(from_=8, to=16)
            self.grafo_obj = FlujoMaximoGrafico()
            self.grafo_obj.cargar_desde_archivo(filepath)
            self._reset_estado()
            self.n_nodos.set(self.grafo_obj.n)
            
            self.grafo_obj.crear_grafo_networkx()
            self.actualizar_layout_y_dibujar()
            
            self.btn_sel_fuentes.configure(state='normal')
            self.btn_sel_sumideros.configure(state='normal')
            self.btn_ejecutar.configure(state='normal')
            self.status_label.configure(text=f"Grafo cargado desde {filepath.split('/')[-1]}.")
        except Exception as e:
            messagebox.showerror("Error de Procesamiento", f"No se pudo procesar el archivo de grafo:\n{e}")
            self.reiniciar_aplicacion()

    def actualizar_layout_y_dibujar(self):
        # Actualiza el grafo NetworkX para reflejar Super Nodos y recalcula el layout
        if not self.grafo_obj: return
        
        # Obtiene capacidades o usa diccionarios vacíos
        cap_f = getattr(self.grafo_obj, 'cap_fuentes', {}) or {}
        cap_s = getattr(self.grafo_obj, 'cap_sumideros', {}) or {}
        
        # Prepara el grafo (crea Super Nodos si aplica)
        self.grafo_obj.preparar_para_multifuente(self.fuentes, self.sumideros, cap_f, cap_s)
        
        # Recalcula el layout personalizado
        self.grafo_obj.pos = layout_final_por_zonas(
            self.grafo_obj.grafo_nx, 
            self.fuentes, 
            self.sumideros, 
            self.grafo_obj.super_fuente, 
            self.grafo_obj.super_sumidero
        )
        self.dibujar_grafo()

    def _bloquear_edicion(self):
        """Deshabilita los botones de creación y edición para iniciar un modo de selección o ejecución."""
        self.btn_gen_aleatorio.configure(state='disabled')
        self.btn_crear_manual.configure(state='disabled')
        self.btn_add_arista.configure(state='disabled')
        self.btn_del_arista.configure(state='disabled')
        self.btn_cargar_archivo.configure(state='disabled')

        self.modo_seleccion = None
        self.primer_nodo_arista = None

    # Modos
    def activar_modo_fuente(self): 
        # Modo de selección de Fuentes (clic)
        self._bloquear_edicion()
        self.modo_seleccion = 'fuente'
        self.status_label.configure(text="MODO SELECCIÓN DE FUENTES: Haz clic en los nodos.")
        
    def activar_modo_sumidero(self): 
        # Modo de selección de Sumideros (clic)
        self._bloquear_edicion()
        self.modo_seleccion = 'sumidero'
        self.status_label.configure(text="MODO SELECCIÓN DE SUMIDEROS: Haz clic en los nodos.")
        
    def activar_modo_add_arista(self): 
        # Añade arista
        self.modo_seleccion = 'add_edge_1'
        self.primer_nodo_arista = None
        self.status_label.configure(text="AÑADIR ARISTA: Haz clic en el nodo de INICIO.")
        
    def activar_modo_del_arista(self): 
        # Elimna arista
        self.modo_seleccion = 'del_edge_1'
        self.primer_nodo_arista = None
        self.status_label.configure(text="ELIMINAR ARISTA: Haz clic en el nodo de INICIO.")

    # Manejadores de Eventos ---
    def on_click(self, event):
        # Maneja los clics en el lienzo gráfico para selección o edición
        if not event.inaxes or not self.grafo_obj or not self.grafo_obj.pos: 
            return
            
        pos_vals = list(self.grafo_obj.pos.values())
        node_keys = list(self.grafo_obj.pos.keys())
        if not pos_vals: 
            return
            
        # Encuentra el nodo más cercano
        click_coord = (event.xdata, event.ydata)
        distances = [((c[0]-click_coord[0])**2 + (c[1]-click_coord[1])**2) for c in pos_vals]
        nodo_cercano = node_keys[distances.index(min(distances))]
        
        # Lógica de selección de Fuentes/Sumideros
        if self.modo_seleccion in ['fuente', 'sumidero']:
            if nodo_cercano >= self.grafo_obj.n: return # Ignora Super Nodos
            
            if self.modo_seleccion == 'fuente':
                if nodo_cercano in self.sumideros: return
                if nodo_cercano not in self.fuentes: self.fuentes.append(nodo_cercano)
                else: self.fuentes.remove(nodo_cercano)
            elif self.modo_seleccion == 'sumidero':
                if nodo_cercano in self.fuentes: return
                if nodo_cercano not in self.sumideros: self.sumideros.append(nodo_cercano)
                else: self.sumideros.remove(nodo_cercano)
                
            self.actualizar_layout_y_dibujar()
            
        # Lógica de edición - Seleccionar inicio
        elif self.modo_seleccion in ['add_edge_1', 'del_edge_1']:
            if nodo_cercano >= self.grafo_obj.n: return
            self.primer_nodo_arista = nodo_cercano
            
            if self.modo_seleccion == 'add_edge_1': 
                self.modo_seleccion = 'add_edge_2'
                self.status_label.configure(text=f"AÑADIR ARISTA: Inicio en {nodo_cercano}. Clic en FIN.")
            else: 
                self.modo_seleccion = 'del_edge_2'
                self.status_label.configure(text=f"ELIMINAR ARISTA: Inicio en {nodo_cercano}. Clic en FIN.")
                
        # Lógica de edición - Seleccional final y ejecutar
        elif self.modo_seleccion in ['add_edge_2', 'del_edge_2']:
            if nodo_cercano >= self.grafo_obj.n: return
            u, v = self.primer_nodo_arista, nodo_cercano
            
            if u != v: # Evita lazos
                if self.modo_seleccion == 'add_edge_2':
                    cap = askinteger("Capacidad", f"Capacidad para arista {u}->{v}:", parent=self.master, minvalue=1)
                    if cap is not None: 
                        self.grafo_obj.agregar_arista(u, v, cap)
                        self.dibujar_grafo()
                elif self.modo_seleccion == 'del_edge_2':
                    if self.grafo_obj.grafo_nx.has_edge(u,v): 
                        self.grafo_obj.remover_arista(u,v)
                        self.dibujar_grafo()
                    else: 
                        self.status_label.configure(text=f"ERROR: No existe arista de {u} a {v}.")
                        
            # Vuelve al inicio del modo de edición
            if self.modo_seleccion == 'add_edge_2': 
                self.activar_modo_add_arista()
            else: 
                self.activar_modo_del_arista()

    def on_key_press(self, event):
        # Teclas de flecha (izquierda/derecha) para navegar por los pasos del algoritmo
        if not self.pasos: 
            return
            
        if event.key == 'right': 
            self.current_step_index = min(self.current_step_index + 1, len(self.pasos) - 1)
        elif event.key == 'left': 
            self.current_step_index = max(self.current_step_index - 1, 0)
            
        self.dibujar_grafo(paso_idx=self.current_step_index)

    # Métodos de Ejecución del Algoritmo
    def ejecutar_algoritmo(self):
        # Validaciones de pre-ejecución
        if not self.grafo_obj or not self.grafo_obj.grafo_nx.nodes(): 
            messagebox.showerror("Error", "Primero debe generar un grafo.")
            return
        if self.grafo_obj.n > 0 and not nx.is_weakly_connected(self.grafo_obj.grafo_nx):
            messagebox.showerror("Error de Grafo", "El grafo no está conectado.")
            self.fuentes, self.sumideros = [], []
            self._reset_estado(modo_manual=True) 
            self.grafo_obj.pos = nx.circular_layout(self.grafo_obj.grafo_nx)
            self.dibujar_grafo()
            self.status_label.configure(text="Error: Grafo no conectado. Se reinició la selección.")
            return
        if not self.fuentes or not self.sumideros: 
            messagebox.showerror("Error de Selección", "Debes seleccionar al menos una fuente y un sumidero.")
            return
        
        self.validar_y_corregir_direccion_flujo()
        self._bloquear_edicion()
        
        # Si hay más de una fuente o un sumidero, se abre el cuadro de diálogo para obtener las capacidades
        if len(self.fuentes) > 1 or len(self.sumideros) > 1: 
            self.abrir_dialogo_capacidades()
        else: 
            self.ejecutar_con_capacidades()

    def abrir_dialogo_capacidades(self):
        # Cuadro de diálogo para capacidades
        # Usamos CTkToplevel en lugar de tk.Toplevel
        self.dialog = ctk.CTkToplevel(self.master)
        self.dialog.title("Verificación de Capacidades")
        
        frame = ctk.CTkFrame(self.dialog)
        frame.pack(expand=True, fill="both", padx=20, pady=20)
        
        self.entry_capacidades = {}
        
        if len(self.fuentes) > 1:
            ctk.CTkLabel(frame, text="Capacidad de oferta (Fuentes):", font=ctk.CTkFont(weight="bold")).pack(pady=5, anchor='w')
            for f in self.fuentes:
                row = ctk.CTkFrame(frame, fg_color="transparent")
                row.pack(fill='x', pady=2)
                ctk.CTkLabel(row, text=f"Nodo {f}:", width=60).pack(side='left', padx=5)
                # Usamos CTkEntry en lugar de ttk.Entry
                entry = ctk.CTkEntry(row)
                entry.pack(side='right', expand=True, fill='x')
                self.entry_capacidades[f] = entry
                
        if len(self.sumideros) > 1:
            ctk.CTkLabel(frame, text="Capacidad de demanda (Sumideros):", font=ctk.CTkFont(weight="bold")).pack(pady=(15, 5), anchor='w')
            for s in self.sumideros:
                row = ctk.CTkFrame(frame, fg_color="transparent")
                row.pack(fill='x', pady=2)
                ctk.CTkLabel(row, text=f"Nodo {s}:", width=60).pack(side='left', padx=5)
                # Usamos CTkEntry en lugar de ttk.Entry
                entry = ctk.CTkEntry(row)
                entry.pack(side='right', expand=True, fill='x')
                self.entry_capacidades[s] = entry
                
        # Usamos CTkButton en lugar de ttk.Button
        ctk.CTkButton(frame, text="Confirmar y Ejecutar", command=self.ejecutar_con_capacidades).pack(pady=20)
        
        # Configuración modal
        self.dialog.transient(self.master)
        self.dialog.grab_set()
        self.master.wait_window(self.dialog)

    def ejecutar_con_capacidades(self):
        # Usa las capacidades si es necesario, y ejecuta el cálculo principal
        cap_fuentes, cap_sumideros = {}, {}
        
        # Recoger capacidades (si se usó el diálogo)
        try:
            if hasattr(self, 'dialog') and self.dialog.winfo_exists():
                for f in self.fuentes:
                    if f in self.entry_capacidades:
                        val = self.entry_capacidades[f].get()
                        # Usa float('inf') si el campo está vacío para capacidad infinita
                        cap_fuentes[f] = int(val) if val.strip() else float('inf') 
                for s in self.sumideros:
                    if s in self.entry_capacidades:
                        val = self.entry_capacidades[s].get()
                        cap_sumideros[s] = int(val) if val.strip() else float('inf')
                self.dialog.destroy()
        except ValueError: 
            messagebox.showerror("Error de Entrada", "Por favor, ingrese solo números enteros.", parent=self.dialog)
            return
            
        # Preparar Grafo Lógico y Visual
        self.status_label.configure(text="Limpiando y calculando...")
        self.grafo_obj.remover_aristas_internas(self.fuentes, self.sumideros)
        self.grafo_obj.preparar_para_multifuente(self.fuentes, self.sumideros, cap_fuentes, cap_sumideros)
        self.actualizar_layout_y_dibujar()
        
        # Ejecutar Cálculo y Mostrar Resultado
        self.pasos, flujo_maximo = self.grafo_obj.calcular_pasos_ford_fulkerson()
        self.current_step_index = 0
        self.dibujar_grafo(paso_idx=0)
        
        self.status_label.configure(text=f"¡Cálculo completo! Flujo Máximo: {flujo_maximo:.2f}. Usa las flechas.")
        self.btn_reiniciar.configure(state='normal')
        
    def reiniciar_aplicacion(self):
        """Restablece la aplicación a su estado inicial de bienvenida."""
        self.grafo_obj = None
        self._reset_estado()
        self.status_label.configure(text="Bienvenido. Genere un grafo para comenzar.")
        self.dibujar_grafo()
        
    # Método de Dibujo (Se mantiene compacto pero con espaciado mejorado)

    def dibujar_grafo(self, paso_idx=None):
        """Dibuja el grafo en el lienzo de Matplotlib, mostrando el estado actual o un paso específico."""
        self.ax.clear()

        try:
            # Obtiene los colores del tema actual
            appearance_mode = ctk.get_appearance_mode()
            if appearance_mode == "Dark":
                bg_color = "#242424"
                text_color = "#EBEBEB"
            else: # "Light" mode
                bg_color = "#EBEBEB"
                text_color = "#1F1F1F"

            legend_facecolor = bg_color
            legend_edgecolor = text_color

            node_color_default = '#007BFF' # Azul
            node_color_fuente = '#28A745'  # Verde
            node_color_sumidero = '#DC3545' # Rojo
            edge_color_default = 'gray'
            edge_color_flujo = '#007BFF'    # Azul
            edge_color_saturada = '#BD0000' # Rojo oscuro
            edge_color_camino = '#17A2B8'  # Celeste
            edge_color_camino_atras = '#FFC107' # Naranja

        except:
            # Colores de respaldo si falla
            bg_color = 'white'
            text_color = 'black'
            node_color_default = 'lightblue'
            node_color_fuente = 'lightgreen'
            node_color_sumidero = 'lightcoral'
            edge_color_default = 'gray'
            edge_color_flujo = 'blue'
            edge_color_saturada = 'darkred'
            edge_color_camino = 'red'
            edge_color_camino_atras = 'orange'
            legend_facecolor = 'white'
            legend_edgecolor = 'black'
            
        self.fig.patch.set_facecolor(bg_color)
        self.ax.clear()
        self.ax.set_facecolor(bg_color)
        
        if not self.grafo_obj or not self.grafo_obj.pos:
            self.ax.text(0.5, 0.5, "Genera un grafo para comenzar", ha='center', va='center', fontsize=12)
            self.ax.set_title("Visualizador Ford-Fulkerson", fontsize=14)
            self.ax.set_axis_off()
            self.canvas.draw()
            return
        
        paso_actual = self.pasos[paso_idx] if paso_idx is not None and paso_idx < len(self.pasos) else {}
        titulo = paso_actual.get('titulo', "Selecciona Fuentes (Verde) y Sumideros (Rojo)")
        self.ax.set_title(titulo, fontsize=14)

        camino = paso_actual.get('camino', [])
        nodos_camino_set = {n for a in camino for n in a}
        
        # Colores y Tamaños de Nodos
        node_colors, node_sizes, labels = [], [], {}
        nodos_a_dibujar = list(self.grafo_obj.grafo_nx.nodes())

        for nodo in nodos_a_dibujar:
            labels[nodo] = str(nodo)
            if nodo == self.grafo_obj.super_fuente: 
                node_colors.append('gold')
                node_sizes.append(1200)
                labels[nodo] = 'S*'
            elif nodo == self.grafo_obj.super_sumidero: 
                node_colors.append('dimgray')
                node_sizes.append(1200)
                labels[nodo] = 'T*'
            elif nodo in self.fuentes: 
                node_colors.append('lightgreen')
                node_sizes.append(1000)
            elif nodo in self.sumideros: 
                node_colors.append('lightcoral')
                node_sizes.append(1000)
            elif paso_idx is not None and nodo in nodos_camino_set: 
                node_colors.append('yellow')
                node_sizes.append(800)
            else: 
                node_colors.append('lightblue')
                node_sizes.append(800)

        nx.draw_networkx_nodes(self.grafo_obj.grafo_nx, self.grafo_obj.pos, ax=self.ax, nodelist=nodos_a_dibujar, node_color=node_colors, node_size=node_sizes)
        nx.draw_networkx_labels(self.grafo_obj.grafo_nx, self.grafo_obj.pos, ax=self.ax, labels=labels, font_size=10, font_weight='bold', font_color='black')

        edge_labels, edge_colors, edge_widths = {}, [], []

        # --- Define los colores de la leyenda ---
        legend_facecolor = ctk.ThemeManager.theme["CTkFrame"]["fg_color"][0]
        legend_edgecolor = ctk.ThemeManager.theme["CTkFrame"]["border_color"][0]
        legend_textcolor = text_color
        
        # Caso: Grafo Inicial (sin pasos)
        if paso_idx is None: 
            for u, v in self.grafo_obj.grafo_nx.edges():
                if u < self.grafo_obj.n and v < self.grafo_obj.n:
                    edge_labels[(u,v)] = f"{self.grafo_obj.capacidad[u][v]}/0"


            edge_colors = ['gray'] * self.grafo_obj.grafo_nx.number_of_edges()
            edge_widths = [1.5] * self.grafo_obj.grafo_nx.number_of_edges()
        
        # Caso: Corte Mínimo
        elif paso_actual.get('tipo') == 'corte_minimo':
            conjunto_s = paso_actual.get('conjunto_s', set())
            nodos_originales = range(self.grafo_obj.n)
            
            node_colors_corte = ['lightgreen' if i in conjunto_s else 'lightcoral' for i in nodos_originales]
            node_labels_corte = {i: f"({'S' if i in conjunto_s else 'T'})" for i in nodos_originales}
            
            # Ajustar posición de etiquetas S/T
            pos_vals = self.grafo_obj.pos.values()
            if pos_vals:
                y_coords = [y for x, y in pos_vals]; graph_height = max(y_coords) - min(y_coords)
                vertical_offset = graph_height * 0.05 if graph_height != 0 else 0.2
            else: vertical_offset = 0.2
            pos_labels = {node: (x, y - vertical_offset) for node, (x, y) in self.grafo_obj.pos.items()}
            
            # Colores del corte
            aristas_corte = set(paso_actual.get('aristas_corte', []))
            edge_colors_corte = ['red' if (u, v) in aristas_corte or (v,u) in aristas_corte else 'gray' for u, v in self.grafo_obj.grafo_nx.edges()]
            edge_widths_corte = [4 if (u, v) in aristas_corte or (v,u) in aristas_corte else 1 for u, v in self.grafo_obj.grafo_nx.edges()]
            
            # Dibujar nodos y aristas con el esquema de corte
            nx.draw_networkx_nodes(self.grafo_obj.grafo_nx, self.grafo_obj.pos, ax=self.ax, nodelist=nodos_originales, node_color=node_colors_corte, node_size=1000)
            nx.draw_networkx_labels(self.grafo_obj.grafo_nx, pos_labels, ax=self.ax, labels=node_labels_corte, font_size=9, font_weight='bold')
            nx.draw_networkx_edges(self.grafo_obj.grafo_nx, self.grafo_obj.pos, ax=self.ax, edgelist=list(self.grafo_obj.grafo_nx.edges()), edge_color=edge_colors_corte, width=edge_widths_corte, arrows=True, arrowsize=20, node_size=1000)
            
            # Leyenda del corte
            legend_elements = [plt.Line2D([0], [0], marker='o', color='w', mfc='lightgreen', label='Conjunto S'), plt.Line2D([0], [0], marker='o', color='w', mfc='lightcoral', label='Conjunto T'), plt.Line2D([0], [0], color='red', lw=4, label='Arista de Corte')]
            self.ax.legend(handles=legend_elements, loc='upper right', fontsize='small')
        
        # Caso: Pasos de Flujo (Iteraciones)
        else: 
            flujo_extendido = paso_actual.get('flujo_extendido', [])
            cap_extendida = paso_actual.get('cap_extendida', [])
            
            for u, v in self.grafo_obj.grafo_nx.edges():
                f = flujo_extendido[u][v] if u < len(flujo_extendido) and v < len(flujo_extendido[u]) else 0
                c = cap_extendida[u][v] if u < len(cap_extendida) and v < len(cap_extendida[u]) else 0
                
                cap_str = 'inf' if c == float('inf') else int(c)
                edge_labels[(u,v)] = f"{cap_str}/{int(f)}"
                
                es_camino_adelante = (u,v) in camino
                es_camino_atras = (v,u) in camino
                
                # Definición de color/ancho de arista
                if es_camino_adelante: 
                    edge_colors.append('red'); edge_widths.append(4)
                elif es_camino_atras: 
                    edge_colors.append('orange'); edge_widths.append(4)
                elif f > 0:
                    if c != float('inf') and f >= c: 
                        edge_colors.append('darkred'); edge_widths.append(3)
                    else: 
                        edge_colors.append('blue'); edge_widths.append(3)
                else: 
                    edge_colors.append('gray'); edge_widths.append(1.5)
            
            # Etiquetas de nodos (Padre, Delta)
            etiquetas_camino = paso_actual.get('etiquetas', {})
            if etiquetas_camino:
                pos_vals = self.grafo_obj.pos.values()
                if pos_vals:
                    y_coords = [y for x, y in pos_vals]; graph_height = max(y_coords) - min(y_coords)
                    vertical_offset = graph_height * 0.07 if graph_height != 0 else 0.25
                else: vertical_offset = 0.25
                
                pos_node_labels = {node: (x, y + vertical_offset) for node, (x, y) in self.grafo_obj.pos.items()}
                formatted_labels = {node: f"({parent}, {delta})" for node, (parent, delta) in etiquetas_camino.items()}
                
                nx.draw_networkx_labels(self.grafo_obj.grafo_nx, pos_node_labels, labels=formatted_labels, 
                                        font_size=9, font_color='purple', font_weight='bold', ax=self.ax)

            # Leyenda del Flujo
            legend_elements = [
                plt.Line2D([0], [0], color='red', lw=4, label='Camino de Aumento (Adelante)'),
                plt.Line2D([0], [0], color='orange', lw=4, label='Camino de Aumento (Atrás)'),
                plt.Line2D([0], [0], color='darkred', lw=3, label='Arista Saturada (Flujo = Cap.)'),
                plt.Line2D([0], [0], color='blue', lw=3, label='Arista con Flujo'),
                plt.Line2D([0], [0], color='gray', lw=1.5, label='Arista sin Flujo'),
                plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='yellow', markersize=10, label='Nodo en Camino Actual')
            ]
            self.ax.legend(handles=legend_elements, loc='upper right', fontsize='small')

        # Dibujar Aristas y Etiquetas (si no es el paso de corte)
        if paso_actual.get('tipo') != 'corte_minimo':
            nx.draw_networkx_edges(self.grafo_obj.grafo_nx, self.grafo_obj.pos, ax=self.ax, edgelist=list(self.grafo_obj.grafo_nx.edges()), edge_color=edge_colors, width=edge_widths, arrows=True, arrowsize=20, node_size=node_sizes)
            nx.draw_networkx_edge_labels(self.grafo_obj.grafo_nx, self.grafo_obj.pos, edge_labels=edge_labels, ax=self.ax, font_size=9, bbox=dict(facecolor="white", alpha=0.7, edgecolor='none', pad=0.1))
            
        self.ax.axis('off') # Ocultar ejes
        self.canvas.draw()
