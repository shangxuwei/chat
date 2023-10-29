import login_page
import tkinter as tk

if __name__ == "__main__":
    init_window = tk.Tk()
    login_portal = login_page.Login_GUI(init_window)
    init_window.mainloop()