import customtkinter as ctk
from gui import FordFulkersonGUI

if __name__ == "__main__":
    
    # Apariencia (System, Dark, Light)
    ctk.set_appearance_mode("System")  
    
    # Tema de color (blue, green, dark-blue)
    ctk.set_default_color_theme("blue")  

    root = ctk.CTk() 
    app = FordFulkersonGUI(root)
    root.mainloop()