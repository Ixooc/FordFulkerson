from problema import FlujoMaximo

def test_ejemplo_simple():
    """Prueba con un ejemplo simple para verificar el teorema"""
    print("=== EJEMPLO DE VERIFICACIÓN ===\n")
    
    # Crear grafo simple: 0 -> 1 -> 3, 0 -> 2 -> 3
    grafo = FlujoMaximo()
    grafo.inicializar(4)
    
    # Agregar aristas
    grafo.agregar_arista(0, 1, 10)  # 0 -> 1: capacidad 10
    grafo.agregar_arista(0, 2, 10)  # 0 -> 2: capacidad 10  
    grafo.agregar_arista(1, 3, 5)   # 1 -> 3: capacidad 5
    grafo.agregar_arista(2, 3, 15)  # 2 -> 3: capacidad 15
    grafo.agregar_arista(1, 2, 4)   # 1 -> 2: capacidad 4
    
    print("Grafo creado:")
    grafo.mostrar_grafo()
    
    # Ejecutar Ford-Fulkerson
    fuente = 0
    sumidero = 3
    flujo_maximo = grafo.ford_fulkerson(fuente, sumidero)
    
    # Mostrar resultados
    grafo.mostrar_asignacion_flujo()
    
    # Verificar el teorema
    resultado = grafo.verificar_teorema_corte_minimo(fuente, flujo_maximo)
    
    if resultado:
        print("\n🎉 ¡El algoritmo funciona correctamente!")
    else:
        print("\n⚠️  Hay un problema en la implementación.")

if __name__ == "__main__":
    test_ejemplo_simple()