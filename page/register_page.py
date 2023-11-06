import tkinter as tk

class RegisterGui(tk.Tk):
    def __init__(self):
        super().__init__()
        self.new_name = tk.StringVar()
        self.new_pwd = tk.StringVar()
        self.new_pwd_confirm = tk.StringVar()
        self.btn_register = tk.Button()
        self.run()

    def run(self):
        self.wm_attributes('-topmost', 1)
        self.geometry('300x200')
        self.resizable(width=False, height=False)

        tk.Label(self, text='User name: ').place(x=10, y=10)
        tk.Entry(self, textvariable=self.new_name).place(x=130,y=0)

        tk.Label(self, text='Password: ').place(x=10, y=50)
        tk.Entry(self, textvariable=self.new_pwd, show='*').place(x=130,y=50)

        tk.Label(self, text='Confirm password: ').place(x=10, y=90)
        tk.Entry(self, textvariable=self.new_pwd_confirm, show='*').place(x=130,y=90)

        self.btn_register = tk.Button(self, text='Sign up')
        self.btn_register.place(x=180,y=120)

