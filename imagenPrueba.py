import matplotlib.pyplot as plt
import networkx as nx
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
import os 

# --- 1. Cargar la imagen desde un archivo local ---
try:
    script_dir = os.path.dirname(os.path.abspath(__file__))
    image_path = os.path.join(script_dir, 'almacen.png')
    
    print(f"Buscando imagen en: {image_path}") 

    img = plt.imread(image_path)
    
except FileNotFoundError:
    print(f"Error: No se encontró en la ruta: {image_path}")
    img = None
except Exception as e:
    print(f"Error al cargar la imagen: {e}")
    img = None

# --- 3. Creación del Grafo y Definición de Roles ---
G = nx.Graph()
G.add_edges_from([(0, 1), (1, 2)])
pos = {0: (0, 0), 1: (1, 0), 2: (2, 0)}

# --- Define qué nodos son especiales ---
nodos_fuente = [1] 
nodos_normales = [0, 2]

# --- 4. Lógica de Dibujo ---
fig, ax = plt.subplots(figsize=(8, 4))

# Dibuja las aristas (al fondo)
nx.draw_networkx_edges(G, pos, ax=ax, width=2.0, alpha=0.7)

# --- Dibuja los NODOS NORMALES (azules) ---
nx.draw_networkx_nodes(G, pos, 
                       nodelist=nodos_normales, 
                       ax=ax, 
                       node_color="#3B8ED0", 
                       node_size=1000)

# --- Dibuja los NODOS FUENTE (verdes) ---
nx.draw_networkx_nodes(G, pos, 
                       nodelist=nodos_fuente, 
                       ax=ax, 
                       node_color="#28A745", # Color verde para fuentes
                       node_size=1000)

# --- Dibuja ETIQUETAS para nodos NORMALES (centradas) ---
labels_normales = {n: str(n) for n in nodos_normales}
nx.draw_networkx_labels(G, pos, 
                       labels=labels_normales,
                       ax=ax, 
                       font_weight='bold')

# --- 5. Superponer Imágenes y Etiquetas para nodos FUENTE ---
if img is not None:
    print("Imagen cargada. Superponiendo sobre nodos fuente...")
    
    image_size = 0.3 # Tamaño de la imagen
    label_offset = 0.3 # Qué tan abajo poner el número
    
    # --- Define dónde irán las etiquetas de las fuentes ---
    pos_labels_fuente = {}
    
    for node in nodos_fuente:
        x, y = pos[node] # Posición del nodo
        
        # 5a. Dibuja la imagen centrada
        extent = [
            x - image_size / 2, 
            x + image_size / 2, 
            y - image_size / 2, 
            y + image_size / 2  
        ]
        ax.imshow(img, extent=extent, zorder=5) 
        
        # 5b. Prepara la etiqueta para dibujarla DEBAJO
        pos_labels_fuente[node] = (x, y - label_offset)

    # 5c. Dibuja las etiquetas de las fuentes (debajo)
    labels_fuente = {n: str(n) for n in nodos_fuente}
    nx.draw_networkx_labels(G, pos_labels_fuente, 
                           labels=labels_fuente,
                           ax=ax, 
                           font_weight='bold',
                           font_color='black')
    
    print("Imágenes y etiquetas especiales dibujadas.")

else:
    # Si falla la carga de imagen, dibuja todas las etiquetas centradas
    print("No se cargó la imagen. Dibujando todas las etiquetas numéricas.")
    nx.draw_networkx_labels(G, pos, 
                           labels={n: str(n) for n in G.nodes()}, 
                           ax=ax, 
                           font_weight='bold')


ax.set_title("Ejemplo de Nodos Mixtos (Normal vs. Imagen+Label)")
ax.set_xlim(-0.5, 2.5)
# Ajustamos el límite Y para que la etiqueta de abajo no se corte
ax.set_ylim(-0.5, 0.5) 
ax.axis('off')
plt.show()