import tkinter as tk
from .gui import AppUI

def main():
    root = tk.Tk()
    app = AppUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
