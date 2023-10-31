from page import login_page
from page import chat_page
import tkinter as tk
from page import addfriend_page
if __name__ == "__main__":
    init_window = tk.Tk()
    login_portal = addfriend_page.AddGui(init_window)
    init_window.mainloop()