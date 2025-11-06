import customtkinter as ctk
from gui import FordFulkersonGUI
import matplotlib.pyplot as plt  # <-- 1. Importa matplotlib.pyplot

if __name__ == "__main__":
    ctk.set_appearance_mode("Dark")  
    ctk.set_default_color_theme("dark-blue")  

    root = ctk.CTk() 
    app = FordFulkersonGUI(root)

    def _on_closing():
        try:
            plt.close(app.fig)
        except Exception as e:
            print(f"Error al cerrar Matplotlib: {e}") 
            
        root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", _on_closing)

    root.mainloop()