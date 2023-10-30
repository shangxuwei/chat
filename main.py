from page import login_page
from page import chat_page
import tkinter as tk

if __name__ == "__main__":
    init_window = tk.Tk()
    login_portal = chat_page.ChatGui(init_window)
    init_window.mainloop()