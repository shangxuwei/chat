from page import login_page
from page import chat_page
import tkinter as tk
from page import addfriend_page
if __name__ == "__main__":
    init_window = tk.Tk()
    init_window.resizable(width=False,height=False)
    login_portal = login_page.LoginGui(init_window)
    init_window.mainloop()