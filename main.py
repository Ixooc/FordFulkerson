import tkinter as tk
from gui import FordFulkersonGUI

if __name__ == "__main__":
    root = tk.Tk() # Creamos la ventana principal
    app = FordFulkersonGUI(root) # Creamos una instancia de la aplicación
    root.mainloop()