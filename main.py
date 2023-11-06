from method.local import client
from page import login_page,addfriend_page,register_page
import tkinter as tk
if __name__ == "__main__":
    tools = client.Client()
    page_login = login_page.LoginGui()
    page_login.btn_login.configure(command=lambda :tools.login())