import tkinter as tk
from tkinter import ttk
import tkinter.messagebox


class LoginGui(tk.Tk):
    def __init__(self):
        super().__init__()
        self.user = tk.StringVar()
        self.pwd = tk.StringVar()
        self.btn_login = tk.Button()
        self.btn_sign_up = tk.Button()
        self.run()

    def run(self):
        self.title("chat")  # 窗口名
        self.wm_attributes('-topmost', 0)
        screenWidth = self.winfo_screenwidth()  # 获取显示区域的宽度
        screenHeight = self.winfo_screenheight()  # 获取显示区域的高度
        width = 400  # 设定窗口宽度
        height = 300  # 设定窗口高度
        left = (screenWidth - width) / 2
        top = (screenHeight - height) / 2
        self.geometry("%dx%d+%d+%d" % (width, height, left, top))
        self.resizable(width=False,height=False)

        ttk.Label(self, text='Username:', font=('Arial', 14)).place(x=10, y=50)
        ttk.Label(self, text='Password:', font=('Arial', 14)).place(x=10, y=90)


        tk.Entry(self, textvariable=self.user, font=('Arial', 16)).place(x=110, y=50)
        tk.Entry(self, textvariable=self.pwd, font=('Arial', 16), show='*').place(x=110, y=90)


        self.btn_login = tk.Button(self, text='Login', font=('Arial', 16))
        self.btn_login.place(x=100, y=200)
        self.btn_sign_up = tk.Button(self, text='Sign up', font=('Arial', 16))
        self.btn_sign_up.place(x=200, y=200)

    def succeed(self):
        tkinter.messagebox.showinfo(title='Welcome', message='How are you? ' + self.user.get())
        self.destroy()
    
    @staticmethod
    def pwd_error():
        tkinter.messagebox.showerror(message='Error, your password is wrong, try again.')
    
    @staticmethod
    def time_out():
        tkinter.messagebox.showerror(message='Error, connect timeout, try again.')
