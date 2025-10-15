# Archivo encargado de la separación por zonas entre fuentes, sumideros y nodos sin ningún rol
import networkx as nx # Librería necesaria para el dibujo de grafos

# super_fuente y super_sumidero están por defecto con "None", ya que solo se usarán al tener dos o más de cada una.
def layout_final_por_zonas(grafo_nx, fuentes, sumideros, super_fuente=None, super_sumidero=None):
    # Realiza los calculos de distribucion de las zonas

    if not grafo_nx.nodes(): return {} # Grafo vacio
    pos = {} # Distribución de capas

    # Verificamos que nodos no tienen un rol
    nodos_intermedios = [n for n in grafo_nx.nodes() if n not in fuentes and n not in sumideros and n != super_fuente and n != super_sumidero]

    # posicion de fuentes
    offset_x = 1 if super_fuente is not None else 0
    y_start_fuentes = (len(fuentes) - 1) / 2.0
    for i, nodo in enumerate(sorted(fuentes)):
        pos[nodo] = (offset_x, y_start_fuentes - i)

    max_x_intermedio = 0
    if nodos_intermedios:
        subgrafo = nx.DiGraph(grafo_nx.subgraph(nodos_intermedios))
        inicios_subgrafo = {n for n in nodos_intermedios if any(grafo_nx.has_edge(f, n) for f in fuentes)}
        if not inicios_subgrafo: 
            inicios_subgrafo = {n for n, d in subgrafo.in_degree() if d == 0}
        if not inicios_subgrafo and nodos_intermedios: 
            inicios_subgrafo = {sorted(nodos_intermedios)[0]}

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
                for i, nodo in enumerate(sorted(nodos_restantes)): 
                    pos[nodo] = (max_x_intermedio, y_start_restantes - i)

        except Exception:
            max_x_intermedio = 1 + offset_x
            y_start_intermedio = (len(nodos_intermedios) - 1) / 2.0
            for i, nodo in enumerate(sorted(nodos_intermedios)): 
                pos[nodo] = (1 + offset_x, y_start_intermedio - i)

    # Posiciones de sumideros
    x_sumidero = max(max_x_intermedio, offset_x) + 1
    y_start_sumideros = (len(sumideros) - 1) / 2.0 if sumideros else 0
    for i, nodo in enumerate(sorted(sumideros)):
        pos[nodo] = (x_sumidero, y_start_sumideros - i)

    # Se coloca 
    if super_fuente is not None: 
        pos[super_fuente] = (0, 0)
    if super_sumidero is not None: 
        pos[super_sumidero] = (x_sumidero + 1, 0)

    for nodo in grafo_nx.nodes():
        if nodo not in pos: pos[nodo] = (-1, 0)
    return pos