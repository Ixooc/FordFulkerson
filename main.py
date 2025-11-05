import customtkinter as ctk
from gui import FordFulkersonGUI

if __name__ == "__main__":
    ctk.set_appearance_mode("Dark")  
    ctk.set_default_color_theme("dark-blue")  

    root = ctk.CTk() 
    app = FordFulkersonGUI(root)
    root.mainloop()