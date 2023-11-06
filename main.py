from method.local import client
from page import login_page,addfriend_page,register_page
import tkinter as tk
if __name__ == "__main__":
    tools = client.Client()
    page_login = login_page.LoginGui()
    def login():
        flag = tools.login(page_login.user.get(),page_login.pwd.get())
        page.login_back()
    page_login.btn_login.configure(command=lambda :login())
    page_login.mainloop()


