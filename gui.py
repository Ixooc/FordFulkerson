import tkinter as tk
from tkinter import messagebox, filedialog
from tkinter.simpledialog import askinteger
import customtkinter as ctk
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
##
import os
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
##
from logic import FlujoMaximoGrafico
from layout import layout_final_por_zonas


class FordFulkersonGUI:
    def __init__(self, master):
        self.master = master
        self.master.title("Aplicación del teorema de Flujo Máximo - Ford Fulkerson")
        
        window_width = 1200
        window_height = 750
        
        screen_width = self.master.winfo_screenwidth()
        screen_height = self.master.winfo_screenheight()
        
        center_x = int(screen_width/2 - window_width / 2)
        center_y = int(screen_height/2 - window_height / 2)
        
        self.master.geometry(f"{window_width}x{window_height}+{center_x}+{center_y}")
        
        self.grafo_obj = None                 
        self.pasos, self.current_step_index = [], 0 
        self.fuentes, self.sumideros = [], [] 
        
        self.modo_seleccion = None            
        self.primer_nodo_arista = None
        self.segundo_nodo_arista = None

        self.btn_prev_paso = None
        self.btn_next_paso = None
        self.btn_ver_flujo = None
        self.btn_ver_corte = None

        RESET_ICON_BASE64 = "R0lGODlhEAAQAPcAAHx+f4SFhnp+f4uNjpucnOnp6e3t7fT09I2QkJicnNPT0+rq6vHx8fLy8vX19fDw8Pb29vj4+ISEhI6OjpSUlJycnKWlpbe3t7+/v8HBwcjIyM/Pz9fX19ra2t/f3+np6erq6u7u7vLy8vX19ff39/j4+Pn5+f39/f///wAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACH5BAEAAIAALAAAAAAQABAAAAjUACEJHEiwoMGDCBMqXMiwocOHECNKnEixosWLGDNq3Mixo8ePIEOKHEmypMmTKFOqXMmypcuXMGPKnEmzps2bOHPq3Mmzp8+fQIMKHUq0qNGjSJMqXcq0qtWrWLNq3cq0q9evYMOKHUu2rNmzaNOqXcu2rdu3cOPKnUu3rt27ePPq3cu3r9+/gAMLHky4sOHDiBMrXsy4sePHkCNLnky5suXLmDNr3sy5s+fPoEOLHk26tOnTqFOrXs26tevXsGPLnk27tu3buHPr3s27t+/fwIMLH068uPHjyJMrX868ufPn0KNLn069uvXr2LNr3869u/fv4MOLH0++vPnz6NOrX8++vfv38OPLn0+/vv37+PPr38+/v///wAYo5IAE9kBACH5BAEAAIAALAAAAAAQABAAAAjdAB5IsKDBgwgTKlzIsKHDhxAjSpxIsaLFixgzatzIsaPHjyBDihxJsqTJkyhTqlzJsqXLlzBjypxJs6bNmzhz6tzJs6fPn0CDCh1KidQBAQAh+QQBAACAAAAsAAAAABAAEAAACP0AECRIsKDBgwgTKlzIsKHDhxAjSpxIsaLFixgzatzIsaPHjyBDihxJsqTJkyhTqlzJsqXLlzBjypxJs6bNmzhz6tzJs6fPn0CDCh1KtKjRo0iTKl3KtKnVq1izat3KtavXr2DDih1LtqzZs2jTql3Ltq3bt3Djyp1Lt67du3jz6t3Lt6/fv4ADCx5MuLDhw4gTK17MuLHjx5AjS55MubLly5gza97MubPnz6BDix5NurTp06hTq17NurXr17Bjy55Nu7bt27hz697Nu7fv38CDCx9OvLjx48iTK1/OvLnz59CjS59Ovbr169iza9/Ovbv37+DDix9Pvrz58+jTq1fPvr379/Djy59Pvz78AADs="
        
        image_data = base64.b64decode(RESET_ICON_BASE64)
        pil_image = Image.open(io.BytesIO(image_data))
        
        self.reset_icon_image = ctk.CTkImage(light_image=pil_image, dark_image=pil_image, size=(16, 16))
        
        ctk.set_default_color_theme("blue")
        ##
        script_dir = os.path.dirname(os.path.abspath(__file__))
        image_path = os.path.join(script_dir, 'almacen.png')
        try:
            self.imagen_fuente = plt.imread(image_path)
        except Exception as e:
            self.imagen_fuente = None
        super_image_path = os.path.join(script_dir, 'superalm.png')
        try:
            self.imagen_super = plt.imread(super_image_path)
        except Exception as e:
            self.imagen_super = None
        ##
        self.crear_layout_principal()

    def crear_layout_principal(self):
        
        self.master.configure(fg_color=("#EBEBEB", "#242424"))

        info_frame = ctk.CTkFrame(self.master, corner_radius=0, fg_color="transparent") 
        info_frame.pack(side=tk.TOP, fill=tk.X, padx=0, pady=0)
        
        info_frame_content = ctk.CTkFrame(info_frame, fg_color="transparent")
        info_frame_content.pack(side=tk.TOP, fill=tk.X, padx=20, pady=(15, 15))

        titulo_label = ctk.CTkLabel(info_frame_content, text="Diseño Incremental de Redes Logísticas", font=ctk.CTkFont(size=22, weight="bold"))
        titulo_label.pack()
        
        descripcion_text = (
            "Un caso concreto es la expansión de redes logísticas de paquetería, donde se debe decidir qué enlaces reforzar "
            "primero para lograr que, en cada etapa, el flujo de paquetes desde origen hasta destino sea lo más alto posible."
        )
        descripcion_label = ctk.CTkLabel(info_frame_content, text=descripcion_text, wraplength=1100, justify="center") 
        descripcion_label.pack(pady=(5, 5))

        main_app_frame = ctk.CTkFrame(self.master, fg_color="transparent")
        main_app_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=0, pady=0)

        self.sidebar_frame = ctk.CTkFrame(main_app_frame, width=280, corner_radius=0, fg_color=("#F0F0F0", "#2B2B2B"))
        self.sidebar_frame.pack(side=tk.LEFT, fill=tk.Y, padx=0, pady=0)
        self.sidebar_frame.pack_propagate(False)

        self.content_frame = ctk.CTkFrame(main_app_frame, fg_color="transparent")
        self.content_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=0, pady=0)
        
        self.simulacion_frame = ctk.CTkFrame(self.content_frame, fg_color=("#FFFFFF", "#2B2B2B")) 
        self.simulacion_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))
        
        self.crear_controles(self.sidebar_frame)
        self.crear_lienzo_grafico(self.simulacion_frame)
        self.dibujar_grafo()

    def crear_controles(self, parent):
        
        controls_container = ctk.CTkFrame(parent, corner_radius=0, fg_color="transparent")
        controls_container.pack(side=tk.TOP, fill="x", expand=False, padx=0)
        
        card_color = ("#FFFFFF", "#343638")
        
        creacion_frame = ctk.CTkFrame(controls_container, fg_color=card_color)
        creacion_frame.pack(side=tk.TOP, fill=tk.X, padx=15, pady=(15, 10))
        
        ctk.CTkLabel(creacion_frame, text="1. Creación de Grafo", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=10, pady=(5,5))

        creacion_grid = ctk.CTkFrame(creacion_frame, fg_color="transparent")
        creacion_grid.pack(fill="x", padx=10, pady=(0,10))

        ctk.CTkLabel(creacion_grid, text="Nodos:").grid(row=0, column=0, padx=5, sticky="w")
        self.n_nodos = tk.IntVar(value=8)
        
        self.slider_nodos = ctk.CTkSlider(creacion_grid, from_=8, to=16, variable=self.n_nodos, number_of_steps=8, command=lambda s: self.n_nodos.set(int(s)))
        self.slider_nodos.grid(row=0, column=1, padx=(5,0), sticky="ew")
        ctk.CTkLabel(creacion_grid, textvariable=self.n_nodos, width=25).grid(row=0, column=2, padx=(5,0), sticky="e")
        
        creacion_grid.columnconfigure(1, weight=1)
        
        self.btn_gen_aleatorio = ctk.CTkButton(creacion_grid, text="Generar Aleatorio", command=self.generar_grafo_aleatorio)
        self.btn_gen_aleatorio.grid(row=1, column=0, columnspan=3, padx=5, pady=(10,5), sticky="ew")
        self.btn_crear_manual = ctk.CTkButton(creacion_grid, text="Crear Lienzo Manual", command=self.iniciar_modo_manual)
        self.btn_crear_manual.grid(row=2, column=0, columnspan=3, padx=5, pady=5, sticky="ew")
        
        self.btn_cargar_archivo = ctk.CTkButton(creacion_grid, text="Cargar Archivo...", command=self.cargar_desde_archivo)
        self.btn_cargar_archivo.grid(row=3, column=0, columnspan=3, padx=5, pady=5, sticky="ew")
        
        tooltip_text = (
            "Formato de Archivo (.txt):\n\n"
            "Definición de Variables:\n"
            "  n = N° total de nodos\n"
            "  m = N° total de aristas\n"
            "  u = Nodo de inicio\n"
            "  v = Nodo de fin\n"
            "  c = Capacidad de la arista (u, v)\n\n"
            "Estructura del Archivo:\n"
            "Línea 1: n m\n"
            "Línea 2: u1 v1 c1\n"
            "Línea 3: u2 v2 c2\n"
            "  ...\n"
            "Línea m+1: um vm cm"
        )
        CTkToolTip(self.btn_cargar_archivo, tooltip_text)
        
        edicion_frame = ctk.CTkFrame(controls_container, fg_color=card_color)
        edicion_frame.pack(side=tk.TOP, fill=tk.X, padx=15, pady=10)
        
        ctk.CTkLabel(edicion_frame, text="2. Edición Manual", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=10, pady=(5,5))
        
        edicion_grid = ctk.CTkFrame(edicion_frame, fg_color="transparent")
        edicion_grid.pack(fill="x", padx=10, pady=(0,10))
        
        self.btn_add_arista = ctk.CTkButton(edicion_grid, text="Añadir Arista", command=self.activar_modo_add_arista, state='disabled')
        self.btn_add_arista.pack(fill=tk.X, padx=5, pady=5)
        self.btn_del_arista = ctk.CTkButton(edicion_grid, text="Eliminar Arista", command=self.activar_modo_del_arista, state='disabled')
        self.btn_del_arista.pack(fill=tk.X, padx=5, pady=(0, 5))
        
        algo_frame = ctk.CTkFrame(controls_container, fg_color=card_color)
        algo_frame.pack(side=tk.TOP, fill=tk.X, padx=15, pady=10)

        ctk.CTkLabel(algo_frame, text="3. Algoritmo", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=10, pady=(5,5))

        algo_grid = ctk.CTkFrame(algo_frame, fg_color="transparent")
        algo_grid.pack(fill="x", padx=10, pady=(0,10))
        
        self.btn_sel_fuentes = ctk.CTkButton(algo_grid, text="Sel. Fuentes", command=self.activar_modo_fuente, state='disabled')
        self.btn_sel_fuentes.pack(fill=tk.X, padx=5, pady=5)
        self.btn_sel_sumideros = ctk.CTkButton(algo_grid, text="Sel. Sumideros", command=self.activar_modo_sumidero, state='disabled')
        self.btn_sel_sumideros.pack(fill=tk.X, padx=5, pady=(0, 5))
        
        self.btn_ejecutar = ctk.CTkButton(algo_grid, text="Ejecutar Algoritmo", command=self.ejecutar_algoritmo, state='disabled', fg_color="#28A745", hover_color="#218838")
        self.btn_ejecutar.pack(fill=tk.X, padx=15, pady=(5,10))
        
        status_frame = ctk.CTkFrame(parent, height=80, corner_radius=0, border_width=1, border_color=("#CCCCCC", "#333333"))
        status_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=0, padx=0)
        status_frame.pack_propagate(False)

        self.btn_reiniciar = ctk.CTkButton(status_frame, text="Reiniciar", command=self.reiniciar_aplicacion, state='disabled', width=90, height=32, fg_color=("#E57373", "#C62828"), hover_color=("#EF5350", "#B71C1C"))
        self.btn_reiniciar.pack(side=tk.RIGHT, padx=10, pady=24)
        
        self.status_label = ctk.CTkLabel(status_frame, text="Bienvenido.", anchor="w", wraplength=140, justify="left")
        self.status_label.pack(side=tk.LEFT, padx=15, pady=10, fill="both", expand=True)


    def crear_lienzo_grafico(self, parent):
        self.fig, self.ax = plt.subplots(figsize=(12, 8))
        self.fig.subplots_adjust(top=0.95, bottom=0.02, left=0.02, right=0.98) 
        
        appearance_mode = ctk.get_appearance_mode()
        if appearance_mode == "Dark":
            bg_color = "#2B2B2B" 
        else:
            bg_color = "#FFFFFF" 

        self.fig.patch.set_facecolor(bg_color)
        self.ax.set_facecolor(bg_color)
        
        nav_frame = ctk.CTkFrame(parent, fg_color="transparent")
        nav_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=(0, 10))

        self.btn_prev_paso = ctk.CTkButton(nav_frame, text="< Anterior", command=self.paso_anterior, state='disabled', width=100)
        self.btn_prev_paso.pack(side=tk.LEFT, padx=5, pady=5)

        self.btn_next_paso = ctk.CTkButton(nav_frame, text="Siguiente >", command=self.paso_siguiente, state='disabled', width=100)
        self.btn_next_paso.pack(side=tk.LEFT, padx=5, pady=5)

        self.btn_ver_corte = ctk.CTkButton(nav_frame, text="Ver Corte Mínimo", command=self.ir_al_corte, state='disabled')
        self.btn_ver_corte.pack(side=tk.RIGHT, padx=5, pady=5)
        self.btn_ver_flujo = ctk.CTkButton(nav_frame, text="Ver Flujo Máximo", command=self.ir_al_flujo, state='disabled')
        self.btn_ver_flujo.pack(side=tk.RIGHT, padx=5, pady=5)

        self.canvas = FigureCanvasTkAgg(self.fig, master=parent)
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True, pady=10, padx=10)
        
        self.fig.canvas.mpl_connect('button_press_event', self.on_click)
        self.fig.canvas.mpl_connect('key_press_event', self.on_key_press)

    def _reset_estado(self):
        self.fuentes, self.sumideros, self.pasos, self.current_step_index = [], [], [], 0
        self.modo_seleccion, self.primer_nodo_arista, self.segundo_nodo_arista = None, None, None
        
        is_ready = self.grafo_obj is not None and self.grafo_obj.n > 0
        
        self.btn_gen_aleatorio.configure(state='normal')
        self.btn_crear_manual.configure(state='normal')
        self.btn_cargar_archivo.configure(state='normal')
        
        step_2_3_state = 'normal' if is_ready else 'disabled'
        
        self.btn_sel_fuentes.configure(state=step_2_3_state)
        self.btn_sel_sumideros.configure(state=step_2_3_state)
        self.btn_ejecutar.configure(state=step_2_3_state)
        
        self.btn_add_arista.configure(state=step_2_3_state)
        self.btn_del_arista.configure(state=step_2_3_state)
        
        self.btn_reiniciar.configure(state='normal' if is_ready else 'disabled')

        if self.btn_prev_paso:
            self.btn_prev_paso.configure(state='disabled')
            self.btn_next_paso.configure(state='disabled')

            if self.btn_ver_flujo:
                self.btn_ver_flujo.configure(state='disabled')
                self.btn_ver_corte.configure(state='disabled')

    def generar_grafo_aleatorio(self):
        self.slider_nodos.configure(from_=8, to=16)
        if not (8 <= self.n_nodos.get() <= 16):
            self.n_nodos.set(8)
            
        n = self.n_nodos.get()
        self.grafo_obj = FlujoMaximoGrafico()
        self.grafo_obj.inicializar(n)
        self.grafo_obj.crear_grafo_networkx()
        self._reset_estado()
        
        self.status_label.configure(text="Generando grafo DAG...")
        
        nodos_ordenados = list(range(n))
        random.shuffle(nodos_ordenados)
        
        for i in range(n - 1):
            u, v = nodos_ordenados[i], nodos_ordenados[i+1]
            self.grafo_obj.agregar_arista(u, v, random.randint(10, 30))
            
        num_aristas_extra = int(n * 1.5)
        pos_nodos = {nodo: i for i, nodo in enumerate(nodos_ordenados)}

        for _ in range(num_aristas_extra):
            u, v = random.sample(range(n), 2)
            
            if pos_nodos[u] < pos_nodos[v] and not any(a[0] == u and a[1] == v for a in self.grafo_obj.aristas): 
                self.grafo_obj.agregar_arista(u, v, random.randint(5, 20))
                
        self.grafo_obj.crear_grafo_networkx()
        self.actualizar_layout_y_dibujar()
        
        self.status_label.configure(text="Grafo DAG generado. Selecciona fuentes y sumideros.")

    def validar_y_corregir_direccion_flujo(self):
        if not self.grafo_obj: return

        aristas_a_revisar = list(self.grafo_obj.grafo_nx.edges())
        aristas_invertidas = 0
        n_original = self.grafo_obj.n

        for u, v in aristas_a_revisar:
            if u >= n_original or v >= n_original:
                continue

            capacidad = self.grafo_obj.capacidad[u][v]

            if v in self.fuentes and u not in self.fuentes:
                self.grafo_obj.remover_arista(u, v)
                self.grafo_obj.agregar_arista(v, u, capacidad)
                aristas_invertidas += 1

            if u in self.sumideros and v not in self.sumideros:
                self.grafo_obj.remover_arista(u, v)
                self.grafo_obj.agregar_arista(v, u, capacidad)
                aristas_invertidas += 1
        
        if aristas_invertidas > 0:
            self.show_message_dialog("Ajuste Automático", f"Se invirtieron {aristas_invertidas} arista(s) para asegurar la dirección correcta del flujo.")

    def iniciar_modo_manual(self):
        self.slider_nodos.configure(from_=8, to=16)
        if not (8 <= self.n_nodos.get() <= 16):
            self.n_nodos.set(8)
            
        n = self.n_nodos.get()
        self.grafo_obj = FlujoMaximoGrafico()
        self.grafo_obj.inicializar(n)
        self.grafo_obj.crear_grafo_networkx() 
        self._reset_estado()
        
        self.status_label.configure(text="Modo Manual: Añade o elimina aristas.")
        self.grafo_obj.pos = nx.circular_layout(self.grafo_obj.grafo_nx)
        self.dibujar_grafo()

    def cargar_desde_archivo(self):
        filepath = filedialog.askopenfilename(title="Seleccionar archivo de grafo", filetypes=[("Archivos de Texto", "*.txt"), ("Todos los archivos", "*.*")])
        if not filepath: 
            return

        try:
            self.slider_nodos.configure(from_=8, to=16)
            self.grafo_obj = FlujoMaximoGrafico()
            self.grafo_obj.cargar_desde_archivo(filepath)
            self.grafo_obj.crear_grafo_networkx()
            self._reset_estado()
            self.n_nodos.set(self.grafo_obj.n)
            
            self.actualizar_layout_y_dibujar()
            
            self.btn_sel_fuentes.configure(state='normal')
            self.btn_sel_sumideros.configure(state='normal')
            self.btn_ejecutar.configure(state='normal')
            self.status_label.configure(text=f"Grafo cargado desde {filepath.split('/')[-1]}.")
        except ValueError as e:
            self.show_message_dialog("Error de Formato de Archivo", str(e))
            self.reiniciar_aplicacion()
        except Exception as e:
            self.show_message_dialog("Error de Procesamiento", f"No se pudo procesar el archivo de grafo:\n{e}")
            self.reiniciar_aplicacion()

    def actualizar_layout_y_dibujar(self):
        if not self.grafo_obj: return
        
        cap_f = getattr(self.grafo_obj, 'cap_fuentes', {}) or {}
        cap_s = getattr(self.grafo_obj, 'cap_sumideros', {}) or {}
        
        self.grafo_obj.preparar_para_multifuente(self.fuentes, self.sumideros, cap_f, cap_s)
        
        self.grafo_obj.pos = layout_final_por_zonas(
            self.grafo_obj.grafo_nx, 
            self.fuentes, 
            self.sumideros, 
            self.grafo_obj.super_fuente, 
            self.grafo_obj.super_sumidero
        )
        self.dibujar_grafo()

    def _bloquear_edicion(self):
        self.btn_gen_aleatorio.configure(state='disabled')
        self.btn_crear_manual.configure(state='disabled')
        self.btn_add_arista.configure(state='disabled')
        self.btn_del_arista.configure(state='disabled')
        self.btn_cargar_archivo.configure(state='disabled')

        self.btn_sel_fuentes.configure(state='disabled')
        self.btn_sel_sumideros.configure(state='disabled')

        self.modo_seleccion = None
        self.primer_nodo_arista = None
        self.segundo_nodo_arista = None

    def _bloquear_edicion_grafo(self):
        self.btn_gen_aleatorio.configure(state='disabled')
        self.btn_crear_manual.configure(state='disabled')
        self.btn_add_arista.configure(state='disabled')
        self.btn_del_arista.configure(state='disabled')
        self.btn_cargar_archivo.configure(state='disabled')

        self.modo_seleccion = None
        self.primer_nodo_arista = None
        self.segundo_nodo_arista = None

    def activar_modo_fuente(self): 
        self._bloquear_edicion_grafo()
        self.modo_seleccion = 'fuente'
        self.status_label.configure(text="MODO SELECCIÓN DE FUENTES: Haz clic en los nodos.")
        
    def activar_modo_sumidero(self): 
        self._bloquear_edicion_grafo()
        self.modo_seleccion = 'sumidero'
        self.status_label.configure(text="MODO SELECCIÓN DE SUMIDEROS: Haz clic en los nodos.")
        
    def activar_modo_add_arista(self): 
        self.modo_seleccion = 'add_edge_1'
        self.primer_nodo_arista = None
        self.segundo_nodo_arista = None
        self.status_label.configure(text="AÑADIR ARISTA: Haz clic en el nodo de INICIO.")
        
    def activar_modo_del_arista(self): 
        self.modo_seleccion = 'del_edge_1'
        self.primer_nodo_arista = None
        self.segundo_nodo_arista = None
        self.status_label.configure(text="ELIMINAR ARISTA: Haz clic en el nodo de INICIO.")

    def center_dialog(self, dialog):
        dialog.update_idletasks()
        
        dialog_width = dialog.winfo_width()
        dialog_height = dialog.winfo_height()
        
        master_x = self.master.winfo_x()
        master_y = self.master.winfo_y()
        master_width = self.master.winfo_width()
        master_height = self.master.winfo_height()
        
        x = master_x + (master_width // 2) - (dialog_width // 2)
        y = master_y + (master_height // 2) - (dialog_height // 2)
        
        dialog.geometry(f"+{x}+{y}")
        dialog.transient(self.master)
        dialog.grab_set()

    def show_message_dialog(self, title, message, parent=None):
        if parent is None:
            parent = self.master
        
        dialog = ctk.CTkToplevel(parent)
        dialog.title(title)
        
        frame = ctk.CTkFrame(dialog)
        frame.pack(expand=True, fill="both", padx=20, pady=20)
        
        label = ctk.CTkLabel(frame, text=message, wraplength=300, justify="center")
        label.pack(padx=10, pady=(10, 20))
        
        ok_button = ctk.CTkButton(frame, text="Aceptar", command=dialog.destroy, width=100)
        ok_button.pack(pady=(0, 10))
        
        dialog.protocol("WM_DELETE_WINDOW", dialog.destroy)
        
        self.center_dialog(dialog)
        dialog.wait_window()

    def abrir_dialogo_capacidad_arista(self, u, v):
        dialog = ctk.CTkToplevel(self.master)
        dialog.title("Capacidad")
        
        self.dialog_result = None

        def on_add():
            val = entry.get()
            try:
                cap = int(val)
                if cap <= 0:
                    self.show_message_dialog("Error", "La capacidad debe ser un número entero positivo.", parent=dialog)
                else:
                    self.dialog_result = cap
                    dialog.destroy()
            except ValueError:
                self.show_message_dialog("Error", "Entrada inválida. Por favor, ingrese un número entero.", parent=dialog)

        def on_cancel():
            self.dialog_result = None
            dialog.destroy()
        
        dialog.protocol("WM_DELETE_WINDOW", on_cancel)

        frame = ctk.CTkFrame(dialog)
        frame.pack(expand=True, fill="both", padx=20, pady=20)
        
        label = ctk.CTkLabel(frame, text=f"Capacidad para arista {u}->{v}:")
        label.pack(padx=10, pady=(10, 5))
        
        entry = ctk.CTkEntry(frame)
        entry.pack(padx=10, pady=(0, 15), fill="x")
        entry.bind("<Return>", lambda event: on_add())
        
        button_frame = ctk.CTkFrame(frame, fg_color="transparent")
        button_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        btn_cancel = ctk.CTkButton(button_frame, text="Cancelar", command=on_cancel, fg_color=("#D9534F", "#555555"), text_color=("#FFFFFF", "#EBEBEB"), hover_color=("#C9302C", "#666666"))
        btn_cancel.pack(side="right", padx=5)

        btn_add = ctk.CTkButton(button_frame, text="Añadir", command=on_add, fg_color="#28A745", hover_color="#218838")
        btn_add.pack(side="right", padx=5)
        
        entry.focus_set()
        
        self.center_dialog(dialog)
        self.master.wait_window(dialog)
        return self.dialog_result

    def on_click(self, event):
        if not event.inaxes or not self.grafo_obj or not self.grafo_obj.pos: 
            return
            
        pos_vals = list(self.grafo_obj.pos.values())
        node_keys = list(self.grafo_obj.pos.keys())
        if not pos_vals: 
            return
            
        click_coord = (event.xdata, event.ydata)
        distances = [((c[0]-click_coord[0])**2 + (c[1]-click_coord[1])**2) for c in pos_vals]
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
            
            if self.modo_seleccion == 'add_edge_1': 
                self.modo_seleccion = 'add_edge_2'
                self.status_label.configure(text=f"AÑADIR ARISTA: Inicio en {nodo_cercano}. Clic en FIN.")
            else: 
                self.modo_seleccion = 'del_edge_2'
                self.status_label.configure(text=f"ELIMINAR ARISTA: Inicio en {nodo_cercano}. Clic en FIN.")
            self.dibujar_grafo()
                
        elif self.modo_seleccion in ['add_edge_2', 'del_edge_2']:
            if nodo_cercano >= self.grafo_obj.n: return
            
            u = self.primer_nodo_arista
            v = nodo_cercano
            
            self.segundo_nodo_arista = v
            self.dibujar_grafo()

            if u != v:
                if self.modo_seleccion == 'add_edge_2':
                    if self.grafo_obj.grafo_nx.has_edge(v, u):
                        self.show_message_dialog("Arista bidireccional no permitida", f"La arista {v}->{u} ya existe.\nNo se puede crear la arista {u}->{v}.", parent=self.master)
                    else:
                        cap = self.abrir_dialogo_capacidad_arista(u, v)
                        if cap is not None: 
                            self.grafo_obj.agregar_arista(u, v, cap)
                
                elif self.modo_seleccion == 'del_edge_2':
                    if self.grafo_obj.grafo_nx.has_edge(u,v): 
                        self.grafo_obj.remover_arista(u,v)
                    else: 
                        self.status_label.configure(text=f"ERROR: No existe arista de {u} a {v}.")

            self.primer_nodo_arista = None
            self.segundo_nodo_arista = None

            if self.modo_seleccion == 'add_edge_2':
                self.activar_modo_add_arista()
            else:
                self.activar_modo_del_arista()
                
            self.dibujar_grafo()

    def on_key_press(self, event):
        if not self.pasos: 
            return
            
        if event.key == 'right': 
            self.paso_siguiente()
        elif event.key == 'left': 
            self.paso_anterior()

    def paso_anterior(self):
        if not self.pasos: return
        self.current_step_index = max(self.current_step_index - 1, 0)
        self.dibujar_grafo(paso_idx=self.current_step_index)

    def paso_siguiente(self):
        if not self.pasos: return
        self.current_step_index = min(self.current_step_index + 1, len(self.pasos) - 1)
        self.dibujar_grafo(paso_idx=self.current_step_index)
        
    def ir_al_flujo(self):
        if not self.pasos: return
        flujo_final_idx = len(self.pasos) - 2
        if flujo_final_idx >= 0:
            self.current_step_index = flujo_final_idx
            self.dibujar_grafo(paso_idx=self.current_step_index)

    def ir_al_corte(self):
        if not self.pasos: return
        self.current_step_index = len(self.pasos) - 1
        self.dibujar_grafo(paso_idx=self.current_step_index)

    def _actualizar_botones_nav(self):
        if not self.pasos or not hasattr(self, 'btn_prev_paso'):
            return

        total_pasos = len(self.pasos)
    
        self.btn_prev_paso.configure(state='normal' if self.current_step_index > 0 else 'disabled')
        self.btn_next_paso.configure(state='normal' if self.current_step_index < (total_pasos - 1) else 'disabled')

    def ejecutar_algoritmo(self):
        if not self.grafo_obj or not self.grafo_obj.grafo_nx.nodes(): 
            self.show_message_dialog("Error", "Primero debe generar un grafo.")
            return

        nodos_originales = range(self.grafo_obj.n)
        subgrafo_original = self.grafo_obj.grafo_nx.subgraph(nodos_originales)
        
        if self.grafo_obj.n > 0 and not nx.is_weakly_connected(subgrafo_original):
            self.show_message_dialog("Error de Grafo", "El grafo no está conectado.")
            self.fuentes, self.sumideros = [], []
            self._reset_estado()
            self.grafo_obj.pos = nx.circular_layout(self.grafo_obj.grafo_nx)
            self.dibujar_grafo()
            self.status_label.configure(text="Error: Grafo no conectado. Se reinició la selección.")
            return
        if not self.fuentes or not self.sumideros: 
            self.show_message_dialog("Error de Selección", "Debes seleccionar al menos una fuente y un sumidero.")
            return
        
        self.validar_y_corregir_direccion_flujo()
        self._bloquear_edicion()
        
        if len(self.fuentes) > 1 or len(self.sumideros) > 1: 
            self.abrir_dialogo_capacidades()
        else: 
            self.ejecutar_con_capacidades()

    def abrir_dialogo_capacidades(self):
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
                entry = ctk.CTkEntry(row)
                entry.pack(side='right', expand=True, fill='x')
                self.entry_capacidades[f] = entry
                
        if len(self.sumideros) > 1:
            ctk.CTkLabel(frame, text="Capacidad de demanda (Sumideros):", font=ctk.CTkFont(weight="bold")).pack(pady=(15, 5), anchor='w')
            for s in self.sumideros:
                row = ctk.CTkFrame(frame, fg_color="transparent")
                row.pack(fill='x', pady=2)
                ctk.CTkLabel(row, text=f"Nodo {s}:", width=60).pack(side='left', padx=5)
                entry = ctk.CTkEntry(row)
                entry.pack(side='right', expand=True, fill='x')
                self.entry_capacidades[s] = entry
                
        ctk.CTkButton(frame, text="Confirmar y Ejecutar", command=self.ejecutar_con_capacidades).pack(pady=20)
        
        self.center_dialog(self.dialog)
        
        self.master.wait_window(self.dialog)

    def ejecutar_con_capacidades(self):
        cap_fuentes, cap_sumideros = {}, {}
        
        try:
            if hasattr(self, 'dialog') and self.dialog.winfo_exists():
                for f in self.fuentes:
                    if f in self.entry_capacidades:
                        val = self.entry_capacidades[f].get()
                        if val.strip():
                            cap = int(val)
                            if cap <= 0:
                                raise ValueError(f"La capacidad para la fuente {f} debe ser positiva.")
                            cap_fuentes[f] = cap
                        else:
                            cap_fuentes[f] = float('inf') 
                for s in self.sumideros:
                    if s in self.entry_capacidades:
                        val = self.entry_capacidades[s].get()
                        if val.strip():
                            cap = int(val)
                            if cap <= 0:
                                raise ValueError(f"La capacidad para el sumidero {s} debe ser positiva.")
                            cap_sumideros[s] = cap
                        else:
                            cap_sumideros[s] = float('inf')
                self.dialog.destroy()
        except ValueError as e: 
            msg = str(e)
            if "invalid literal" in msg:
                msg = "Por favor, ingrese solo números enteros."
            self.show_message_dialog("Error de Entrada", msg, parent=self.dialog if hasattr(self, 'dialog') else self.master)
            return
            
        self.status_label.configure(text="Limpiando y calculando...")
        
        aristas_eliminadas = self.grafo_obj.remover_aristas_internas(self.fuentes, self.sumideros)
        if aristas_eliminadas:
            msg = (f"Se eliminaron {len(aristas_eliminadas)} arista(s) internas "
                   "para evitar ciclos entre fuentes o sumideros:\n\n" +
                   ", ".join([f"({u}→{v})" for u, v in aristas_eliminadas]))
            self.show_message_dialog("Ajuste Automático", msg)

        self.grafo_obj.preparar_para_multifuente(self.fuentes, self.sumideros, cap_fuentes, cap_sumideros)
        self.actualizar_layout_y_dibujar()
        
        self.pasos, flujo_maximo = self.grafo_obj.calcular_pasos_ford_fulkerson()
        self.current_step_index = 0
        self.dibujar_grafo(paso_idx=0)
        
        self.status_label.configure(text=f"¡Cálculo completo! Flujo Máximo: {int(flujo_maximo)}. Usa las flechas.")
        self.btn_reiniciar.configure(state='normal')
        
        self.btn_ver_flujo.configure(state='normal')
        self.btn_ver_corte.configure(state='normal')
        
    def reiniciar_aplicacion(self):
        if self.modo_seleccion is not None:
            self.modo_seleccion = None
            self.fuentes = []
            self.sumideros = []
            self.primer_nodo_arista = None
            self.segundo_nodo_arista = None
            self._reset_estado()
            self.actualizar_layout_y_dibujar()
            self.status_label.configure(text="Selección cancelada. Elija una acción.")
        
        elif self.pasos:
            self.pasos = []
            self.current_step_index = 0
            self.fuentes = []
            self.sumideros = []
            self.primer_nodo_arista = None
            self.segundo_nodo_arista = None
            self._reset_estado()
            self.actualizar_layout_y_dibujar()
            self.status_label.configure(text="Grafo listo. Selecciona nuevas fuentes y sumideros.")

        else:
            self.grafo_obj = None
            self.primer_nodo_arista = None
            self.segundo_nodo_arista = None
            self._reset_estado()
            self.status_label.configure(text="Bienvenido. Genere un grafo para comenzar.")
            self.dibujar_grafo()
        
    def dibujar_grafo(self, paso_idx=None):
        
        try:
            appearance_mode = ctk.get_appearance_mode()
            if appearance_mode == "Dark":
                bg_color = "#2B2B2B"
                text_color = "#EBEBEB"
                legend_facecolor = "#343638"
                legend_edgecolor = "#EBEBEB"
                accent_color = "#3B8ED0" 
            else: 
                bg_color = "#FFFFFF"
                text_color = "#1F1F1F"
                legend_facecolor = "#F0F0F0"
                legend_edgecolor = "#1F1F1F"
                accent_color = "#3B8ED0"
            
            node_color_default = accent_color 
            node_color_fuente = '#28A745'  
            node_color_sumidero = '#DC3545' 
            edge_color_default = 'gray'
            edge_color_flujo = accent_color    
            edge_color_saturada = '#BD0000' 
            edge_color_camino = '#17A2B8'  
            edge_color_camino_atras = '#FFC107' 
            
        except Exception:
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
            self.ax.text(0.5, 0.5, "Genera un grafo para comenzar", ha='center', va='center', fontsize=12, color=text_color)
            self.ax.set_title("Visualizador Ford-Fulkerson", fontsize=14, color=text_color)
            self.ax.set_axis_off()
            self.canvas.draw()
            return
        
        paso_actual = self.pasos[paso_idx] if paso_idx is not None and paso_idx < len(self.pasos) else {}
        titulo = paso_actual.get('titulo', "Selecciona Fuentes (Verde) y Sumideros (Rojo)")

        if paso_idx is not None and self.pasos:
            if paso_actual.get('tipo') != 'corte_minimo':
                self.status_label.configure(text=f"Paso {paso_idx+1}/{len(self.pasos)}: {titulo}")
        elif paso_idx is None and "Bienvenido" in self.status_label.cget("text"):
             self.status_label.configure(text="Grafo listo. Selecciona fuentes y sumideros.")


        self.ax.set_title(titulo, fontsize=14, color=text_color)

        camino = paso_actual.get('camino', [])
        nodos_camino_set = {n for a in camino for n in a}
        
        node_colors, node_sizes, labels = [], [], {}
        nodos_a_dibujar = list(self.grafo_obj.grafo_nx.nodes())

        for nodo in nodos_a_dibujar:
            labels[nodo] = str(nodo)
            if nodo in self.fuentes: 
                node_colors.append(node_color_fuente); node_sizes.append(1000)
            elif nodo in self.sumideros: 
                node_colors.append(node_color_sumidero); node_sizes.append(1000)
            elif nodo == self.primer_nodo_arista or nodo == self.segundo_nodo_arista:
                node_colors.append('yellow')
                node_sizes.append(1000)
            elif paso_idx is not None and nodo in nodos_camino_set: 
                node_colors.append('yellow'); node_sizes.append(800)
            else: 
                node_colors.append(node_color_default); node_sizes.append(800)

        node_size_dict = dict(zip(nodos_a_dibujar, node_sizes))
        ## 
        nodos_normales = [n for n in nodos_a_dibujar 
                if n not in self.fuentes 
                and n not in self.sumideros
                and n != self.grafo_obj.super_fuente
                and n != self.grafo_obj.super_sumidero]

        colores_normales = []
        tamanos_normales = []
        for n in nodos_normales:
            if n == self.primer_nodo_arista or n == self.segundo_nodo_arista:
                colores_normales.append('yellow')
                tamanos_normales.append(1000)
            elif paso_idx is not None and n in nodos_camino_set:
                colores_normales.append('yellow')
                tamanos_normales.append(800)
            else:
                colores_normales.append(node_color_default)
                tamanos_normales.append(800)

        if nodos_normales:
            nx.draw_networkx_nodes(self.grafo_obj.grafo_nx, self.grafo_obj.pos,
                                nodelist=nodos_normales,
                                node_color=colores_normales,
                                node_size=tamanos_normales,
                                ax=self.ax)

        # --- Fuentes y sumideros: dibujar como imagen o círculo ---
        nodos_especiales = self.fuentes + self.sumideros
        if self.imagen_fuente is not None and nodos_especiales:
            for nodo in nodos_especiales:
                if nodo in self.grafo_obj.pos:
                    x, y = self.grafo_obj.pos[nodo]
                    imagebox = OffsetImage(self.imagen_fuente, zoom=0.09)
                    ab = AnnotationBbox(imagebox, (x, y), frameon=False, zorder=5)
                    self.ax.add_artist(ab)
        else:
            # Si no hay imagen, dibujar como círculos (comportamiento original)
            for nodo in self.fuentes:
                nx.draw_networkx_nodes(self.grafo_obj.grafo_nx, self.grafo_obj.pos,
                                    nodelist=[nodo],
                                    node_color=node_color_fuente,
                                    node_size=1000,
                                    ax=self.ax)
            for nodo in self.sumideros:
                nx.draw_networkx_nodes(self.grafo_obj.grafo_nx, self.grafo_obj.pos,
                                    nodelist=[nodo],
                                    node_color=node_color_sumidero,
                                    node_size=1000,
                                    ax=self.ax)

        # --- Super fuente y super sumidero ---
        super_nodos = []
        if self.grafo_obj.super_fuente is not None:
            super_nodos.append(self.grafo_obj.super_fuente)
            labels[self.grafo_obj.super_fuente] = 'S*'
        if self.grafo_obj.super_sumidero is not None:
            super_nodos.append(self.grafo_obj.super_sumidero)
            labels[self.grafo_obj.super_sumidero] = 'T*'

        if self.imagen_super is not None and super_nodos:
            for nodo in super_nodos:
                if nodo in self.grafo_obj.pos:
                    x, y = self.grafo_obj.pos[nodo]
                    imagebox = OffsetImage(self.imagen_super, zoom=0.09)
                    ab = AnnotationBbox(imagebox, (x, y), frameon=False, zorder=6)
                    self.ax.add_artist(ab)
            # Eliminar etiquetas S*/T* si usamos imagen
            for n in super_nodos:
                if n in labels:
                    del labels[n]
        else:
            # Fallback: dibujar como círculos
            if self.grafo_obj.super_fuente is not None:
                nx.draw_networkx_nodes(self.grafo_obj.grafo_nx, self.grafo_obj.pos,
                                    nodelist=[self.grafo_obj.super_fuente],
                                    node_color='gold', node_size=1200, ax=self.ax)
            if self.grafo_obj.super_sumidero is not None:
                nx.draw_networkx_nodes(self.grafo_obj.grafo_nx, self.grafo_obj.pos,
                                    nodelist=[self.grafo_obj.super_sumidero],
                                    node_color='dimgray', node_size=1200, ax=self.ax)
        ##
        ##
        pos_labels = self.grafo_obj.pos.copy()
        if self.imagen_fuente is not None and (self.fuentes or self.sumideros):
            # Calcular offset horizontal (ajusta según el tamaño de la imagen)
            pos_vals = list(self.grafo_obj.pos.values())
            if pos_vals:
                x_coords = [x for x, y in pos_vals]
                graph_width = max(x_coords) - min(x_coords) if x_coords else 1
                offset_h = graph_width * 0.04 if graph_width != 0 else 0.15
            else:
                offset_h = 0.15

            # Fuentes: etiqueta a la IZQUIERDA
            for nodo in self.fuentes:
                if nodo in pos_labels:
                    x, y = pos_labels[nodo]
                    pos_labels[nodo] = (x - offset_h, y)

            # Sumideros: etiqueta a la DERECHA
            for nodo in self.sumideros:
                if nodo in pos_labels:
                    x, y = pos_labels[nodo]
                    pos_labels[nodo] = (x + offset_h, y)

        ##            
        nx.draw_networkx_labels(self.grafo_obj.grafo_nx, pos_labels, ax=self.ax,
                                labels=labels, font_size=10, font_weight='bold', font_color=text_color)
        ##

        edge_labels, edge_colors, edge_widths = {}, [], []
        
        if paso_idx is None: 
            for u, v in self.grafo_obj.grafo_nx.edges():
                if u < self.grafo_obj.n and v < self.grafo_obj.n:
                    edge_labels[(u,v)] = f"{self.grafo_obj.capacidad[u][v]}/0"

            edge_colors = [edge_color_default] * self.grafo_obj.grafo_nx.number_of_edges()
            edge_widths = [1.5] * self.grafo_obj.grafo_nx.number_of_edges()
        
        elif paso_actual.get('tipo') == 'corte_minimo':
            conjunto_s = paso_actual.get('conjunto_s', set())
            
            nodelist_corte = list(range(self.grafo_obj.n))
            if self.grafo_obj.super_fuente is not None:
                nodelist_corte.append(self.grafo_obj.super_fuente)
            if self.grafo_obj.super_sumidero is not None:
                nodelist_corte.append(self.grafo_obj.super_sumidero)

            aristas_corte_data = paso_actual.get('aristas_corte', []) 
            aristas_corte_pares = set((u, v) for u, v, cap in aristas_corte_data)
            
            lista_aristas = list(self.grafo_obj.grafo_nx.edges())

            edge_colors_corte = ['red' if (u, v) in aristas_corte_pares else edge_color_default for (u, v) in lista_aristas]
            edge_widths_corte = [4 if (u, v) in aristas_corte_pares else 1 for (u, v) in lista_aristas]
            
            node_colors_corte = [node_color_fuente if i in conjunto_s else node_color_sumidero for i in nodelist_corte]
            node_sizes_corte = [node_size_dict.get(i, 800) for i in nodelist_corte]
            node_labels_corte = {i: f"({'S' if i in conjunto_s else 'T'})" for i in nodelist_corte}
            
            pos_vals = self.grafo_obj.pos.values()
            if pos_vals:
                y_coords = [y for x, y in pos_vals]; graph_height = max(y_coords) - min(y_coords)
                vertical_offset = graph_height * 0.05 if graph_height != 0 else 0.2
            else: vertical_offset = 0.2
            pos_labels = {node: (x, y - vertical_offset) for node, (x, y) in self.grafo_obj.pos.items()}
            
            nx.draw_networkx_nodes(self.grafo_obj.grafo_nx, self.grafo_obj.pos, ax=self.ax, nodelist=nodelist_corte, node_color=node_colors_corte, node_size=node_sizes_corte)
            
            nx.draw_networkx_labels(self.grafo_obj.grafo_nx, pos_labels, ax=self.ax, labels=node_labels_corte, font_size=9, font_weight='bold', font_color=text_color)
            
            edge_labels_corte = {}
            for u, v, cap in aristas_corte_data:
                if (u,v) in self.grafo_obj.grafo_nx.edges(): 
                    cap_str = 'inf' if cap == float('inf') else int(cap)
                    edge_labels_corte[(u, v)] = f"{cap_str}"
            
            nx.draw_networkx_edges(self.grafo_obj.grafo_nx, self.grafo_obj.pos, 
                                ax=self.ax, 
                                edgelist=lista_aristas,
                                edge_color=edge_colors_corte, 
                                width=edge_widths_corte, 
                                arrows=True, 
                                arrowsize=20, 
                                node_size=1000)
            
            for (u, v), label in edge_labels_corte.items():
                if u not in self.grafo_obj.pos or v not in self.grafo_obj.pos: continue
                pos_u = self.grafo_obj.pos[u]
                pos_v = self.grafo_obj.pos[v]
                length = math.sqrt((pos_v[0] - pos_u[0])**2 + (pos_v[1] - pos_u[1])**2)
                
                k = 0.3
                dynamic_label_pos = k / length if length > 0 else 0.3
                dynamic_label_pos = max(0.1, min(0.4, dynamic_label_pos)) 

                nx.draw_networkx_edge_labels(self.grafo_obj.grafo_nx, self.grafo_obj.pos, 
                                            edge_labels={(u,v): label}, 
                                            ax=self.ax, font_size=7, 
                                            bbox=dict(facecolor=bg_color, alpha=0.9, edgecolor='none', pad=0.1), 
                                            font_color='red',
                                            font_weight='bold',
                                            label_pos=dynamic_label_pos)
            
            legend_elements = [plt.Line2D([0], [0], marker='o', color='w', mfc=node_color_fuente, label='Conjunto S'), plt.Line2D([0], [0], marker='o', color='w', mfc=node_color_sumidero, label='Conjunto T'), plt.Line2D([0], [0], color='red', lw=4, label='Arista de Corte')]
            
            leg = self.ax.legend(handles=legend_elements, loc='upper right', fontsize='small', shadow=True, facecolor=legend_facecolor, edgecolor=legend_edgecolor, bbox_to_anchor=(1, 1.05))
            for text in leg.get_texts(): text.set_color(text_color) 

            flujo_max = paso_actual.get('flujo_maximo', 0)
            cap_corte = sum(cap for u, v, cap in aristas_corte_data)
            
            self.status_label.configure(text=f"Resultado: Flujo Máx. ({int(flujo_max)}) = Cap. Corte ({int(cap_corte)})")
        
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
                
                if es_camino_adelante: 
                    edge_colors.append(edge_color_camino); edge_widths.append(4)
                elif es_camino_atras: 
                    edge_colors.append(edge_color_camino_atras); edge_widths.append(4)
                elif f > 0:
                    if c != float('inf') and f >= c: 
                        edge_colors.append(edge_color_saturada); edge_widths.append(3)
                    else: 
                        edge_colors.append(edge_color_flujo); edge_widths.append(3)
                else: 
                    edge_colors.append(edge_color_default); edge_widths.append(1.5)
            
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
                                        font_size=9, font_color=text_color, font_weight='bold', ax=self.ax)

            legend_elements = [
                plt.Line2D([0], [0], color=edge_color_camino, lw=4, label='Camino de Aumento (Adelante)'),
                plt.Line2D([0], [0], color=edge_color_camino_atras, lw=4, label='Camino de Aumento (Atrás)'),
                plt.Line2D([0], [0], color=edge_color_saturada, lw=3, label='Arista Saturada (Flujo = Cap.)'),
                plt.Line2D([0], [0], color=edge_color_flujo, lw=3, label='Arista con Flujo'),
                plt.Line2D([0], [0], color=edge_color_default, lw=1.5, label='Arista sin Flujo'),
                plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='yellow', markersize=10, label='Nodo en Camino Actual')
            ]
            leg = self.ax.legend(handles=legend_elements, loc='upper right', fontsize='small', shadow=True, facecolor=legend_facecolor, edgecolor=legend_edgecolor, bbox_to_anchor=(1, 1.05))
            for text in leg.get_texts(): text.set_color(text_color) 

        if paso_actual.get('tipo') != 'corte_minimo':
            nx.draw_networkx_edges(self.grafo_obj.grafo_nx, self.grafo_obj.pos, ax=self.ax, edgelist=list(self.grafo_obj.grafo_nx.edges()), edge_color=edge_colors, width=edge_widths, arrows=True, arrowsize=20, node_size=node_sizes)

            dynamic_labels = {}
            for (u, v), label in edge_labels.items():
                if u not in self.grafo_obj.pos or v not in self.grafo_obj.pos: continue
                pos_u = self.grafo_obj.pos[u]
                pos_v = self.grafo_obj.pos[v]
                length = math.sqrt((pos_v[0] - pos_u[0])**2 + (pos_v[1] - pos_u[1])**2)
                
                k = 0.3
                dynamic_label_pos = k / length if length > 0 else 0.3
                dynamic_label_pos = max(0.1, min(0.4, dynamic_label_pos)) 
                dynamic_labels[(u,v)] = (label, dynamic_label_pos)

            for (u, v), (label, pos) in dynamic_labels.items():
                nx.draw_networkx_edge_labels(self.grafo_obj.grafo_nx, self.grafo_obj.pos, 
                                            edge_labels={(u,v): label}, 
                                            ax=self.ax, font_size=7, 
                                            bbox=dict(facecolor=bg_color, alpha=0.7, edgecolor='none', pad=0.1), 
                                            font_color=text_color, 
                                            label_pos=pos)
            
        self.ax.axis('off')
        self.canvas.draw()

        if hasattr(self, 'btn_prev_paso'): 
            self._actualizar_botones_nav()


class CTkToolTip:
    def __init__(self, widget, message, delay=500):
        self.widget = widget
        self.message = message
        self.delay = delay
        self.tooltip_window = None
        self.show_timer = None
        self.hide_timer = None

        self.widget.bind("<Enter>", self.schedule_show, add="+")
        self.widget.bind("<Leave>", self.schedule_hide, add="+")
        self.widget.bind("<Button-1>", self.hide_tooltip_click, add="+")

    def schedule_show(self, event=None):
        self.cancel_hide()
        if self.tooltip_window:
            return
        if not self.show_timer:
            self.show_timer = self.widget.after(self.delay, lambda: self.show_tooltip(event))

    def show_tooltip(self, event=None):
        if self.tooltip_window:
            return
        
        x = self.widget.winfo_rootx() + self.widget.winfo_width() + 10
        y = self.widget.winfo_rooty() 

        self.tooltip_window = ctk.CTkToplevel(self.widget)
        self.tooltip_window.wm_overrideredirect(True)
        self.tooltip_window.wm_geometry(f"+{x}+{y}")
        
        label = ctk.CTkLabel(self.tooltip_window,
                            text=self.message,
                            justify='left',
                            fg_color=("#EBEBEB", "#343638"),
                            text_color=("#1F1F1F", "#EBEBEB"),
                            corner_radius=6,
                            padx=10, pady=8,
                            font=ctk.CTkFont(size=12))
        label.pack()

        self.tooltip_window.bind("<Enter>", lambda e: self.cancel_hide())
        self.tooltip_window.bind("<Leave>", lambda e: self.schedule_hide())

    def schedule_hide(self, event=None):
        self.cancel_show()
        if not self.hide_timer:
            self.hide_timer = self.widget.after(100, self.hide_tooltip)

    def hide_tooltip(self):
        if self.tooltip_window:
            self.tooltip_window.destroy()
            self.tooltip_window = None
        self.cancel_timers()

    def hide_tooltip_click(self, event=None):
        self.hide_tooltip()

    def cancel_show(self):
        if self.show_timer:
            self.widget.after_cancel(self.show_timer)
            self.show_timer = None

    def cancel_hide(self):
        if self.hide_timer:
            self.widget.after_cancel(self.hide_timer)
            self.hide_timer = None

    def cancel_timers(self):
        self.cancel_show()
        self.cancel_hide()